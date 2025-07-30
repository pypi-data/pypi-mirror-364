"""
Configuration system for PhysioNet MCP Server

Handles server configuration, database selection, authentication,
and runtime settings.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum

from .database_registry import AccessType, get_database_info


class StorageFormat(str, Enum):
    """Supported storage formats for converted databases."""

    DUCKDB = "duckdb"  # Single-file OLAP database
    PARQUET = "parquet"  # Columnar format, good for Spark/BigQuery
    BOTH = "both"  # Keep both formats


class AuthConfig(BaseModel):
    """Authentication configuration for PhysioNet access."""

    username: Optional[str] = None
    password: Optional[str] = None

    @field_validator("username", "password", mode="before")
    @classmethod
    def load_from_env(cls, v, info):
        """Load credentials from environment variables if not provided."""
        if v is None:
            env_var = f"PHYSIONET_{info.field_name.upper()}"
            return os.getenv(env_var)
        return v


class DatabaseConfig(BaseModel):
    """Configuration for a specific database."""

    name: str
    enabled: bool = True
    custom_path: Optional[Path] = None
    download_options: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def validate_database_name(cls, v):
        """Ensure the database exists in our registry."""
        db_info = get_database_info(v)
        if not db_info:
            raise ValueError(f"Unknown database: {v}")
        return v


class ServerConfig(BaseModel):
    """Main server configuration."""

    # Core settings
    data_root: Path = Field(default=Path.home() / "physionet_data")
    storage_format: StorageFormat = StorageFormat.DUCKDB

    # Database selection
    databases: List[str] = Field(default_factory=list)
    database_configs: Dict[str, DatabaseConfig] = Field(default_factory=dict)

    # Download settings
    max_concurrent_downloads: int = 3
    chunk_size: int = 8192
    verify_checksums: bool = True
    resume_downloads: bool = True

    # Storage optimization
    compress_data: bool = True
    vacuum_schedule: Optional[str] = "daily"  # cron-like: daily, weekly, etc.

    # Query settings
    query_timeout_seconds: int = 300
    max_result_rows: int = 10000
    enable_query_cache: bool = True

    # Authentication
    auth: AuthConfig = Field(default_factory=AuthConfig)

    # Logging and monitoring
    log_level: str = "INFO"
    enable_metrics: bool = False
    metrics_port: Optional[int] = None

    model_config = ConfigDict(extra="allow")

    @field_validator("data_root", mode="before")
    @classmethod
    def expand_data_root(cls, v):
        """Expand user path and create directory if needed."""
        path = Path(v).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    @field_validator("databases")
    @classmethod
    def validate_databases(cls, v):
        """Validate all requested databases exist."""
        for db_name in v:
            if not get_database_info(db_name):
                raise ValueError(f"Unknown database: {db_name}")
        return v

    def get_database_path(self, db_name: str) -> Path:
        """Get the storage path for a database."""
        # Check for custom path first
        if db_name in self.database_configs:
            custom_path = self.database_configs[db_name].custom_path
            if custom_path:
                return custom_path

        # Default path
        return self.data_root / db_name

    def get_database_file(
        self, db_name: str, format_type: StorageFormat = None
    ) -> Path:
        """Get the storage file path for a database."""
        format_type = format_type or self.storage_format
        base_path = self.get_database_path(db_name)

        if format_type == StorageFormat.DUCKDB:
            return base_path / f"{db_name}.duckdb"
        elif format_type == StorageFormat.PARQUET:
            return base_path / "parquet"
        else:
            raise ValueError(f"Unknown storage format: {format_type}")

    def is_database_downloaded(self, db_name: str) -> bool:
        """Check if a database has been downloaded."""
        db_path = self.get_database_path(db_name)
        db_info = get_database_info(db_name)

        if not db_info:
            return False

        # Check for raw download
        if db_info.expected_files:
            return all(
                (db_path / f).exists() for f in db_info.expected_files[:3]
            )  # Check first 3

        # Fallback: check if directory exists and has content
        return db_path.exists() and any(db_path.iterdir())

    def is_database_converted(self, db_name: str) -> bool:
        """Check if a database has been converted to the target storage format."""
        if self.storage_format == StorageFormat.DUCKDB:
            return self.get_database_file(db_name, StorageFormat.DUCKDB).exists()
        elif self.storage_format == StorageFormat.PARQUET:
            parquet_dir = self.get_database_file(db_name, StorageFormat.PARQUET)
            return parquet_dir.exists() and any(parquet_dir.glob("*.parquet"))
        elif self.storage_format == StorageFormat.BOTH:
            return (
                self.is_database_converted(db_name)
                and self.get_database_file(db_name, StorageFormat.PARQUET).exists()
            )
        return False

    def get_required_credentials(self) -> List[str]:
        """Get list of databases requiring credentials."""
        return [
            db_name
            for db_name in self.databases
            if get_database_info(db_name).access_type
            in [AccessType.CREDENTIALED, AccessType.PROTECTED]
        ]


def load_config_from_mcp_init(init_data: Dict[str, Any]) -> ServerConfig:
    """Load configuration from MCP initialization data."""
    # Extract our custom configuration keys
    config_data = {
        "data_root": init_data.get("dataRoot", Path.home() / "physionet_data"),
        "databases": init_data.get("db", []),
        "storage_format": init_data.get("storageFormat", "duckdb"),
        "auth": init_data.get("auth", {}),
    }

    # Add any additional configuration keys
    for key, value in init_data.items():
        if key not in ["dataRoot", "db", "storageFormat", "auth", "command", "args"]:
            config_data[key] = value

    return ServerConfig(**config_data)


def create_example_mcp_config() -> Dict[str, Any]:
    """Create an example MCP configuration for Claude Desktop."""
    return {
        "mcpServers": {
            "physionetmcp": {
                "command": "uv",
                "args": ["run", "--with", "physionetmcp", "physionetmcp", "run"],
                # Custom PhysioNet MCP configuration
                "db": ["mimic-iv", "aumc", "eicu", "mitdb", "ptb-xl"],
                "dataRoot": "~/physionet_data",
                "storageFormat": "duckdb",
                "auth": {
                    "username": "your_physionet_username",
                    "password": "your_physionet_password",
                },
                # Advanced options
                "maxConcurrentDownloads": 2,
                "queryTimeoutSeconds": 300,
                "maxResultRows": 10000,
                "enableQueryCache": True,
                "compressData": True,
                # Database-specific settings
                "databaseConfigs": {
                    "mimic-iv": {
                        "downloadOptions": {
                            "includeNotes": False,  # Skip large notes tables
                            "sampleSize": 1000,  # Download only subset for testing
                        }
                    }
                },
            }
        }
    }
