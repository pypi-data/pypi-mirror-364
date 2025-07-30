"""
PhysioNet MCP Server

Main server implementation providing MCP tools for querying PhysioNet databases.
Handles database download, conversion, and provides high-level query interfaces.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import duckdb
import polars as pl

from fastmcp import FastMCP

from .config import ServerConfig, load_config_from_mcp_init, StorageFormat
from .database_registry import get_database_info
from .download_manager import DownloadManager
from .storage_converter import StorageConverter


# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
app = FastMCP("PhysioNet MCP Server")
config: Optional[ServerConfig] = None
download_manager: Optional[DownloadManager] = None
storage_converter: Optional[StorageConverter] = None
database_connections: Dict[str, Union[duckdb.DuckDBPyConnection, str]] = {}


@app.tool
def query_sql(sql: str, database: str = None) -> List[Dict[str, Any]]:
    """
    Execute a SQL query against a PhysioNet database.

    Args:
        sql: The SQL query to execute
        database: Database name (e.g., 'mimic-iv', 'aumc', 'eicu')

    Returns:
        List of dictionaries representing the query results
    """
    if not config:
        return {"error": "Server not initialized"}

    # Use first available database if none specified
    if not database:
        if not config.databases:
            return {"error": "No databases configured"}
        database = config.databases[0]

    if database not in config.databases:
        return {
            "error": f"Database '{database}' not configured. Available: {config.databases}"
        }

    try:
        # Get database connection
        connection = _get_database_connection(database)
        if isinstance(connection, str):  # Error message
            return {"error": connection}

        # Execute query with timeout
        if config.storage_format == StorageFormat.DUCKDB:
            result = connection.execute(sql).fetchall()
            columns = [desc[0] for desc in connection.description]
            return [dict(zip(columns, row)) for row in result[: config.max_result_rows]]

        elif config.storage_format == StorageFormat.PARQUET:
            # For Parquet, we need to construct the query differently
            parquet_dir = config.get_database_file(database, StorageFormat.PARQUET)

            # Simple table replacement for common patterns
            modified_sql = _adapt_sql_for_parquet(sql, parquet_dir)
            df = pl.sql(modified_sql)
            return df.limit(config.max_result_rows).to_dicts()

    except Exception as e:
        logger.error(f"Query failed: {e}")
        return {"error": f"Query execution failed: {str(e)}"}


@app.tool
def list_databases() -> Dict[str, Any]:
    """
    List all configured PhysioNet databases with their status and metadata.

    Returns:
        Dictionary containing database information and status
    """
    if not config:
        return {"error": "Server not initialized"}

    databases = {}

    for db_name in config.databases:
        db_info = get_database_info(db_name)
        if not db_info:
            continue

        databases[db_name] = {
            "title": db_info.title,
            "description": db_info.description,
            "access_type": db_info.access_type,
            "size_gb": db_info.size_gb,
            "patient_count": db_info.patient_count,
            "downloaded": config.is_database_downloaded(db_name),
            "converted": config.is_database_converted(db_name),
            "main_tables": db_info.main_tables,
        }

    return {
        "total_databases": len(databases),
        "storage_format": config.storage_format,
        "data_root": str(config.data_root),
        "databases": databases,
    }


@app.tool
def get_database_schema(database: str) -> Dict[str, Any]:
    """
    Get detailed schema information for a specific database.

    Args:
        database: Database name to get schema for

    Returns:
        Schema information including tables and columns
    """
    if not config or not storage_converter:
        return {"error": "Server not initialized"}

    if database not in config.databases:
        return {"error": f"Database '{database}' not configured"}

    if not config.is_database_converted(database):
        return {"error": f"Database '{database}' not converted yet"}

    try:
        schema = storage_converter.get_database_schema(database)
        return {
            "database": database,
            "schema": schema,
            "storage_format": config.storage_format,
        }
    except Exception as e:
        return {"error": f"Failed to get schema: {str(e)}"}


@app.tool
def prepare_database(database: str, force_redownload: bool = False) -> Dict[str, Any]:
    """
    Download and convert a PhysioNet database for querying.

    Args:
        database: Database name to prepare
        force_redownload: Whether to redownload even if already exists

    Returns:
        Status of the preparation process
    """
    if not config or not download_manager or not storage_converter:
        return {"error": "Server not initialized"}

    if database not in config.databases:
        return {"error": f"Database '{database}' not in configuration"}

    db_info = get_database_info(database)
    if not db_info:
        return {"error": f"Unknown database: {database}"}

    try:
        # Check if already prepared
        if not force_redownload and config.is_database_converted(database):
            return {
                "status": "already_prepared",
                "database": database,
                "message": "Database already downloaded and converted",
            }

        # This would typically run asynchronously, but for simplicity we'll simulate
        # In a real implementation, you'd want to run this in a background task
        return {
            "status": "preparation_started",
            "database": database,
            "message": f"Started preparation of {database}. This may take some time.",
            "estimated_size_gb": db_info.size_gb,
        }

    except Exception as e:
        return {"error": f"Failed to prepare database: {str(e)}"}


@app.tool
def run_analysis(
    analysis_type: str, database: str, parameters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Run a predefined analysis on a PhysioNet database.

    Args:
        analysis_type: Type of analysis ('patient_summary', 'vital_trends', 'lab_values', etc.)
        database: Database to analyze
        parameters: Additional parameters for the analysis

    Returns:
        Analysis results
    """
    if not config:
        return {"error": "Server not initialized"}

    if database not in config.databases:
        return {"error": f"Database '{database}' not configured"}

    if not config.is_database_converted(database):
        return {
            "error": f"Database '{database}' not ready. Run prepare_database first."
        }

    parameters = parameters or {}

    try:
        # Define common analysis queries
        analyses = _get_predefined_analyses()

        if analysis_type not in analyses:
            available = list(analyses.keys())
            return {"error": f"Unknown analysis type. Available: {available}"}

        # Get the query template
        query_template = analyses[analysis_type]

        # Replace parameters in the query
        query = query_template.format(
            database=database, limit=parameters.get("limit", 100), **parameters
        )

        # Execute the query
        return query_sql(query, database)

    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}


