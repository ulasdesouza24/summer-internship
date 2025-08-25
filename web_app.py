#!/usr/bin/env python3
"""
FastAPI Web Interface for Gemini + MCP Weather Assistant
Simple, fast, and embedded HTML interface
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import asyncio
from gemini_client import GeminiMCPClient
import os

# Load environment variables
load_dotenv()

app = FastAPI(title="🌤️ Gemini Weather Assistant", version="1.0.0")

# Global client instance
gemini_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize Gemini client on startup"""
    global gemini_client
    try:
        print("🚀 Starting Gemini Weather Assistant...")
        gemini_client = GeminiMCPClient()
        await gemini_client.connect()
        print("✅ Gemini client ready!")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global gemini_client
    if gemini_client:
        await gemini_client.disconnect()

@app.get("/", response_class=HTMLResponse)
async def home():
    """Main web interface"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌤️ Gemini Weather Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 800px;
            width: 100%;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        
        .chat-container {
            height: 400px;
            border: 2px solid #f0f0f0;
            border-radius: 15px;
            padding: 20px;
            overflow-y: auto;
            margin-bottom: 20px;
            background: #fafafa;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 12px 18px;
            border-radius: 12px;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        .user-message {
            background: #667eea;
            color: white;
            margin-left: auto;
        }
        
        .bot-message {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
        }
        
        .input-container {
            display: flex;
            gap: 10px;
        }
        
        .input-field {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .input-field:focus {
            border-color: #667eea;
        }
        
        .send-button {
            padding: 15px 25px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .send-button:hover {
            background: #5a67d8;
        }
        
        .send-button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .examples {
            margin-top: 20px;
            text-align: center;
        }
        
        .example-button {
            display: inline-block;
            margin: 5px;
            padding: 8px 15px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 20px;
            color: #666;
            text-decoration: none;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .example-button:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .loading {
            display: none;
            text-align: center;
            color: #666;
            font-style: italic;
        }
        
        @keyframes typing {
            0%, 60%, 100% { opacity: 0; }
            30% { opacity: 1; }
        }
        
        .typing-indicator {
            animation: typing 1.5s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌤️ Gemini Weather Assistant</h1>
            <p>Ask me anything about weather in US cities!</p>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message bot-message">
                👋 Hi! I'm your AI weather assistant powered by Gemini and real-time weather data. Ask me anything about weather in US cities!
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" class="input-field" 
                   placeholder="Ask about weather... (e.g., 'Should I bring umbrella in New York?')">
            <button id="sendButton" class="send-button">Send</button>
        </div>
        
        <div class="examples">
            <div style="margin-bottom: 10px; color: #666; font-size: 14px;">Try these examples:</div>
            <span class="example-button" data-message="Should I bring umbrella in New York tonight?">🌧️ Umbrella in NYC?</span>
            <span class="example-button" data-message="What should I wear in Houston today?">👕 What to wear in Houston?</span>
            <span class="example-button" data-message="Is it good weather for hiking in Seattle?">🥾 Hiking in Seattle?</span>
            <span class="example-button" data-message="Any storms coming to Texas?">⛈️ Texas storms?</span>
        </div>
        
        <div class="loading" id="loading">
            <span class="typing-indicator">🤖 Thinking...</span>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const chatContainer = document.getElementById('chatContainer');
            const messageInput = document.getElementById('messageInput');
            const sendButton = document.getElementById('sendButton');
            const loading = document.getElementById('loading');
            
            function addMessage(content, isUser = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
                // Convert newlines to <br> tags
                const formattedContent = content.split('\\n').join('<br>');
                messageDiv.innerHTML = formattedContent;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            
            function setLoading(show) {
                loading.style.display = show ? 'block' : 'none';
                sendButton.disabled = show;
                sendButton.textContent = show ? 'Sending...' : 'Send';
            }
            
            async function sendMessage() {
                console.log('Send button clicked');
                const message = messageInput.value.trim();
                console.log('Message:', message);
                
                if (!message) {
                    console.log('Empty message, returning');
                    return;
                }
                
                // Add user message
                addMessage(message, true);
                messageInput.value = '';
                
                // Show loading
                setLoading(true);
                
                try {
                    console.log('Sending request to /chat');
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({message: message})
                    });
                    
                    console.log('Response status:', response.status);
                    const data = await response.json();
                    console.log('Response data:', data);
                    
                    if (data.success) {
                        addMessage(data.response);
                    } else {
                        addMessage('❌ Sorry, something went wrong: ' + (data.error || 'Unknown error'));
                    }
                } catch (error) {
                    console.error('Fetch error:', error);
                    addMessage('❌ Connection error. Please try again.');
                } finally {
                    setLoading(false);
                }
            }
            
            function setMessage(text) {
                messageInput.value = text;
                messageInput.focus();
            }
            
            // Event listeners
            sendButton.addEventListener('click', sendMessage);
            
            messageInput.addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Example buttons
            document.querySelectorAll('.example-button').forEach(button => {
                button.addEventListener('click', function() {
                    const message = this.getAttribute('data-message');
                    setMessage(message);
                });
            });
            
            // Focus input
            messageInput.focus();
        });
    </script>
</body>
</html>
    """

@app.post("/chat")
async def chat(request: Request):
    """Handle chat requests"""
    try:
        print("📥 Received chat request")
        data = await request.json()
        message = data.get("message", "").strip()
        print(f"📝 Message: {message}")
        
        if not message:
            print("❌ Empty message")
            return {"success": False, "error": "Empty message"}
        
        if not gemini_client:
            print("❌ Gemini client not ready")
            return {"success": False, "error": "Weather service not initialized. Please wait and try again."}
        
        print("🤖 Processing with Gemini...")
        # Get response from Gemini
        response = await gemini_client.chat_with_weather(message)
        print(f"✅ Response ready: {response[:100]}...")
        
        return {"success": True, "response": response}
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = "healthy" if gemini_client else "not_ready"
    api_key_status = "found" if os.getenv('GOOGLE_AI_API_KEY') else "missing"
    return {
        "status": status, 
        "service": "Gemini Weather Assistant",
        "api_key": api_key_status,
        "client_ready": gemini_client is not None
    }

@app.post("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"success": True, "message": "Test successful!"}

if __name__ == "__main__":
    import uvicorn
    
    # Check API key
    if not os.getenv('GOOGLE_AI_API_KEY'):
        print("❌ Please set GOOGLE_AI_API_KEY in .env file or environment variable")
        print("📋 Get your API key from: https://aistudio.google.com/app/apikey")
        exit(1)
    
    print("🚀 Starting Gemini Weather Web App...")
    print("🌐 Web interface will be available at: http://localhost:8000")
    print("🤖 Powered by Gemini AI + MCP Weather Data")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
