#!/usr/bin/env python3
"""
Test script to verify MCP weather server is working correctly.
Run this before configuring in Cursor IDE.
"""

import subprocess
import json
import sys
import os

def test_mcp_server():
    print("🧪 Testing MCP Weather Server...")
    
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_dir = os.path.join(current_dir, 'weather-server-python')
    server_script = os.path.join(server_dir, 'weather.py')
    
    print(f"📂 Server directory: {server_dir}")
    print(f"📄 Server script: {server_script}")
    
    if not os.path.exists(server_script):
        print(f"❌ Server script not found: {server_script}")
        return False
    
    try:
        # Start server
        process = subprocess.Popen(
            [sys.executable, server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=server_dir
        )
        
        # Test initialization
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        process.stdin.write(json.dumps(init_msg) + '\n')
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        if response:
            resp_data = json.loads(response.strip())
            if not resp_data.get('error'):
                print("✅ MCP Server initialization successful")
                
                # Send initialized notification
                init_notify = {"jsonrpc": "2.0", "method": "notifications/initialized"}
                process.stdin.write(json.dumps(init_notify) + '\n')
                process.stdin.flush()
                
                # Test tools list
                tools_msg = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
                
                process.stdin.write(json.dumps(tools_msg) + '\n')
                process.stdin.flush()
                
                tools_response = process.stdout.readline()
                if tools_response:
                    tools_data = json.loads(tools_response.strip())
                    tools = tools_data.get('result', {}).get('tools', [])
                    print(f"🔧 Available tools: {[tool['name'] for tool in tools]}")
                    
                    if len(tools) > 0:
                        print("✅ MCP Server is ready for Cursor IDE!")
                        return True
                    else:
                        print("❌ No tools found")
                        return False
            else:
                print(f"❌ Initialization failed: {resp_data['error']}")
                return False
        else:
            print("❌ No response from server")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        if process:
            process.terminate()
            process.wait()

if __name__ == '__main__':
    success = test_mcp_server()
    if success:
        print("\n🎉 Server is ready! You can now add it to Cursor IDE.")
        print("\n📋 Next steps:")
        print("1. Open Cursor IDE Settings (Ctrl+,)")
        print("2. Search for 'MCP'")
        print("3. Add the weather server configuration")
        print("4. Restart Cursor IDE")
    else:
        print("\n❌ Server test failed. Please check the setup.")
    
    sys.exit(0 if success else 1)