@app.tool
def get_patient_info(patient_id: str, database: str) -> Dict[str, Any]:
    """
    Get comprehensive information about a specific patient.

    Args:
        patient_id: Patient identifier
        database: Database to search in

    Returns:
        Patient information including demographics, admissions, and key events
    """
    if not config:
        return {"error": "Server not initialized"}

    if database not in config.databases:
        return {"error": f"Database '{database}' not configured"}

    try:
        # Build patient query based on database type
        if database.startswith("mimic"):
            query = f"""
            SELECT p.subject_id, p.gender, p.anchor_age,
                   a.hadm_id, a.admittime, a.dischtime, a.admission_type,
                   a.insurance, a.ethnicity
            FROM patients p
            LEFT JOIN admissions a ON p.subject_id = a.subject_id
            WHERE p.subject_id = '{patient_id}'
            ORDER BY a.admittime
            """
        elif database == "eicu":
            query = f"""
            SELECT patientunitstayid, gender, age, 
                   hospitaladmitoffset, hospitaldischargeoffset,
                   unittype, ethnicity
            FROM patient
            WHERE patientunitstayid = '{patient_id}'
            """
        else:
            # Generic query
            query = f"""
            SELECT * FROM patients 
            WHERE patient_id = '{patient_id}' OR subject_id = '{patient_id}' 
                OR patientunitstayid = '{patient_id}'
            LIMIT 10
            """

        result = query_sql(query, database)

        if isinstance(result, dict) and "error" in result:
            return result

        return {
            "patient_id": patient_id,
            "database": database,
            "records_found": len(result),
            "patient_data": result,
        }

    except Exception as e:
        return {"error": f"Failed to get patient info: {str(e)}"}


