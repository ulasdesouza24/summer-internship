#!/usr/bin/env python3
"""
Test script for Gemini + MCP Weather integration
"""

import asyncio
import os
import sys
from gemini_client import GeminiMCPClient

async def test_basic_connection():
    """Test basic connection to both Gemini and MCP"""
    print("🧪 Testing basic connections...")
    
    # Check API key
    if not os.getenv('GOOGLE_AI_API_KEY'):
        print("❌ GOOGLE_AI_API_KEY not set")
        return False
    
    try:
        client = GeminiMCPClient()
        await client.connect()
        print("✅ Connections successful")
        await client.disconnect()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def test_weather_query():
    """Test a simple weather query"""
    print("\n🧪 Testing weather query...")
    
    try:
        client = GeminiMCPClient()
        await client.connect()
        
        # Simple test query
        response = await client.chat_with_weather("What's the weather in Houston?")
        print(f"✅ Response received: {response[:100]}...")
        
        await client.disconnect()
        return True
    except Exception as e:
        print(f"❌ Weather query failed: {e}")
        return False

async def test_tool_conversion():
    """Test MCP to Gemini tool conversion"""
    print("\n🧪 Testing tool schema conversion...")
    
    try:
        client = GeminiMCPClient()
        await client.connect()
        
        tools = client.convert_mcp_tools_to_gemini_format()
        print(f"✅ Converted {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description'][:50]}...")
        
        await client.disconnect()
        return True
    except Exception as e:
        print(f"❌ Tool conversion failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🚀 Gemini + MCP Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Basic Connection", test_basic_connection),
        ("Tool Conversion", test_tool_conversion),
        ("Weather Query", test_weather_query)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Ready to use Gemini + MCP Weather client.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("""
🧪 Gemini + MCP Integration Test Suite

Usage:
    python test_gemini_integration.py

Requirements:
    - GOOGLE_AI_API_KEY environment variable set
    - MCP weather server available
    - All dependencies installed

This script tests:
    ✓ Basic connections (Gemini + MCP)
    ✓ Tool schema conversion
    ✓ Weather query functionality
""")
    else:
        asyncio.run(run_all_tests())
