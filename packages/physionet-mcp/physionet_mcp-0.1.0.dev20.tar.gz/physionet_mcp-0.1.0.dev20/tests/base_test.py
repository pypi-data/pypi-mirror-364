"""
Base test class for PhysioNet dataset testing.

Provides common functionality for testing dataset download, conversion, and querying.
"""

import asyncio
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from physionetmcp.config import ServerConfig, StorageFormat
from physionetmcp.database_registry import get_database_info, DatabaseInfo
from physionetmcp.download_manager import DownloadManager
from physionetmcp.storage_converter import StorageConverter
from physionetmcp.server import initialize_server, query_sql, list_databases, get_database_schema, prepare_database


class BaseDatasetTest:
    """Base class for testing PhysioNet datasets."""
    
    def __init__(self, database_name: str, test_data_root: Optional[Path] = None):
        """
        Initialize test for a specific database.
        
        Args:
            database_name: Name of the database to test
            test_data_root: Root directory for test data (uses temp dir if None)
        """
        self.database_name = database_name
        self.db_info = get_database_info(database_name)
        
        # Support both temporary and persistent cache modes
        self.use_cache = os.environ.get('PHYSIONET_USE_CACHE', 'false').lower() == 'true'
        
        # Setup test directories
        if test_data_root:
            self.test_data_root = Path(test_data_root)
        elif self.use_cache:
            # Use persistent cache directory for more realistic testing
            cache_root = Path.home() / "physionet_test_cache"
            cache_root.mkdir(exist_ok=True)
            self.test_data_root = cache_root
            self.logger = logging.getLogger(f"test_{database_name}")
            self.logger.info(f"🗄️ Using persistent cache at {self.test_data_root}")
        else:
            self.test_data_root = Path(tempfile.mkdtemp(prefix=f"physionet_test_{database_name}_"))
        
        self.test_data_root.mkdir(parents=True, exist_ok=True)
        
        # Create single config object for consistency across tests
        self.config = self._create_test_config()
        
        # Test results
        self.results = {
            'database_info': None,
            'download_success': False,
            'download_time': None,
            'conversion_success': False,
            'conversion_time': None,
            'query_success': False,
            'errors': [],
            'warnings': [],
            'cache_used': self.use_cache,
            'cache_path': str(self.test_data_root) if self.use_cache else None
        }
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for test output."""
        self.logger = logging.getLogger(f"test_{self.database_name}")
        self.logger.setLevel(logging.INFO)
        
        # Create console handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[{self.database_name.upper()}] %(levelname)s: %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _create_test_config(self, **overrides) -> ServerConfig:
        """Create test configuration for the database."""
        config_data = {
            'db': [self.database_name],
            'dataRoot': str(self.test_data_root),
            'storageFormat': 'duckdb',
            'maxResultRows': 10,
            'queryTimeoutSeconds': 30,
            'maxConcurrentDownloads': 1,
            **overrides
        }
        
        from physionetmcp.config import load_config_from_mcp_init
        return load_config_from_mcp_init(config_data)
    
    async def test_database_info(self) -> bool:
        """Test that database information is available."""
        self.logger.info("Testing database info retrieval...")
        
        try:
            if not self.db_info:
                self.results['errors'].append(f"Database {self.database_name} not found in registry")
                return False
            
            self.results['database_info'] = {
                'name': self.db_info.name,
                'title': self.db_info.title,
                'access_type': str(self.db_info.access_type),
                'size_gb': self.db_info.size_gb,
                'patient_count': self.db_info.patient_count
            }
            
            self.logger.info(f"✅ Database info: {self.db_info.title} ({self.db_info.access_type})")
            return True
            
        except Exception as e:
            self.results['errors'].append(f"Database info test failed: {str(e)}")
            self.logger.error(f"❌ Database info test failed: {e}")
            return False
    
    async def test_download(self, timeout_minutes: int = 10) -> bool:
        """Test database download."""
        self.logger.info("Testing database download...")
        
        try:
            download_manager = DownloadManager(self.config)
            
            # Check if already downloaded
            if self.config.is_database_downloaded(self.database_name):
                self.logger.info("✅ Database already downloaded")
                self.results['download_success'] = True
                return True
            
            # Time the download
            start_time = time.time()
            
            # Start download with timeout
            success = await asyncio.wait_for(
                download_manager.ensure_database(self.db_info),
                timeout=timeout_minutes * 60
            )
            
            end_time = time.time()
            self.results['download_time'] = end_time - start_time
            
            if success:
                self.logger.info(f"✅ Download completed in {self.results['download_time']:.1f}s")
                self.results['download_success'] = True
                return True
            else:
                self.results['errors'].append("Download returned False")
                self.logger.error("❌ Download failed")
                return False
                
        except asyncio.TimeoutError:
            self.results['errors'].append(f"Download timed out after {timeout_minutes} minutes")
            self.logger.error(f"❌ Download timed out after {timeout_minutes} minutes")
            return False
        except Exception as e:
            self.results['errors'].append(f"Download test failed: {str(e)}")
            self.logger.error(f"❌ Download test failed: {e}")
            return False
    
    async def test_conversion(self, timeout_minutes: int = 5) -> bool:
        """Test database conversion to storage format."""
        self.logger.info("Testing database conversion...")
        
        try:
            storage_converter = StorageConverter(self.config)
            
            # Check if already converted
            if self.config.is_database_converted(self.database_name):
                self.logger.info("✅ Database already converted")
                self.results['conversion_success'] = True
                return True
            
            # Ensure download first
            if not self.config.is_database_downloaded(self.database_name):
                self.results['errors'].append("Cannot convert: database not downloaded")
                return False
            
            # Time the conversion
            start_time = time.time()
            
            # Start conversion with timeout
            conversion_result = await asyncio.wait_for(
                storage_converter.convert_database(self.db_info),
                timeout=timeout_minutes * 60
            )
            
            end_time = time.time()
            self.results['conversion_time'] = end_time - start_time
            
            if conversion_result.success:
                self.logger.info(f"✅ Conversion completed in {self.results['conversion_time']:.1f}s")
                self.logger.info(f"✅ Tables: {conversion_result.tables_created} tables created")
                self.results['conversion_success'] = True
                return True
            else:
                self.results['errors'].append("Conversion returned failure")
                self.logger.error("❌ Conversion failed")
                return False
                
        except asyncio.TimeoutError:
            self.results['errors'].append(f"Conversion timed out after {timeout_minutes} minutes")
            self.logger.error(f"❌ Conversion timed out after {timeout_minutes} minutes")
            return False
        except Exception as e:
            self.results['errors'].append(f"Conversion test failed: {str(e)}")
            self.logger.error(f"❌ Conversion test failed: {e}")
            return False
    
    async def test_mcp_tools(self) -> bool:
        """Test MCP tools functionality."""
        self.logger.info("Testing MCP tools...")
        
        try:
            # Initialize MCP server using existing config
            config_data = {
                'db': [self.database_name],
                'dataRoot': str(self.test_data_root),
                'storageFormat': 'duckdb',
                'maxResultRows': 5
            }
            
            await initialize_server(config_data)
            self.logger.info("✅ MCP server initialized")
            
            # Test list_databases (using .fn() to access underlying function)
            db_list = list_databases.fn()
            if isinstance(db_list, dict) and 'databases' in db_list:
                self.logger.info(f"✅ list_databases: {len(db_list['databases'])} databases")
            else:
                self.results['errors'].append("list_databases failed")
                return False
            
            # Test get_database_schema (may fail if not converted, which is OK)
            schema_result = get_database_schema.fn(self.database_name)
            if isinstance(schema_result, dict):
                if 'error' in schema_result:
                    self.logger.info(f"⚠️  get_database_schema: {schema_result['error']}")
                    self.results['warnings'].append(f"Schema not available: {schema_result['error']}")
                else:
                    self.logger.info("✅ get_database_schema: Success")
            
            # Test prepare_database
            prep_result = prepare_database.fn(self.database_name)
            if isinstance(prep_result, dict):
                if 'error' in prep_result:
                    self.logger.info(f"⚠️  prepare_database: {prep_result['error']}")
                else:
                    self.logger.info(f"✅ prepare_database: {prep_result.get('status', 'Success')}")
            
            self.results['query_success'] = True
            return True
            
        except Exception as e:
            self.results['errors'].append(f"MCP tools test failed: {str(e)}")
            self.logger.error(f"❌ MCP tools test failed: {e}")
            return False
    
    async def test_basic_queries(self) -> bool:
        """Test basic SQL queries if data is available."""
        self.logger.info("Testing basic queries...")
        
        try:
            # Only test if database is converted
            if not self.config.is_database_converted(self.database_name):
                self.logger.info("⚠️  Skipping query tests - database not converted")
                return True
            
            # Test a simple query
            test_queries = self._get_test_queries()
            
            for query_name, query in test_queries.items():
                self.logger.info(f"Testing query: {query_name}")
                result = query_sql.fn(query, self.database_name)
                
                if isinstance(result, dict) and 'error' in result:
                    self.logger.warning(f"⚠️  Query '{query_name}' failed: {result['error']}")
                    self.results['warnings'].append(f"Query '{query_name}' failed: {result['error']}")
                elif isinstance(result, list):
                    self.logger.info(f"✅ Query '{query_name}': {len(result)} rows")
                else:
                    self.logger.warning(f"⚠️  Query '{query_name}': unexpected result type")
            
            return True
            
        except Exception as e:
            self.results['errors'].append(f"Query test failed: {str(e)}")
            self.logger.error(f"❌ Query test failed: {e}")
            return False
    
    def _get_test_queries(self) -> Dict[str, str]:
        """Get database-specific test queries. Override in subclasses."""
        return {
            "table_count": "SELECT name FROM sqlite_master WHERE type='table'",
            "row_count": "SELECT COUNT(*) as total FROM (SELECT 1 LIMIT 1)"
        }
    
    async def run_full_test(self, cleanup: bool = True) -> Dict[str, Any]:
        """Run complete test suite for the database."""
        self.logger.info(f"🧪 Starting full test suite for {self.database_name}")
        
        try:
            # Test database info
            await self.test_database_info()
            
            # Test download
            await self.test_download()
            
            # Test conversion (only if download succeeded)
            if self.results['download_success']:
                await self.test_conversion()
            
            # Test MCP tools
            await self.test_mcp_tools()
            
            # Test basic queries (only if conversion succeeded)
            if self.results['conversion_success']:
                await self.test_basic_queries()
            
            # Calculate overall success
            critical_tests = ['download_success', 'conversion_success', 'query_success']
            success_count = sum(1 for test in critical_tests if self.results.get(test, False))
            self.results['overall_success'] = success_count >= 2  # At least 2/3 critical tests
            
            # Log summary
            self._log_summary()
            
        except Exception as e:
            self.results['errors'].append(f"Test suite failed: {str(e)}")
            self.logger.error(f"❌ Test suite failed: {e}")
            self.results['overall_success'] = False
        
        finally:
            # Cleanup if requested
            if cleanup and self.test_data_root.exists():
                try:
                    shutil.rmtree(self.test_data_root)
                    self.logger.info("🧹 Cleaned up test data")
                except Exception as e:
                    self.logger.warning(f"⚠️  Cleanup failed: {e}")
        
        return self.results
    
    def _log_summary(self):
        """Log test summary."""
        self.logger.info("\n" + "="*50)
        self.logger.info(f"TEST SUMMARY FOR {self.database_name.upper()}")
        self.logger.info("="*50)
        
        if self.results.get('database_info'):
            info = self.results['database_info']
            self.logger.info(f"Database: {info['title']}")
            self.logger.info(f"Access: {info['access_type']}")
            self.logger.info(f"Size: {info['size_gb']} GB")
        
        self.logger.info(f"Download: {'✅ SUCCESS' if self.results['download_success'] else '❌ FAILED'}")
        if self.results.get('download_time'):
            self.logger.info(f"  Time: {self.results['download_time']:.1f}s")
        
        self.logger.info(f"Conversion: {'✅ SUCCESS' if self.results['conversion_success'] else '❌ FAILED'}")
        if self.results.get('conversion_time'):
            self.logger.info(f"  Time: {self.results['conversion_time']:.1f}s")
        
        self.logger.info(f"MCP Tools: {'✅ SUCCESS' if self.results['query_success'] else '❌ FAILED'}")
        
        if self.results['errors']:
            self.logger.info(f"\n❌ ERRORS ({len(self.results['errors'])}):")
            for error in self.results['errors']:
                self.logger.info(f"  - {error}")
        
        if self.results['warnings']:
            self.logger.info(f"\n⚠️  WARNINGS ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                self.logger.info(f"  - {warning}")
        
        overall = "✅ OVERALL SUCCESS" if self.results.get('overall_success') else "❌ OVERALL FAILED"
        self.logger.info(f"\n{overall}")
        self.logger.info("="*50) 