#!/usr/bin/env python3
"""
Demo script for Gemini + MCP Weather integration
Shows various usage examples
"""

import asyncio
import os
import sys
from gemini_client import GeminiMCPClient

async def demo_conversation():
    """Run a demo conversation with various weather queries"""
    
    demo_queries = [
        "Houston'da hava nasıl?",
        "What's the weather like in New York today?",
        "Will it rain in Los Angeles tomorrow?", 
        "Any weather alerts for California?",
        "Compare weather between Chicago and Miami",
        "Should I bring an umbrella to Seattle?",
        "What's the temperature in Phoenix right now?",
        "Is there a storm coming to Texas?"
    ]
    
    print("🤖 Gemini Weather Assistant Demo")
    print("=" * 50)
    print("📋 Demo will run these queries:")
    for i, query in enumerate(demo_queries, 1):
        print(f"   {i}. {query}")
    
    print("\n⏳ Starting demo in 3 seconds...")
    await asyncio.sleep(3)
    
    # Initialize client
    client = GeminiMCPClient()
    await client.connect()
    
    print("\n🚀 Demo Started!\n")
    
    for i, query in enumerate(demo_queries, 1):
        print(f"{'='*60}")
        print(f"📝 Demo Query {i}/{len(demo_queries)}")
        print(f"You: {query}")
        print("-" * 60)
        
        try:
            response = await client.chat_with_weather(query)
            print(f"🤖 Gemini: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print(f"\n⏳ Next query in 2 seconds...\n")
        await asyncio.sleep(2)
    
    print("🎉 Demo completed!")
    await client.disconnect()

async def interactive_demo():
    """Interactive demo mode"""
    print("🤖 Interactive Gemini Weather Assistant")
    print("=" * 50)
    print("💭 Ask me anything about weather!")
    print("💡 Examples:")
    print("   - 'Houston weather'")
    print("   - 'Will it rain in NYC?'")
    print("   - 'Weather alerts for CA'")
    print("   - 'Should I wear a jacket in Seattle?'")
    print("\n🔧 Commands:")
    print("   /demo  - Run automated demo")
    print("   /help  - Show this help")
    print("   /quit  - Exit")
    print("\n" + "="*50)
    
    client = GeminiMCPClient()
    await client.connect()
    
    print("✅ Ready! Ask me about weather...\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['/quit', 'quit', 'exit']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == '/demo':
                print("\n🎬 Starting automated demo...")
                await demo_conversation()
                print("\n🔙 Back to interactive mode...\n")
                continue
            
            if user_input.lower() == '/help':
                print("""
🆘 Help:
   - Ask natural questions about weather
   - Supported: US cities and states
   - Examples: 'weather in Miami', 'alerts for Texas'
   - Commands: /demo, /help, /quit
""")
                continue
            
            if len(user_input) == 0:
                continue
            
            response = await client.chat_with_weather(user_input)
            print(f"🤖 Gemini: {response}\n")
            
        except KeyboardInterrupt:
            print("\n🛑 Goodbye!")
            break
        except EOFError:
            print("\n🛑 Goodbye!")
            break
    
    await client.disconnect()

async def main():
    """Main function"""
    if not os.getenv('GOOGLE_AI_API_KEY'):
        print("❌ Please set GOOGLE_AI_API_KEY environment variable")
        print("📋 Get your API key from: https://aistudio.google.com/app/apikey")
        print("\nWindows: set GOOGLE_AI_API_KEY=your_key")
        print("Linux/Mac: export GOOGLE_AI_API_KEY=your_key")
        sys.exit(1)
    
    # Check arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--demo':
            await demo_conversation()
        elif sys.argv[1] == '--help':
            print("""
🤖 Gemini + MCP Weather Demo

Usage:
    python demo_gemini_weather.py [option]

Options:
    --demo     Run automated demo with sample queries
    --help     Show this help
    (no args) Run interactive mode

Features:
    🧠 Natural language weather queries
    🌤️ Real-time US weather data
    🚨 Weather alerts and warnings
    💬 Conversational AI responses

Examples:
    "What's the weather in Houston?"
    "Will it rain tomorrow in Seattle?"
    "Any storms coming to Florida?"
""")
        else:
            print(f"❌ Unknown option: {sys.argv[1]}")
            print("Use --help for options")
    else:
        await interactive_demo()

if __name__ == '__main__':
    asyncio.run(main())
