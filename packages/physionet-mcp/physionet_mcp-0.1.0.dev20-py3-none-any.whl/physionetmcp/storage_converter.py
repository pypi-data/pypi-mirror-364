"""
Storage Converter for PhysioNet Databases

Converts raw downloaded data (CSV, text files) into efficient storage formats
like DuckDB and Parquet for fast querying and analysis.
"""

import asyncio
import logging
import pandas as pd
import polars as pl
import duckdb
from pathlib import Path
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .database_registry import DatabaseInfo
from .config import ServerConfig, StorageFormat


logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    """Result of a database conversion operation."""

    database: str
    success: bool
    tables_created: int
    total_rows: int
    storage_size_mb: float
    conversion_time_seconds: float
    error_message: Optional[str] = None


class StorageConverter:
    """Converts PhysioNet databases to efficient storage formats."""

    def __init__(self, config: ServerConfig):
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=2)  # I/O intensive

    async def convert_database(self, db_info: DatabaseInfo) -> ConversionResult:
        """Convert a database to the configured storage format."""
        start_time = asyncio.get_event_loop().time()

        try:
            if self.config.storage_format == StorageFormat.DUCKDB:
                result = await self._convert_to_duckdb(db_info)
            elif self.config.storage_format == StorageFormat.PARQUET:
                result = await self._convert_to_parquet(db_info)
            elif self.config.storage_format == StorageFormat.BOTH:
                # Convert to both formats
                duckdb_result = await self._convert_to_duckdb(db_info)
                parquet_result = await self._convert_to_parquet(db_info)

                # Combine results
                result = ConversionResult(
                    database=db_info.name,
                    success=duckdb_result.success and parquet_result.success,
                    tables_created=duckdb_result.tables_created,
                    total_rows=duckdb_result.total_rows,
                    storage_size_mb=duckdb_result.storage_size_mb
                    + parquet_result.storage_size_mb,
                    conversion_time_seconds=0,
                    error_message=duckdb_result.error_message
                    or parquet_result.error_message,
                )
            else:
                raise ValueError(
                    f"Unknown storage format: {self.config.storage_format}"
                )

            result.conversion_time_seconds = (
                asyncio.get_event_loop().time() - start_time
            )

            if result.success:
                logger.info(
                    f"Successfully converted {db_info.name}: "
                    f"{result.tables_created} tables, {result.total_rows:,} rows, "
                    f"{result.storage_size_mb:.1f} MB"
                )

            return result

        except Exception as e:
            logger.error(f"Conversion failed for {db_info.name}: {e}")
            return ConversionResult(
                database=db_info.name,
                success=False,
                tables_created=0,
                total_rows=0,
                storage_size_mb=0,
                conversion_time_seconds=asyncio.get_event_loop().time() - start_time,
                error_message=str(e),
            )

    async def _convert_to_duckdb(self, db_info: DatabaseInfo) -> ConversionResult:
        """Convert database to DuckDB format."""
        db_path = self.config.get_database_path(db_info.name)
        duckdb_file = self.config.get_database_file(db_info.name, StorageFormat.DUCKDB)

        # Ensure parent directory exists
        duckdb_file.parent.mkdir(parents=True, exist_ok=True)

        # Run conversion in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, self._convert_to_duckdb_sync, db_info, db_path, duckdb_file
        )

    def _convert_to_duckdb_sync(
        self, db_info: DatabaseInfo, db_path: Path, duckdb_file: Path
    ) -> ConversionResult:
        """Synchronous DuckDB conversion."""
        tables_created = 0
        total_rows = 0

        # Connect to DuckDB
        con = duckdb.connect(str(duckdb_file))

        try:
            # Configure DuckDB for performance
            con.execute("SET memory_limit='4GB'")
            con.execute("SET threads TO 4")
            # Note: Compression is enabled by default in newer DuckDB versions

            # Find and convert data files
            data_files = self._discover_data_files(db_path)

            for file_path, table_name in data_files:
                try:
                    rows_imported = self._import_file_to_duckdb(
                        con, file_path, table_name
                    )
                    if rows_imported > 0:
                        tables_created += 1
                        total_rows += rows_imported
                        logger.debug(
                            f"Imported {rows_imported:,} rows to table {table_name}"
                        )

                except Exception as e:
                    logger.warning(f"Failed to import {file_path} to {table_name}: {e}")
                    continue

            # Optimize database
            con.execute("ANALYZE")
            if self.config.vacuum_schedule:
                con.execute("VACUUM")

            # Get final database size
            storage_size_mb = duckdb_file.stat().st_size / (1024 * 1024)

            return ConversionResult(
                database=db_info.name,
                success=tables_created > 0,
                tables_created=tables_created,
                total_rows=total_rows,
                storage_size_mb=storage_size_mb,
                conversion_time_seconds=0,  # Will be set by caller
            )

        except Exception as e:
            logger.error(f"DuckDB conversion error: {e}")
            return ConversionResult(
                database=db_info.name,
                success=False,
                tables_created=0,
                total_rows=0,
                storage_size_mb=0,
                conversion_time_seconds=0,
                error_message=str(e),
            )
        finally:
            con.close()

    def _import_file_to_duckdb(
        self, con: duckdb.DuckDBPyConnection, file_path: Path, table_name: str
    ) -> int:
        """Import a single file to DuckDB."""

        # Handle compressed files
        if file_path.suffix.lower() == ".gz":
            # DuckDB can read gzipped CSV directly
            sql = f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM read_csv_auto('{file_path}', header=true, ignore_errors=true)
            """
        elif file_path.suffix.lower() == ".csv":
            sql = f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM read_csv_auto('{file_path}', header=true, ignore_errors=true)
            """
        elif file_path.suffix.lower() == ".parquet":
            sql = f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM read_parquet('{file_path}')
            """
        else:
            # Try to read as CSV with flexible parsing
            sql = f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM read_csv_auto('{file_path}', header=true, ignore_errors=true, delim=',')
            """

        try:
            con.execute(sql)

            # Get row count
            result = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            return result[0] if result else 0

        except Exception as e:
            logger.warning(f"Failed to import {file_path}: {e}")
            # Try with pandas as fallback
            return self._import_with_pandas_fallback(con, file_path, table_name)

    def _import_with_pandas_fallback(
        self, con: duckdb.DuckDBPyConnection, file_path: Path, table_name: str
    ) -> int:
        """Fallback import using pandas for problematic files."""
        try:
            # Read with pandas
            if file_path.suffix.lower() == ".gz":
                df = pd.read_csv(file_path, compression="gzip", low_memory=False)
            else:
                df = pd.read_csv(file_path, low_memory=False)

            # Clean column names
            df.columns = [self._clean_column_name(col) for col in df.columns]

            # Import to DuckDB
            con.register("temp_df", df)
            con.execute(
                f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM temp_df"
            )
            con.unregister("temp_df")

            return len(df)

        except Exception as e:
            logger.error(f"Pandas fallback failed for {file_path}: {e}")
            return 0

    async def _convert_to_parquet(self, db_info: DatabaseInfo) -> ConversionResult:
        """Convert database to Parquet format."""
        db_path = self.config.get_database_path(db_info.name)
        parquet_dir = self.config.get_database_file(db_info.name, StorageFormat.PARQUET)

        # Ensure directory exists
        parquet_dir.mkdir(parents=True, exist_ok=True)

        # Run conversion in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, self._convert_to_parquet_sync, db_info, db_path, parquet_dir
        )

    def _convert_to_parquet_sync(
        self, db_info: DatabaseInfo, db_path: Path, parquet_dir: Path
    ) -> ConversionResult:
        """Synchronous Parquet conversion using Polars."""
        tables_created = 0
        total_rows = 0
        total_size = 0

        try:
            # Find and convert data files
            data_files = self._discover_data_files(db_path)

            for file_path, table_name in data_files:
                try:
                    # Read with Polars (faster than pandas for large files)
                    if file_path.suffix.lower() == ".gz":
                        df = pl.read_csv(file_path, compression="gzip")
                    else:
                        df = pl.read_csv(file_path)

                    # Clean column names
                    df = df.rename(
                        {col: self._clean_column_name(col) for col in df.columns}
                    )

                    # Write to Parquet
                    output_file = parquet_dir / f"{table_name}.parquet"
                    df.write_parquet(
                        output_file,
                        compression="snappy" if self.config.compress_data else None,
                    )

                    tables_created += 1
                    total_rows += len(df)
                    total_size += output_file.stat().st_size

                    logger.debug(f"Converted {len(df):,} rows to {output_file}")

                except Exception as e:
                    logger.warning(f"Failed to convert {file_path} to parquet: {e}")
                    continue

            return ConversionResult(
                database=db_info.name,
                success=tables_created > 0,
                tables_created=tables_created,
                total_rows=total_rows,
                storage_size_mb=total_size / (1024 * 1024),
                conversion_time_seconds=0,
            )

        except Exception as e:
            return ConversionResult(
                database=db_info.name,
                success=False,
                tables_created=0,
                total_rows=0,
                storage_size_mb=0,
                conversion_time_seconds=0,
                error_message=str(e),
            )

    def _discover_data_files(self, db_path: Path) -> List[tuple[Path, str]]:
        """Discover data files in a database directory."""
        data_files = []

        # Common data file extensions
        data_extensions = {".csv", ".csv.gz", ".tsv", ".txt", ".parquet"}

        # Skip these files/directories
        skip_patterns = {"readme", "license", "changelog", "sha256sums", "__pycache__"}

        for file_path in db_path.rglob("*"):
            if not file_path.is_file():
                continue

            # Check extension
            if file_path.suffix.lower() not in data_extensions:
                # Handle .csv.gz files
                if not (file_path.suffixes[-2:] == [".csv", ".gz"]):
                    continue

            # Skip unwanted files
            if any(skip in file_path.name.lower() for skip in skip_patterns):
                continue

            # Generate table name
            table_name = self._generate_table_name(file_path, db_path)
            data_files.append((file_path, table_name))

        # Sort by file size (process smaller files first)
        data_files.sort(key=lambda x: x[0].stat().st_size)

        return data_files

    def _generate_table_name(self, file_path: Path, db_path: Path) -> str:
        """Generate a clean table name from file path."""
        # Start with the filename without extension
        table_name = file_path.stem

        # Handle compressed files (.csv.gz -> remove .csv part)
        if table_name.endswith(".csv"):
            table_name = table_name[:-4]

        # For MIMIC/medical databases, use simple names without directory prefixes
        # This makes queries more intuitive (e.g., "patients" instead of "hosp_patients")
        clean_name = self._clean_column_name(table_name)

        return clean_name

    def _clean_column_name(self, name: str) -> str:
        """Clean a column/table name for SQL compatibility."""
        # Replace problematic characters
        clean_name = name.lower()
        clean_name = "".join(c if c.isalnum() else "_" for c in clean_name)

        # Ensure it starts with a letter
        if clean_name and clean_name[0].isdigit():
            clean_name = "col_" + clean_name

        # Handle empty names
        if not clean_name:
            clean_name = "unnamed_column"

        return clean_name

    def get_database_schema(self, db_name: str) -> Dict[str, Any]:
        """Get schema information for a converted database."""
        if self.config.storage_format == StorageFormat.DUCKDB:
            return self._get_duckdb_schema(db_name)
        elif self.config.storage_format == StorageFormat.PARQUET:
            return self._get_parquet_schema(db_name)
        else:
            return {}

    def _get_duckdb_schema(self, db_name: str) -> Dict[str, Any]:
        """Get schema from DuckDB database."""
        duckdb_file = self.config.get_database_file(db_name, StorageFormat.DUCKDB)

        if not duckdb_file.exists():
            return {}

        try:
            con = duckdb.connect(str(duckdb_file))

            # Get table list
            tables = con.execute("SHOW TABLES").fetchall()
            schema = {"tables": {}}

            for (table_name,) in tables:
                # Get table info
                columns = con.execute(f"DESCRIBE {table_name}").fetchall()
                row_count = con.execute(
                    f"SELECT COUNT(*) FROM {table_name}"
                ).fetchone()[0]

                schema["tables"][table_name] = {
                    "columns": [{"name": col[0], "type": col[1]} for col in columns],
                    "row_count": row_count,
                }

            con.close()
            return schema

        except Exception as e:
            logger.error(f"Failed to get DuckDB schema for {db_name}: {e}")
            return {}

    def _get_parquet_schema(self, db_name: str) -> Dict[str, Any]:
        """Get schema from Parquet files."""
        parquet_dir = self.config.get_database_file(db_name, StorageFormat.PARQUET)

        if not parquet_dir.exists():
            return {}

        schema = {"tables": {}}

        try:
            for parquet_file in parquet_dir.glob("*.parquet"):
                table_name = parquet_file.stem

                # Read schema using Polars
                df = pl.scan_parquet(parquet_file)
                columns = [
                    {"name": col, "type": str(dtype)}
                    for col, dtype in zip(df.columns, df.dtypes)
                ]
                row_count = df.select(pl.count()).collect().item()

                schema["tables"][table_name] = {
                    "columns": columns,
                    "row_count": row_count,
                }

            return schema

        except Exception as e:
            logger.error(f"Failed to get Parquet schema for {db_name}: {e}")
            return {}
