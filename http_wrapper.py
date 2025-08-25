#!/usr/bin/env python3
"""
HTTP wrapper for MCP Weather Server to make it compatible with TestSprite
"""

from flask import Flask, request, jsonify
import asyncio
import subprocess
import json
import sys
import os
from threading import Thread
import time

app = Flask(__name__)

class MCPServerWrapper:
    def __init__(self):
        self.process = None
        self.setup_server()
    
    def setup_server(self):
        """Setup the MCP server process"""
        try:
            server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weather-server-python')
            server_script = os.path.join(server_dir, 'weather.py')
            
            self.process = subprocess.Popen(
                [sys.executable, server_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=server_dir,
                bufsize=0
            )
            
            # Initialize MCP connection
            time.sleep(0.5)
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "http-wrapper", "version": "1.0.0"}
                }
            }
            
            self.send_message(init_message)
            response = self.receive_message()
            
            if not response.get('error'):
                # Send initialized notification
                initialized_message = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                self.send_message(initialized_message)
                print("✅ MCP Server initialized successfully")
            else:
                print(f"❌ MCP Server initialization failed: {response.get('error')}")
                
        except Exception as e:
            print(f"❌ Failed to setup MCP server: {e}")
    
    def send_message(self, message):
        if self.process and self.process.stdin:
            json_str = json.dumps(message) + '\n'
            self.process.stdin.write(json_str)
            self.process.stdin.flush()
    
    def receive_message(self):
        if self.process and self.process.stdout:
            line = self.process.stdout.readline()
            if line:
                line = line.strip()
                if line.startswith('{'):
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError:
                        return {}
        return {}
    
    def call_tool(self, tool_name, arguments):
        """Call MCP tool and return result"""
        try:
            message = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            self.send_message(message)
            response = self.receive_message()
            
            if response.get('error'):
                return {'error': response['error']['message']}
            
            return response.get('result', {})
            
        except Exception as e:
            return {'error': str(e)}

# Global MCP wrapper instance
mcp_wrapper = MCPServerWrapper()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "MCP Weather Server HTTP Wrapper"})

@app.route('/weather/forecast', methods=['POST'])
def get_forecast():
    """Get weather forecast"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            return jsonify({'error': 'latitude and longitude are required'}), 400
        
        result = mcp_wrapper.call_tool('get_forecast', {
            'latitude': float(latitude),
            'longitude': float(longitude)
        })
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/weather/alerts', methods=['POST'])
def get_alerts():
    """Get weather alerts"""
    try:
        data = request.get_json()
        state = data.get('state')
        
        if not state:
            return jsonify({'error': 'state is required'}), 400
        
        result = mcp_wrapper.call_tool('get_alerts', {'state': state.upper()})
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/weather/cities', methods=['GET'])
def get_supported_cities():
    """Get list of supported cities"""
    cities = [
        'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
        'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose',
        'Austin', 'Jacksonville', 'San Francisco', 'Columbus', 'Charlotte',
        'Fort Worth', 'Detroit', 'El Paso', 'Memphis', 'Seattle',
        'Denver', 'Washington', 'Boston', 'Nashville', 'Baltimore',
        'Oklahoma City', 'Portland', 'Las Vegas', 'Milwaukee', 'Albuquerque',
        'Tucson', 'Fresno', 'Sacramento', 'Miami', 'Kansas City',
        'Mesa', 'Atlanta', 'Omaha', 'Raleigh', 'Colorado Springs',
        'Virginia Beach'
    ]
    return jsonify({"supported_cities": cities})

if __name__ == '__main__':
    print("🌤️ Starting MCP Weather Server HTTP Wrapper...")
    print("📡 Server will be available at http://localhost:8000")
    print("🔗 Endpoints:")
    print("  - GET  /health")
    print("  - POST /weather/forecast (requires latitude, longitude)")
    print("  - POST /weather/alerts (requires state)")
    print("  - GET  /weather/cities")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