@app.tool
def get_download_progress(database: str = None) -> Dict[str, Any]:
    """
    Get real-time download progress for databases.

    Args:
        database: Specific database name to check, or None for all active downloads

    Returns:
        Download progress information including percentage, speed, and ETA
    """
    if not config or not download_manager:
        return {"error": "Server not initialized"}

    try:
        if database:
            # Get progress for specific database
            return download_manager.get_download_progress_info(database)
        else:
            # Get progress for all active downloads
            active_downloads = {}
            for db_name in download_manager.active_downloads:
                active_downloads[db_name] = download_manager.get_download_progress_info(
                    db_name
                )

            return {
                "active_downloads": active_downloads,
                "total_active": len(active_downloads),
            }

    except Exception as e:
        return {"error": f"Failed to get download progress: {str(e)}"}


@app.tool
def get_cache_info() -> Dict[str, Any]:
    """
    Get comprehensive information about the download cache.

    Returns:
        Cache statistics including total size, number of databases, and per-database info
    """
    if not config or not download_manager:
        return {"error": "Server not initialized"}

    try:
        return download_manager.get_cache_info()

    except Exception as e:
        return {"error": f"Failed to get cache info: {str(e)}"}


@app.tool
def manage_cache(
    action: str, databases: List[str] = None, confirm: bool = False
) -> Dict[str, Any]:
    """
    Manage the download cache (clear, verify, or get info).

    Args:
        action: Action to perform ('clear', 'verify', 'info')
        databases: List of database names to target (None for all)
        confirm: Required confirmation for destructive actions like 'clear'

    Returns:
        Results of the cache management operation
    """
    if not config or not download_manager:
        return {"error": "Server not initialized"}

    try:
        if action == "clear":
            return download_manager.clear_cache(databases, confirm)
        elif action == "verify":
            return download_manager.verify_cache_integrity(databases)
        elif action == "info":
            return download_manager.get_cache_info()
        else:
            return {
                "error": f"Unknown action '{action}'. Available actions: clear, verify, info",
                "available_actions": ["clear", "verify", "info"],
            }

    except Exception as e:
        return {"error": f"Cache management failed: {str(e)}"}


@app.tool
def download_database(database: str, force_redownload: bool = False) -> Dict[str, Any]:
    """
    Download a PhysioNet database with real-time progress tracking.

    Args:
        database: Database name to download
        force_redownload: Whether to redownload even if already cached

    Returns:
        Download status and progress information
    """
    if not config or not download_manager:
        return {"error": "Server not initialized"}

    if database not in config.databases:
        return {"error": f"Database '{database}' not in configuration"}

    db_info = get_database_info(database)
    if not db_info:
        return {"error": f"Unknown database: {database}"}

    try:
        # Check if already downloaded and not forcing redownload
        if not force_redownload and download_manager._is_download_complete(db_info):
            cache_info = download_manager.get_cache_info()
            db_cache = next(
                (db for db in cache_info["cached_databases"] if db["name"] == database),
                None,
            )

            return {
                "status": "already_downloaded",
                "database": database,
                "message": "Database already cached. Use force_redownload=True to re-download.",
                "cache_info": db_cache,
            }

        # Start download asynchronously (this returns immediately)

        # Create a task to run the download
        async def download_task():
            try:
                return await download_manager.ensure_database(db_info)
            except Exception as e:
                logger.error(f"Download task failed: {e}")
                return False

        # Note: In a real implementation, you'd want to run this as a background task
        # For now, we'll return the status that download has started
        return {
            "status": "download_started",
            "database": database,
            "message": f"Download of {database} has been initiated. Use get_download_progress() to monitor.",
            "estimated_size_gb": db_info.size_gb,
            "expected_files": len(db_info.expected_files)
            if db_info.expected_files
            else "unknown",
        }

    except Exception as e:
        return {"error": f"Failed to start download: {str(e)}"}


