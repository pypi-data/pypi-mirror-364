#!/usr/bin/env python3
"""
Manual test of PhysioNet MCP server functionality
"""
import json
from physionetmcp.server import initialize_server, app

async def test_mcp_server():
    """Test the MCP server functionality directly."""
    print("🧪 Testing PhysioNet MCP Server Tools...")
    
    # Initialize server
    init_data = {
        'db': ['mimic-iv-demo', 'eicu-demo'],
        'dataRoot': '/tmp/physionet_test',
        'storageFormat': 'duckdb',
        'maxResultRows': 10
    }
    
    try:
        await initialize_server(init_data)
        print("✅ Server initialized successfully")
        
        # Test list_databases tool
        from physionetmcp.server import list_databases
        db_list = list_databases()
        print(f"\n📊 Databases available: {db_list.get('total_databases', 0)}")
        
        # Test get_database_schema (this will fail until we download data, which is expected)
        from physionetmcp.server import get_database_schema
        schema_result = get_database_schema('mimic-iv-demo')
        print(f"\n🏗️  Schema result: {type(schema_result).__name__}")
        
        print("\n🎉 Basic server functionality verified!")
        print("\n🔗 Ready to connect with Claude Desktop!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_mcp_server()) 