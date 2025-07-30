"""
CLI interface for PhysioNet MCP Server

Provides command-line interface for running the server and managing databases.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .server import initialize_server, serve_stdio
from .config import ServerConfig, create_example_mcp_config
from .database_registry import DATABASE_REGISTRY, AccessType

app = typer.Typer(help="PhysioNet MCP Server - Access physiological databases via MCP")
console = Console()


@app.command()
def run(
    init_json: str = typer.Argument(
        ..., help="MCP initialization JSON (passed automatically by Claude Desktop)"
    ),
) -> None:
    """
    Run the PhysioNet MCP server.

    This command is typically called by Claude Desktop via the MCP protocol.
    The init_json parameter contains configuration data from your MCP settings.
    """
    try:
        # Parse initialization data
        init_data = json.loads(init_json)

        # Initialize server
        asyncio.run(initialize_server(init_data))

        # Start serving
        console.print("[green]Starting PhysioNet MCP Server...[/green]")
        serve_stdio()

    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON in init_json: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error starting server: {e}[/red]")
        sys.exit(1)


@app.command()
def init_config(
    output_file: Path = typer.Option(
        Path("claude_config.json"),
        "--output",
        "-o",
        help="Output file for the example configuration",
    ),
) -> None:
    """
    Generate an example MCP configuration file for Claude Desktop.
    """
    try:
        config = create_example_mcp_config()

        with open(output_file, "w") as f:
            json.dump(config, f, indent=2)

        console.print(f"[green]Example configuration written to {output_file}[/green]")
        console.print("\nTo use this configuration:")
        console.print("1. Copy the contents to your Claude Desktop MCP settings")
        console.print("2. Update the paths and credentials as needed")
        console.print("3. Restart Claude Desktop")

    except Exception as e:
        console.print(f"[red]Error creating config: {e}[/red]")
        sys.exit(1)


@app.command()
def list_dbs(
    access_type: Optional[str] = typer.Option(
        None,
        "--access-type",
        "-a",
        help="Filter by access type (open, credentialed, protected)",
    ),
    max_size: Optional[float] = typer.Option(
        None, "--max-size", "-s", help="Maximum database size in GB"
    ),
) -> None:
    """
    List available PhysioNet databases in the registry.
    """
    try:
        databases = list(DATABASE_REGISTRY.values())

        # Apply filters
        if access_type:
            try:
                access_filter = AccessType(access_type.lower())
                databases = [db for db in databases if db.access_type == access_filter]
            except ValueError:
                console.print(
                    "[red]Invalid access type. Use: open, credentialed, or protected[/red]"
                )
                return

        if max_size:
            databases = [
                db for db in databases if db.size_gb and db.size_gb <= max_size
            ]

        # Create table
        table = Table(title="PhysioNet Databases")
        table.add_column("Name", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Access", style="yellow")
        table.add_column("Size (GB)", justify="right", style="magenta")
        table.add_column("Patients", justify="right", style="blue")
        table.add_column("Method", style="dim")

        for db in databases:
            table.add_row(
                db.name,
                db.title[:50] + "..." if len(db.title) > 50 else db.title,
                db.access_type.value,
                f"{db.size_gb:.1f}" if db.size_gb else "Unknown",
                f"{db.patient_count:,}" if db.patient_count else "Unknown",
                db.download_method.value,
            )

        console.print(table)
        console.print(f"\nShowing {len(databases)} databases")

    except Exception as e:
        console.print(f"[red]Error listing databases: {e}[/red]")
        sys.exit(1)


@app.command()
def download(
    database: str = typer.Argument(..., help="Database name to download"),
    data_root: Path = typer.Option(
        Path.home() / "physionet_data",
        "--data-root",
        "-d",
        help="Root directory for storing databases",
    ),
    username: Optional[str] = typer.Option(
        None, "--username", "-u", help="PhysioNet username (for credentialed databases)"
    ),
    password: Optional[str] = typer.Option(
        None, "--password", "-p", help="PhysioNet password (for credentialed databases)"
    ),
) -> None:
    """
    Download a specific PhysioNet database.

    This is a standalone command for downloading databases outside of the MCP server.
    """
    from .download_manager import DownloadManager
    from .database_registry import get_database_info
    from .config import AuthConfig

    try:
        # Get database info
        db_info = get_database_info(database)
        if not db_info:
            console.print(f"[red]Unknown database: {database}[/red]")
            console.print("Use 'physionetmcp list-dbs' to see available databases")
            return

        # Create minimal config
        config = ServerConfig(
            data_root=data_root,
            databases=[database],
            auth=AuthConfig(username=username, password=password),
        )

        # Initialize download manager
        download_manager = DownloadManager(config)

        console.print(f"[cyan]Downloading {db_info.title}...[/cyan]")
        console.print(f"Size: ~{db_info.size_gb} GB")
        console.print(f"Access: {db_info.access_type.value}")

        # Download
        result = asyncio.run(download_manager.ensure_database(db_info))

        if result:
            console.print(f"[green]Successfully downloaded {database}[/green]")
            console.print(f"Location: {config.get_database_path(database)}")
        else:
            console.print(f"[red]Failed to download {database}[/red]")

    except Exception as e:
        console.print(f"[red]Download error: {e}[/red]")
        sys.exit(1)


@app.command()
def convert(
    database: str = typer.Argument(..., help="Database name to convert"),
    data_root: Path = typer.Option(
        Path.home() / "physionet_data",
        "--data-root",
        "-d",
        help="Root directory containing the database",
    ),
    format_type: str = typer.Option(
        "duckdb", "--format", "-f", help="Output format (duckdb, parquet, both)"
    ),
) -> None:
    """
    Convert a downloaded database to an efficient storage format.
    """
    from .storage_converter import StorageConverter
    from .database_registry import get_database_info
    from .config import StorageFormat

    try:
        # Get database info
        db_info = get_database_info(database)
        if not db_info:
            console.print(f"[red]Unknown database: {database}[/red]")
            return

        # Validate format
        try:
            storage_format = StorageFormat(format_type.lower())
        except ValueError:
            console.print("[red]Invalid format. Use: duckdb, parquet, or both[/red]")
            return

        # Create config
        config = ServerConfig(
            data_root=data_root, databases=[database], storage_format=storage_format
        )

        # Check if database exists
        if not config.is_database_downloaded(database):
            console.print(f"[red]Database {database} not found in {data_root}[/red]")
            console.print("Download it first using the 'download' command")
            return

        # Initialize converter
        storage_converter = StorageConverter(config)

        console.print(f"[cyan]Converting {db_info.title} to {format_type}...[/cyan]")

        # Convert
        result = asyncio.run(storage_converter.convert_database(db_info))

        if result.success:
            console.print(f"[green]Successfully converted {database}[/green]")
            console.print(f"Tables created: {result.tables_created}")
            console.print(f"Total rows: {result.total_rows:,}")
            console.print(f"Storage size: {result.storage_size_mb:.1f} MB")
            console.print(
                f"Conversion time: {result.conversion_time_seconds:.1f} seconds"
            )
        else:
            console.print(f"[red]Conversion failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]Conversion error: {e}[/red]")
        sys.exit(1)


@app.command()
def test_query(
    database: str = typer.Argument(..., help="Database to query"),
    sql: str = typer.Argument(..., help="SQL query to execute"),
    data_root: Path = typer.Option(
        Path.home() / "physionet_data",
        "--data-root",
        "-d",
        help="Root directory containing the database",
    ),
) -> None:
    """
    Test a SQL query against a converted database.
    """
    import duckdb
    from .config import StorageFormat

    try:
        config = ServerConfig(
            data_root=data_root,
            databases=[database],
            storage_format=StorageFormat.DUCKDB,
        )

        db_file = config.get_database_file(database, StorageFormat.DUCKDB)

        if not db_file.exists():
            console.print(f"[red]Database file not found: {db_file}[/red]")
            console.print("Convert the database first using the 'convert' command")
            return

        # Execute query
        con = duckdb.connect(str(db_file))

        console.print(f"[cyan]Executing query on {database}...[/cyan]")
        console.print(f"Query: {sql}")

        result = con.execute(sql).fetchall()
        columns = [desc[0] for desc in con.description]

        # Display results in table
        if result:
            table = Table(title=f"Query Results ({len(result)} rows)")
            for col in columns:
                table.add_column(col)

            for row in result[:20]:  # Show first 20 rows
                table.add_row(*[str(val) for val in row])

            console.print(table)

            if len(result) > 20:
                console.print(f"[dim]... and {len(result) - 20} more rows[/dim]")
        else:
            console.print("[yellow]No results returned[/yellow]")

        con.close()

    except Exception as e:
        console.print(f"[red]Query error: {e}[/red]")
        sys.exit(1)


@app.command()
def info(
    database: str = typer.Argument(..., help="Database to get info about"),
) -> None:
    """
    Get detailed information about a specific database.
    """
    from .database_registry import get_database_info

    try:
        db_info = get_database_info(database)
        if not db_info:
            console.print(f"[red]Unknown database: {database}[/red]")
            return

        console.print(f"[bold cyan]{db_info.title}[/bold cyan]")
        console.print(f"Name: {db_info.name}")
        console.print(f"Description: {db_info.description}")
        console.print(f"Access Type: {db_info.access_type.value}")
        console.print(f"Download Method: {db_info.download_method.value}")

        if db_info.size_gb:
            console.print(f"Size: ~{db_info.size_gb} GB")
        if db_info.patient_count:
            console.print(f"Patients: {db_info.patient_count:,}")
        if db_info.record_count:
            console.print(f"Records: {db_info.record_count:,}")

        if db_info.main_tables:
            console.print(f"Main Tables: {', '.join(db_info.main_tables)}")

        if db_info.base_url:
            console.print(f"URL: {db_info.base_url}")
        elif db_info.s3_bucket:
            console.print(f"S3 Bucket: s3://physionet-open/{db_info.s3_bucket}")
        elif db_info.wfdb_database:
            console.print(f"WFDB Database: {db_info.wfdb_database}")

    except Exception as e:
        console.print(f"[red]Error getting info: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    app()