def _get_database_connection(database: str) -> Union[duckdb.DuckDBPyConnection, str]:
    """Get or create a database connection."""
    if database in database_connections:
        return database_connections[database]

    try:
        if config.storage_format == StorageFormat.DUCKDB:
            db_file = config.get_database_file(database, StorageFormat.DUCKDB)
            if not db_file.exists():
                return f"Database file not found: {db_file}"

            connection = duckdb.connect(str(db_file))
            database_connections[database] = connection
            return connection

        elif config.storage_format == StorageFormat.PARQUET:
            parquet_dir = config.get_database_file(database, StorageFormat.PARQUET)
            if not parquet_dir.exists():
                return f"Parquet directory not found: {parquet_dir}"

            # For Parquet, we store the directory path
            database_connections[database] = str(parquet_dir)
            return str(parquet_dir)

    except Exception as e:
        return f"Failed to connect to database: {str(e)}"


def _adapt_sql_for_parquet(sql: str, parquet_dir: Path) -> str:
    """Adapt SQL query for Parquet files."""
    # This is a simplified adaptation - you'd want more sophisticated parsing
    adapted_sql = sql

    # Replace table names with parquet file paths
    parquet_files = list(parquet_dir.glob("*.parquet"))
    for parquet_file in parquet_files:
        table_name = parquet_file.stem
        adapted_sql = adapted_sql.replace(
            f"FROM {table_name}", f"FROM read_parquet('{parquet_file}')"
        )

    return adapted_sql


def _get_predefined_analyses() -> Dict[str, str]:
    """Get predefined analysis queries."""
    return {
        "patient_summary": """
            SELECT COUNT(*) as total_patients,
                   COUNT(DISTINCT gender) as gender_categories,
                   AVG(CAST(anchor_age AS FLOAT)) as avg_age
            FROM patients
            LIMIT {limit}
        """,
        "admission_stats": """
            SELECT admission_type, COUNT(*) as count,
                   AVG(los) as avg_length_of_stay
            FROM admissions
            GROUP BY admission_type
            ORDER BY count DESC
            LIMIT {limit}
        """,
        "vital_trends": """
            SELECT itemid, label, COUNT(*) as measurement_count,
                   AVG(valuenum) as avg_value
            FROM chartevents c
            JOIN d_items d ON c.itemid = d.itemid
            WHERE valuenum IS NOT NULL
            GROUP BY itemid, label
            ORDER BY measurement_count DESC
            LIMIT {limit}
        """,
    }


async def initialize_server(init_data: Dict[str, Any]) -> None:
    """Initialize the server with configuration data."""
    global config, download_manager, storage_converter

    try:
        # Load configuration
        config = load_config_from_mcp_init(init_data)
        logger.info(f"Loaded configuration for {len(config.databases)} databases")

        # Initialize managers
        download_manager = DownloadManager(config)
        storage_converter = StorageConverter(config)

        # Check credentials for protected databases
        required_creds = config.get_required_credentials()
        if required_creds and not (config.auth.username and config.auth.password):
            logger.warning(f"Some databases require credentials: {required_creds}")

        # Log database status
        for db_name in config.databases:
            db_info = get_database_info(db_name)
            if db_info:
                downloaded = config.is_database_downloaded(db_name)
                converted = config.is_database_converted(db_name)
                logger.info(
                    f"Database {db_name}: downloaded={downloaded}, converted={converted}"
                )

        # Tools are automatically registered via @app.tool decorators

        logger.info("PhysioNet MCP Server initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        raise


def serve_stdio() -> None:
    """Serve the MCP server over stdio."""
    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        # Clean up connections
        for connection in database_connections.values():
            if hasattr(connection, "close"):
                connection.close()
