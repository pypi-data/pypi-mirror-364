#!/usr/bin/env python3
"""
KForce Demo Cleanup Script
Removes demo tables from the database
"""

import requests
import json

def cleanup_kforce_demo():
    """Clean up KForce demo tables"""
    print("🧹 KForce Demo Cleanup")
    print("=" * 50)
    
    cleanup_sql = """
    DROP TABLE IF EXISTS clean_employees CASCADE;
    DROP TABLE IF EXISTS raw_employees CASCADE;
    """
    
    mcp_url = "http://localhost:8081"
    
    try:
        print("🗑️ Removing demo tables...")
        response = requests.post(f"{mcp_url}/execute_tool", json={
            "tool_name": "SQLExecutor",
            "params": {"sql_query": cleanup_sql}
        }, headers={
            "X-Bridge-Secret": "test-secret-for-development",
            "Content-Type": "application/json"
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Demo tables removed successfully")
                print("   • raw_employees table dropped")
                print("   • clean_employees table dropped")
            else:
                print(f"⚠️ Cleanup had issues: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Failed to cleanup tables: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        print("💡 Make sure the MCP bridge server is running on port 8081")
    
    print("✅ Cleanup complete")

if __name__ == "__main__":
    cleanup_kforce_demo() 