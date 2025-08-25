#!/usr/bin/env python3
"""
Gemini API Client with MCP Weather Tools Integration
Hybrid approach: Gemini AI + MCP Weather Server
"""

import asyncio
import json
import os
import sys
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from client import MCPClient

# Load environment variables from .env file
load_dotenv()

class GeminiMCPClient:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client with MCP integration
        
        Args:
            api_key: Google AI API key. If None, will try to get from environment
        """
        self.api_key = api_key or os.getenv('GOOGLE_AI_API_KEY')
        if not self.api_key:
            raise ValueError("Google AI API key required. Set GOOGLE_AI_API_KEY environment variable or pass api_key parameter.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # MCP Weather Client
        self.mcp_client = MCPClient()
        self.available_tools = []
        
        # Chat session
        self.chat = None
        
    async def connect(self):
        """Connect to MCP weather server and setup Gemini with tools"""
        try:
            print('🔌 Connecting to MCP Weather Server...')
            await self.mcp_client.connect()
            
            # Get available tools and convert to Gemini format
            self.available_tools = self.convert_mcp_tools_to_gemini_format()
            
            # Initialize Gemini chat with tools
            self.chat = self.model.start_chat(
                history=[],
                enable_automatic_function_calling=True
            )
            
            print('🤖 Gemini AI connected with weather tools')
            print(f'🌤️ Available tools: {[tool["name"] for tool in self.available_tools]}')
            
        except Exception as error:
            print(f'❌ Connection failed: {error}')
            raise error
    
    def convert_mcp_tools_to_gemini_format(self) -> List[Dict[str, Any]]:
        """
        Convert MCP tools to Gemini Function Calling format
        
        Returns:
            List of Gemini-compatible function declarations
        """
        gemini_tools = []
        
        for tool in self.mcp_client.available_tools:
            # Convert MCP tool schema to Gemini format
            gemini_tool = {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": self._convert_input_schema(tool.get("inputSchema", {}))
            }
            gemini_tools.append(gemini_tool)
        
        return gemini_tools
    
    def _convert_input_schema(self, input_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MCP inputSchema to Gemini parameters format
        
        Args:
            input_schema: MCP tool input schema
            
        Returns:
            Gemini-compatible parameters schema
        """
        if not input_schema:
            return {"type": "object", "properties": {}}
        
        # Handle JSON Schema format
        gemini_params = {
            "type": input_schema.get("type", "object"),
            "properties": {},
            "required": input_schema.get("required", [])
        }
        
        # Convert properties
        properties = input_schema.get("properties", {})
        for prop_name, prop_schema in properties.items():
            gemini_params["properties"][prop_name] = {
                "type": prop_schema.get("type", "string"),
                "description": prop_schema.get("description", "")
            }
            
            # Handle enum values
            if "enum" in prop_schema:
                gemini_params["properties"][prop_name]["enum"] = prop_schema["enum"]
        
        return gemini_params
    
    async def chat_with_weather(self, user_message: str) -> str:
        """
        Chat with Gemini AI that can access weather tools
        
        Args:
            user_message: User's input message
            
        Returns:
            Gemini's response with weather data if needed
        """
        try:
            print(f'🧠 Processing with Gemini AI: {user_message}')
            
            # Simple approach: Let's manually handle common weather queries first
            # and call MCP tools directly, then format response
            
            user_lower = user_message.lower()
            
            # Check for city weather requests
            if any(city in user_lower for city in ['houston', 'new york', 'los angeles', 'chicago', 'miami', 'seattle', 'phoenix']):
                return await self._handle_city_weather(user_message)
            
            # Check for alerts
            elif any(word in user_lower for word in ['alert', 'warning', 'storm']):
                return await self._handle_weather_alerts(user_message)
            
            else:
                # General weather response
                return await self._generate_simple_response(user_message)
            
        except Exception as error:
            print(f'❌ Chat error: {error}')
            return f"Sorry, I encountered an error: {error}"
    
    async def _generate_with_tools(self, message: str, tools: List) -> str:
        """
        Generate response with tool calling capability
        
        Args:
            message: User message
            tools: Available Gemini tools
            
        Returns:
            Final response after tool calls
        """
        # System prompt for weather assistant
        system_prompt = """You are a helpful weather assistant with access to real-time weather data for US cities. 
        
You can:
- Get weather forecasts for any US city using coordinates
- Check weather alerts for US states
- Provide weather advice and recommendations
- Answer weather-related questions in a friendly, conversational manner

Available US cities include major cities like New York, Los Angeles, Chicago, Houston, etc.
For weather alerts, use 2-letter US state codes (CA, NY, TX, etc.).

Be conversational and helpful. If someone asks about weather, use the appropriate tools to get current data.
"""
        
        # Combine system prompt with user message
        full_prompt = f"{system_prompt}\n\nUser: {message}\nAssistant:"
        
        # Generate response
        model_with_tools = genai.GenerativeModel(
            'gemini-1.5-pro',
            tools=tools,
            system_instruction=system_prompt
        )
        
        response = model_with_tools.generate_content(message)
        
        # Handle function calls
        if response.candidates[0].content.parts:
            final_response_parts = []
            
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    # Execute the function call via MCP
                    function_name = part.function_call.name
                    function_args = dict(part.function_call.args)
                    
                    print(f'🔧 Calling weather tool: {function_name}({function_args})')
                    
                    # Call MCP tool
                    mcp_result = await self.mcp_client.call_mcp_tool(function_name, function_args)
                    
                    # Format the result for Gemini
                    tool_result = self._format_mcp_result(mcp_result)
                    
                    # Continue conversation with tool result
                    follow_up_response = model_with_tools.generate_content([
                        message,
                        response.candidates[0].content,
                        genai.protos.Content(parts=[
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=function_name,
                                    response={"result": tool_result}
                                )
                            )
                        ])
                    ])
                    
                    return follow_up_response.text
                
                elif hasattr(part, 'text') and part.text:
                    final_response_parts.append(part.text)
            
            return "".join(final_response_parts)
        
        return response.text if response.text else "I'm sorry, I couldn't generate a response."
    
    def _format_mcp_result(self, mcp_result: Dict[str, Any]) -> str:
        """
        Format MCP tool result for Gemini consumption
        
        Args:
            mcp_result: Result from MCP tool call
            
        Returns:
            Formatted result string
        """
        if 'error' in mcp_result:
            return f"Error: {mcp_result['error']}"
        
        # Extract content from MCP response
        content = mcp_result.get('content', [])
        if isinstance(content, list) and len(content) > 0:
            return content[0].get('text', str(mcp_result))
        
        return str(mcp_result)
    
    async def _handle_city_weather(self, user_message: str) -> str:
        """Handle city weather requests"""
        # City coordinates mapping
        city_coords = {
            'houston': {'latitude': 29.7604, 'longitude': -95.3698},
            'new york': {'latitude': 40.7128, 'longitude': -74.0060},
            'los angeles': {'latitude': 34.0522, 'longitude': -118.2437},
            'chicago': {'latitude': 41.8781, 'longitude': -87.6298},
            'miami': {'latitude': 25.7617, 'longitude': -80.1918},
            'seattle': {'latitude': 47.6062, 'longitude': -122.3321},
            'phoenix': {'latitude': 33.4484, 'longitude': -112.0740}
        }
        
        user_lower = user_message.lower()
        found_city = None
        
        for city in city_coords:
            if city in user_lower:
                found_city = city
                break
        
        if found_city:
            coords = city_coords[found_city]
            print(f'🔧 Getting weather for {found_city.title()}')
            
            # Call MCP tool directly
            result = await self.mcp_client.call_mcp_tool('get_forecast', coords)
            
            if 'error' in result:
                return f"❌ Sorry, I couldn't get weather data for {found_city.title()}: {result['error']}"
            
            # Get raw weather data
            weather_data = self._format_mcp_result(result)
            
            # Now use Gemini to provide an intelligent response based on the weather data
            return await self._generate_intelligent_response(user_message, found_city, weather_data)
        
        return "❌ I couldn't identify the city you're asking about."
    
    async def _handle_weather_alerts(self, user_message: str) -> str:
        """Handle weather alerts requests"""
        # Extract state if mentioned
        states = {
            'california': 'CA', 'texas': 'TX', 'florida': 'FL', 'new york': 'NY',
            'illinois': 'IL', 'washington': 'WA', 'arizona': 'AZ'
        }
        
        user_lower = user_message.lower()
        found_state = None
        
        for state_name, state_code in states.items():
            if state_name in user_lower or state_code.lower() in user_lower:
                found_state = state_code
                break
        
        if found_state:
            print(f'🚨 Checking alerts for {found_state}')
            result = await self.mcp_client.call_mcp_tool('get_alerts', {'state': found_state})
            
            if 'error' in result:
                return f"❌ Sorry, I couldn't get alerts for {found_state}: {result['error']}"
            
            alerts_data = self._format_mcp_result(result)
            return f"🚨 Weather alerts for {found_state}:\n\n{alerts_data}"
        
        return "❌ Please specify a US state for weather alerts (e.g., 'California', 'Texas', 'CA', 'TX')"
    
    async def _generate_intelligent_response(self, user_question: str, city: str, weather_data: str) -> str:
        """Generate intelligent response using Gemini based on weather data and user question"""
        try:
            prompt = f"""
You are a helpful and friendly weather assistant. A user asked: "{user_question}"

I have retrieved the current weather forecast for {city.title()}:

{weather_data}

Please provide a helpful, conversational response that directly answers their question using this weather information. 

Guidelines:
- Be conversational and friendly
- Give practical advice based on the weather data
- If they ask about umbrellas/rain, focus on precipitation chances
- If they ask about what to wear, consider temperature and conditions
- If they ask about outdoor activities, consider all relevant weather factors
- Keep it concise but informative
- Use emojis appropriately to make it engaging

Answer their specific question, don't just repeat the weather data.
"""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"❌ Gemini response error: {e}")
            # Fallback to basic response with weather data
            return f"🌤️ Here's the weather for {city.title()}:\n\n{weather_data}"

    async def _generate_simple_response(self, user_message: str) -> str:
        """Generate a simple Gemini response without tools"""
        try:
            response = self.model.generate_content(f"""
You are a helpful weather assistant. The user asked: "{user_message}"

Provide a helpful response about weather. If they're asking about a specific location, 
suggest they be more specific about US cities or states. Keep it friendly and conversational.
""")
            return response.text
        except Exception as e:
            return f"I understand you're asking about weather. Could you be more specific about which US city or state you're interested in?"

    async def disconnect(self):
        """Disconnect from MCP server"""
        await self.mcp_client.disconnect()
        print('👋 Disconnected from services')

async def main():
    """Main function for testing the Gemini MCP client"""
    print('🚀 Starting Gemini + MCP Weather Client...')
    
    # Check for API key
    if not os.getenv('GOOGLE_AI_API_KEY'):
        print('❌ Please set GOOGLE_AI_API_KEY environment variable')
        print('Get your API key from: https://aistudio.google.com/app/apikey')
        sys.exit(1)
    
    client = GeminiMCPClient()
    
    try:
        await client.connect()
        
        print('\n🤖 Gemini Weather Assistant Ready!')
        print('💭 Ask me about weather in any US city, or type "/quit" to exit\n')
        
        while True:
            try:
                user_input = input('You: ').strip()
                
                if user_input.lower() in ['/quit', 'quit', 'exit']:
                    print('👋 Goodbye!')
                    break
                
                if len(user_input) == 0:
                    continue
                
                # Get Gemini response with weather tools
                response = await client.chat_with_weather(user_input)
                print(f'🤖 Gemini: {response}\n')
                
            except KeyboardInterrupt:
                print('\n🛑 Shutting down...')
                break
            except EOFError:
                print('\n🛑 Shutting down...')
                break
    
    except Exception as error:
        print(f'💥 Failed to start client: {error}')
        sys.exit(1)
    
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
