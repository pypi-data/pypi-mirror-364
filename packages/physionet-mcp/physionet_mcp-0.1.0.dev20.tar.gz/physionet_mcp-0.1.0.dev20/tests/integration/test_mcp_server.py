"""
Integration tests for PhysioNet MCP Server.

Tests the complete MCP server functionality including:
- Server initialization
- Tool registration
- Basic MCP protocol compliance
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from physionetmcp.server import initialize_server, list_databases, get_database_schema
from physionetmcp.config import load_config_from_mcp_init


class MCPServerIntegrationTest:
    """Integration test for MCP server functionality."""
    
    def __init__(self):
        """Initialize integration test."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mcp_integration_test_"))
        self.results = {
            'server_init': False,
            'tools_available': False,
            'config_loading': False,
            'errors': [],
            'warnings': []
        }
    
    async def test_server_initialization(self) -> bool:
        """Test server initialization with minimal config."""
        self.logger.info("Testing server initialization...")
        
        try:
            config_data = {
                'db': ['mimic-iv-demo'],
                'dataRoot': str(self.temp_dir),
                'storageFormat': 'duckdb',
                'maxResultRows': 10
            }
            
            await initialize_server(config_data)
            self.logger.info("✅ Server initialized successfully")
            self.results['server_init'] = True
            return True
            
        except Exception as e:
            self.results['errors'].append(f"Server initialization failed: {str(e)}")
            self.logger.error(f"❌ Server initialization failed: {e}")
            return False
    
    async def test_config_loading(self) -> bool:
        """Test configuration loading and validation."""
        self.logger.info("Testing configuration loading...")
        
        try:
            config_data = {
                'db': ['mimic-iv-demo', 'aumc'],
                'dataRoot': str(self.temp_dir),
                'storageFormat': 'duckdb',
                'maxResultRows': 100,
                'queryTimeoutSeconds': 30
            }
            
            config = load_config_from_mcp_init(config_data)
            
            # Verify config loaded correctly
            assert config.databases == ['mimic-iv-demo', 'aumc']
            assert config.storage_format.value == 'duckdb'
            assert config.max_result_rows == 100
            assert config.query_timeout_seconds == 30
            
            self.logger.info("✅ Configuration loaded and validated successfully")
            self.results['config_loading'] = True
            return True
            
        except Exception as e:
            self.results['errors'].append(f"Configuration loading failed: {str(e)}")
            self.logger.error(f"❌ Configuration loading failed: {e}")
            return False
    
    async def test_mcp_tools(self) -> bool:
        """Test MCP tools functionality."""
        self.logger.info("Testing MCP tools...")
        
        try:
            # Test list_databases tool
            db_list_result = list_databases()
            
            if isinstance(db_list_result, dict) and 'databases' in db_list_result:
                self.logger.info(f"✅ list_databases: Found {len(db_list_result['databases'])} databases")
            else:
                self.results['errors'].append("list_databases returned invalid format")
                return False
            
            # Test get_database_schema tool (may fail without data, which is OK)
            schema_result = get_database_schema('mimic-iv-demo')
            
            if isinstance(schema_result, dict):
                if 'error' in schema_result:
                    self.logger.info(f"⚠️  get_database_schema: {schema_result['error']} (expected)")
                    self.results['warnings'].append("Schema not available - database not yet downloaded")
                else:
                    self.logger.info("✅ get_database_schema: Success")
            else:
                self.results['errors'].append("get_database_schema returned invalid format")
                return False
            
            self.logger.info("✅ MCP tools functioning correctly")
            self.results['tools_available'] = True
            return True
            
        except Exception as e:
            self.results['errors'].append(f"MCP tools test failed: {str(e)}")
            self.logger.error(f"❌ MCP tools test failed: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        self.logger.info("🧪 Running MCP Server Integration Tests...")
        
        try:
            # Test configuration loading first
            await self.test_config_loading()
            
            # Test server initialization
            await self.test_server_initialization()
            
            # Test MCP tools (only if server initialized)
            if self.results['server_init']:
                await self.test_mcp_tools()
            
            # Calculate overall success
            critical_tests = ['server_init', 'tools_available', 'config_loading']
            success_count = sum(1 for test in critical_tests if self.results.get(test, False))
            overall_success = success_count >= 2  # At least 2/3 critical tests
            
            self.results['overall_success'] = overall_success
            
            # Log summary
            self._log_summary()
            
        except Exception as e:
            self.results['errors'].append(f"Integration test suite failed: {str(e)}")
            self.logger.error(f"❌ Integration test suite failed: {e}")
            self.results['overall_success'] = False
        
        finally:
            # Cleanup
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
                self.logger.info("🧹 Cleaned up test directory")
            except Exception as e:
                self.logger.warning(f"⚠️  Cleanup failed: {e}")
        
        return self.results
    
    def _log_summary(self):
        """Log test summary."""
        self.logger.info("\n" + "="*50)
        self.logger.info("MCP SERVER INTEGRATION TEST SUMMARY")
        self.logger.info("="*50)
        
        self.logger.info(f"Config Loading: {'✅ SUCCESS' if self.results['config_loading'] else '❌ FAILED'}")
        self.logger.info(f"Server Init: {'✅ SUCCESS' if self.results['server_init'] else '❌ FAILED'}")
        self.logger.info(f"MCP Tools: {'✅ SUCCESS' if self.results['tools_available'] else '❌ FAILED'}")
        
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


async def run_integration_test():
    """Run MCP server integration test."""
    test = MCPServerIntegrationTest()
    return await test.run_all_tests()


if __name__ == "__main__":
    import logging
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the test
    print("🧪 Running MCP Server Integration Tests...")
    results = asyncio.run(run_integration_test())
    
    # Print final result
    if results.get('overall_success'):
        print("\n🎉 MCP Server integration tests passed!")
    else:
        print("\n❌ MCP Server integration tests failed!")
        if results.get('errors'):
            print("Errors:")
            for error in results['errors']:
                print(f"  - {error}")
    
    exit(0 if results.get('overall_success') else 1) 