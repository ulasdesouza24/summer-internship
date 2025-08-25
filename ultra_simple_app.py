#!/usr/bin/env python3
"""
Ultra Simple Weather Web App
"""

from flask import Flask, render_template_string, request, jsonify
from dotenv import load_dotenv
import asyncio
import threading
from gemini_client import GeminiMCPClient
import os

load_dotenv()

app = Flask(__name__)
gemini_client = None

def init_gemini():
    global gemini_client
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def setup():
        global gemini_client
        gemini_client = GeminiMCPClient()
        await gemini_client.connect()
        print("✅ Gemini ready!")
    
    loop.run_until_complete(setup())

# Start Gemini in background
if os.getenv('GOOGLE_AI_API_KEY'):
    threading.Thread(target=init_gemini, daemon=True).start()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Weather Assistant</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        .chat { height: 400px; border: 2px solid #ddd; padding: 20px; overflow-y: auto; background: #f9f9f9; margin-bottom: 20px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 10px; }
        .user { background: #007bff; color: white; margin-left: 100px; }
        .bot { background: #e9ecef; margin-right: 100px; }
        .input-box { display: flex; gap: 10px; }
        input { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 5px; font-size: 16px; }
        button { padding: 12px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .examples span { display: inline-block; margin: 5px; padding: 8px 12px; background: #f8f9fa; border: 1px solid #ddd; border-radius: 20px; cursor: pointer; font-size: 14px; }
        .examples span:hover { background: #007bff; color: white; }
    </style>
</head>
<body>
    <h1>🌤️ Weather Assistant</h1>
    <div class="chat" id="chat">
        <div class="message bot">👋 Hi! Ask me about weather in any US city!</div>
    </div>
    
    <div class="input-box">
        <input type="text" id="input" placeholder="Ask about weather...">
        <button onclick="send()">Send</button>
    </div>
    
    <div class="examples" style="margin-top: 20px;">
        <span onclick="setMsg('Should I bring umbrella in New York?')">🌧️ Umbrella NYC</span>
        <span onclick="setMsg('What to wear in Houston?')">👕 Houston weather</span>
        <span onclick="setMsg('Good weather for hiking in Seattle?')">🥾 Seattle hiking</span>
    </div>

    <script>
        function addMsg(text, isUser) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'message ' + (isUser ? 'user' : 'bot');
            div.textContent = text;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        
        function setMsg(text) {
            document.getElementById('input').value = text;
        }
        
        function send() {
            const input = document.getElementById('input');
            const msg = input.value.trim();
            if (!msg) return;
            
            addMsg(msg, true);
            input.value = '';
            addMsg('🤖 Thinking...', false);
            
            fetch('/ask', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({q: msg})
            })
            .then(r => r.json())
            .then(data => {
                // Remove thinking message
                const messages = document.querySelectorAll('.message');
                messages[messages.length - 1].remove();
                
                addMsg(data.answer || 'Sorry, error occurred', false);
            })
            .catch(e => {
                const messages = document.querySelectorAll('.message');
                messages[messages.length - 1].remove();
                addMsg('Connection error', false);
            });
        }
        
        // Enter key
        document.getElementById('input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') send();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        question = data.get('q', '').strip()
        
        if not gemini_client:
            return jsonify({'answer': '⏳ Starting up... please wait and try again in a moment.'})
        
        # Get answer
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        answer = loop.run_until_complete(gemini_client.chat_with_weather(question))
        loop.close()
        
        return jsonify({'answer': answer})
        
    except Exception as e:
        return jsonify({'answer': f'Error: {str(e)}'})

if __name__ == '__main__':
    if not os.getenv('GOOGLE_AI_API_KEY'):
        print("❌ Set GOOGLE_AI_API_KEY first!")
        exit(1)
    
    print("🚀 Ultra Simple Weather App")
    print("📱 Open: http://localhost:3000")
    app.run(host='127.0.0.1', port=3000, debug=False)
