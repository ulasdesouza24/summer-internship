#!/usr/bin/env python3
import asyncio
import json
import os
import sys
import subprocess
from typing import List, Dict, Any, Optional

class MCPClient:
    def __init__(self):
        self.process = None
        self.available_tools = []
        
    async def connect(self):
        try:
            print('🔌 Connecting to MCP Weather Server...')
            
            # Start the Python weather server process
            server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weather-server-python')
            server_script = os.path.join(server_dir, 'weather.py')

            if not os.path.isdir(server_dir):
                raise FileNotFoundError(f"Weather server directory not found: {server_dir}")
            if not os.path.isfile(server_script):
                raise FileNotFoundError(f"Weather server script not found: {server_script}")

            self.process = subprocess.Popen(
                [sys.executable, server_script],
                cwd=server_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,  # Keep stderr separate
                text=True,
                bufsize=0
            )
            
            # Give the server a moment to start
            import time
            time.sleep(0.5)
            
            # Initialize the MCP connection with correct protocol version
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "mcp-weather-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            await self._send_message(init_message)
            response = await self._receive_message()
            
            if response.get('error'):
                raise Exception(f"Initialization failed: {response['error']}")
            
            # Send initialized notification
            initialized_message = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            await self._send_message(initialized_message)
                
            print('✅ Connected to MCP Weather Server')
            await self.get_available_tools()
            
        except Exception as error:
            print(f'❌ Weather server connection failed: {error}')
            raise error
    
    async def _send_message(self, message):
        if self.process and self.process.stdin:
            json_str = json.dumps(message) + '\n'
            self.process.stdin.write(json_str)
            self.process.stdin.flush()
    
    async def _receive_message(self):
        if self.process and self.process.stdout:
            line = self.process.stdout.readline()
            if line:
                line = line.strip()
                # Skip non-JSON lines (like server startup messages)
                if line.startswith('{'):
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError as e:
                        print(f"❌ Invalid JSON from server: {line}")
                        print(f"❌ JSON Error: {e}")
                        return {}
                else:
                    # This is likely a log message, ignore it and try to read the next line
                    return await self._receive_message()
            else:
                print("📭 No response from server")
        return {}
    
    async def get_available_tools(self):
        try:
            message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            await self._send_message(message)
            response = await self._receive_message()
            

            
            self.available_tools = response.get('result', {}).get('tools', [])
            tool_names = [tool['name'] for tool in self.available_tools]
            print(f'🌤️ Available weather tools: {", ".join(tool_names)}')
            
        except Exception as error:
            print(f'❌ Failed to get weather tools: {error}')
    
    def convert_tools_to_gemini_schema(self):
        return [
            {
                'name': tool['name'],
                'description': tool['description'],
                'parameters': tool.get('inputSchema', {})
            }
            for tool in self.available_tools
        ]
    
    async def call_mcp_tool(self, tool_name: str, args: Dict[str, Any]):
        try:
            print(f'🌤️ Getting weather data: {tool_name}({json.dumps(args)})')
            
            message = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": args
                }
            }
            
            await self._send_message(message)
            response = await self._receive_message()
            
            if response.get('error'):
                return {'error': response['error']['message']}
            
            result = response.get('result', {})

            return result
            
        except Exception as error:
            print(f'❌ Weather tool call failed: {error}')
            return {'error': str(error)}
    
    async def disconnect(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            print('👋 Disconnected from MCP Weather Server')

class MCPWeatherClient:
    def __init__(self):
        self.mcp_client = MCPClient()
    
    async def connect(self):
        await self.mcp_client.connect()
    
    async def get_weather(self, user_input: str) -> str:
        """Parse user input and call appropriate weather functions."""
        user_input = user_input.lower().strip()
        
        # Simple parsing for demonstration
        if any(keyword in user_input for keyword in ['alert', 'uyarı', 'warning']):
            # For alerts, we need a US state code
            if len(user_input.split()) > 1:
                # Try to extract state code (this is a simple implementation)
                words = user_input.split()
                for word in words:
                    if len(word) == 2 and word.isalpha():
                        return await self.mcp_client.call_mcp_tool('get_alerts', {'state': word.upper()})
            return "❌ For weather alerts, please provide a US state code (e.g., 'alerts CA')"
        
        else:
            # Only US cities for NWS API - tested coordinates
            city_coords = {
                'new york': {'latitude': 40.7128, 'longitude': -74.0060},
                'los angeles': {'latitude': 34.0522, 'longitude': -118.2437},
                'chicago': {'latitude': 41.8781, 'longitude': -87.6298},
                'houston': {'latitude': 29.7604, 'longitude': -95.3698},
                'phoenix': {'latitude': 33.4484, 'longitude': -112.0740},
                'philadelphia': {'latitude': 39.9526, 'longitude': -75.1652},
                'san antonio': {'latitude': 29.4241, 'longitude': -98.4936},
                'san diego': {'latitude': 32.7157, 'longitude': -117.1611},
                'dallas': {'latitude': 32.7767, 'longitude': -96.7970},
                'san jose': {'latitude': 37.3382, 'longitude': -121.8863},
                'austin': {'latitude': 30.2672, 'longitude': -97.7431},
                'jacksonville': {'latitude': 30.3322, 'longitude': -81.6557},
                'san francisco': {'latitude': 37.7749, 'longitude': -122.4194},
                'columbus': {'latitude': 39.9612, 'longitude': -82.9988},
                'charlotte': {'latitude': 35.2271, 'longitude': -80.8431},
                'fort worth': {'latitude': 32.7555, 'longitude': -97.3308},
                'detroit': {'latitude': 42.3314, 'longitude': -83.0458},
                'el paso': {'latitude': 31.7619, 'longitude': -106.4850},
                'memphis': {'latitude': 35.1495, 'longitude': -90.0490},
                'seattle': {'latitude': 47.6062, 'longitude': -122.3321},
                'denver': {'latitude': 39.7392, 'longitude': -104.9903},
                'washington': {'latitude': 38.9072, 'longitude': -77.0369},
                'boston': {'latitude': 42.3601, 'longitude': -71.0589},
                'nashville': {'latitude': 36.1627, 'longitude': -86.7816},
                'baltimore': {'latitude': 39.2904, 'longitude': -76.6122},
                'oklahoma city': {'latitude': 35.4676, 'longitude': -97.5164},
                'portland': {'latitude': 45.5152, 'longitude': -122.6784},
                'las vegas': {'latitude': 36.1699, 'longitude': -115.1398},
                'milwaukee': {'latitude': 43.0389, 'longitude': -87.9065},
                'albuquerque': {'latitude': 35.0844, 'longitude': -106.6504},
                'tucson': {'latitude': 32.2226, 'longitude': -110.9747},
                'fresno': {'latitude': 36.7378, 'longitude': -119.7871},
                'sacramento': {'latitude': 38.5816, 'longitude': -121.4944},
                'miami': {'latitude': 25.7617, 'longitude': -80.1918},
                'kansas city': {'latitude': 39.0997, 'longitude': -94.5786},
                'mesa': {'latitude': 33.4152, 'longitude': -111.8315},
                'atlanta': {'latitude': 33.7490, 'longitude': -84.3880},
                'omaha': {'latitude': 41.2565, 'longitude': -95.9345},
                'raleigh': {'latitude': 35.7796, 'longitude': -78.6382},
                'colorado springs': {'latitude': 38.8339, 'longitude': -104.8214},
                'virginia beach': {'latitude': 36.8529, 'longitude': -76.0927}
            }
            
            # Find city in user input
            found_city = None
            for city, coords in city_coords.items():
                if city in user_input:
                    found_city = city
                    break
            
            if found_city:
                coords = city_coords[found_city]
                result = await self.mcp_client.call_mcp_tool('get_forecast', coords)
                if result.get('error'):
                    return f"❌ Weather service error: {result['error']}"
                else:
                    # Extract the actual content from the MCP response
                    content = result.get('content', [])
                    if isinstance(content, list) and len(content) > 0:
                        weather_text = content[0].get('text', str(result))
                    else:
                        weather_text = str(result)
                    return f"🌤️ Weather forecast for {found_city.title()}:\n\n{weather_text}"
            else:
                return f"""❌ City not found. Available US cities:

🇺🇸 Major Cities:
New York, Los Angeles, Chicago, Houston, Phoenix, Philadelphia

🇺🇸 West Coast:
San Francisco, Seattle, Portland, Las Vegas, Denver, Sacramento

🇺🇸 South:
Austin, Jacksonville, Charlotte, Fort Worth, El Paso, Memphis, Nashville, Atlanta, Miami

🇺🇸 Midwest/Northeast:
Detroit, Columbus, Milwaukee, Kansas City, Omaha, Boston, Baltimore, Washington

🇺🇸 Southwest:
Albuquerque, Tucson, Colorado Springs, Oklahoma City, Mesa, Virginia Beach

Usage examples:
- "New York" or "Seattle" 
- "alerts CA" (for weather alerts)

Note: Only US cities are supported for accurate weather data."""
    
    async def disconnect(self):
        await self.mcp_client.disconnect()

async def main():
    print('🌤️ MCP Weather Client Starting...')
    
    client = MCPWeatherClient()
    
    try:
        await client.connect()
        
        print('\n💬 Weather chat started! Ask about weather in any city. Type "/help" for commands or "/quit" to exit\n')
        
        while True:
            try:
                message = input('You: ').strip()
                
                if message == '/quit':
                    print('👋 Goodbye!')
                    await client.disconnect()
                    break
                
                if message == '/help':
                    tool_names = [tool['name'] for tool in client.mcp_client.available_tools]
                    print(f"""
Commands:
  /help  - Show this help
  /tools - List available weather tools  
  /quit  - Exit the client

Available weather tools: {', '.join(tool_names)}

Examples:
- "New York" or "Seattle"
- "alerts CA" (US weather alerts)

Supported locations:
🇺🇸 US Cities only: Real weather data from National Weather Service

Type any invalid city name to see full US city list.
""")
                    continue
                
                if message == '/tools':
                    print('Available weather tools:')
                    for tool in client.mcp_client.available_tools:
                        print(f"- {tool['name']}: {tool['description']}")
                    continue
                
                if len(message) == 0:
                    continue
                
                print('🌤️ Getting weather data...')
                response = await client.get_weather(message)
                print(f'{response}\n')
                
            except KeyboardInterrupt:
                print('\n🛑 Shutting down weather client...')
                await client.disconnect()
                break
            except EOFError:
                print('\n🛑 Shutting down weather client...')
                await client.disconnect()
                break
    
    except Exception as error:
        print(f'💥 Failed to start weather client: {error}')
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())