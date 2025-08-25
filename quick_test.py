#!/usr/bin/env python3
"""
Quick test web app
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
    <h1>🌤️ Weather Test</h1>
    <button onclick="testSend()">Test Send</button>
    <div id="result"></div>
    
    <script>
        async function testSend() {
            console.log('Button clicked!');
            document.getElementById('result').innerHTML = 'Button works!';
            
            try {
                const response = await fetch('/test', {method: 'POST'});
                const data = await response.json();
                document.getElementById('result').innerHTML = 'API works: ' + data.message;
            } catch (error) {
                document.getElementById('result').innerHTML = 'Error: ' + error;
                console.error('Error:', error);
            }
        }
    </script>
</body>
</html>
    """

@app.post("/test")
async def test():
    return {"message": "API is working!"}

if __name__ == "__main__":
    import uvicorn
    print("🧪 Test app starting at http://localhost:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)
