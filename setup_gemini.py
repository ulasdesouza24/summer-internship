#!/usr/bin/env python3
"""
Setup script for Gemini + MCP Weather integration
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def check_api_key():
    """Check if Google AI API key is set"""
    # Try to load from .env file first
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if api_key and api_key != 'your_api_key_here':
        print("✅ Google AI API key found")
        return True
    else:
        print("❌ Google AI API key not found")
        print("📋 Please set your API key:")
        print("   1. Get API key from: https://aistudio.google.com/app/apikey")
        print("   2. Create .env file in project root:")
        print("      GOOGLE_AI_API_KEY=your_api_key_here")
        print("   3. Or set environment variable:")
        print("      Windows: set GOOGLE_AI_API_KEY=your_api_key_here")
        print("      Linux/Mac: export GOOGLE_AI_API_KEY=your_api_key_here")
        
        # Offer to create .env file
        if not os.path.exists('.env'):
            create_env = input("\n❓ Would you like me to create a .env file template? (y/n): ").lower()
            if create_env in ['y', 'yes']:
                create_env_file()
        
        return False

def create_env_file():
    """Create a .env file template"""
    try:
        env_content = """# Google AI API Key
# Get your API key from: https://aistudio.google.com/app/apikey
GOOGLE_AI_API_KEY=your_api_key_here

# Optional: Set to true for verbose debugging
DEBUG_MODE=false
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file template")
        print("📝 Please edit .env file and add your actual API key")
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")

def test_mcp_server():
    """Test if MCP weather server is working"""
    print("🌤️ Testing MCP weather server...")
    try:
        # Import and test basic MCP functionality
        from client import MCPClient
        print("✅ MCP client imports successfully")
        return True
    except ImportError as e:
        print(f"❌ MCP import failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Gemini + MCP Weather Setup")
    print("=" * 40)
    
    success = True
    
    # Install requirements
    if not install_requirements():
        success = False
    
    print()
    
    # Check API key
    if not check_api_key():
        success = False
    
    print()
    
    # Test MCP server
    if not test_mcp_server():
        success = False
    
    print("\n" + "=" * 40)
    
    if success:
        print("🎉 Setup completed successfully!")
        print("\n🚀 Ready to run:")
        print("   python gemini_client.py")
        print("\n💡 Example usage:")
        print('   You: "What\'s the weather in Houston today?"')
        print('   You: "Will it rain in New York tomorrow?"')
        print('   You: "Any weather alerts for California?"')
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
