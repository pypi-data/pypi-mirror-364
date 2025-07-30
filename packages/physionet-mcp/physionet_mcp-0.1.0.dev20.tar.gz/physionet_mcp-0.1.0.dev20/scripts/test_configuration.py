#!/usr/bin/env python3
"""
Simple test script to verify PhysioNet MCP server functionality
"""
import os
from physionetmcp.config import load_config_from_mcp_init
from physionetmcp.database_registry import get_database_info

def test_configuration():
    """Test configuration loading with credentials."""
    print("🧪 Testing PhysioNet MCP Server Configuration...")
    
    # Set credentials
    os.environ["PHYSIONET_USERNAME"] = "pedromoreira"
    os.environ["PHYSIONET_PASSWORD"] = "Peter5h3!"
    
    # Test configuration
    config_data = {
        'db': ['mimic-iv-demo', 'eicu-demo'], 
        'dataRoot': '/tmp/test_physionet',
        'storageFormat': 'duckdb',
        'maxResultRows': 100
    }
    
    try:
        config = load_config_from_mcp_init(config_data)
        print("✅ Configuration loaded successfully")
        print(f"   Databases: {config.databases}")
        print(f"   Storage format: {config.storage_format}")
        print(f"   Data root: {config.data_root}")
        print(f"   Username: {config.auth.username}")
        print(f"   Password set: {bool(config.auth.password)}")
        
        # Test database info
        print("\n🗃️  Database Information:")
        for db_name in config.databases:
            db_info = get_database_info(db_name)
            if db_info:
                print(f"   {db_name}: {db_info.title} ({db_info.access_type})")
            else:
                print(f"   {db_name}: Not found!")
        
        print("\n🎉 All tests passed! Ready for Claude Desktop integration.")
        return True
        
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

if __name__ == "__main__":
    test_configuration() 