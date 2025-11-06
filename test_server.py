#!/usr/bin/env python3
"""
Simple test server to verify Flask is working
"""

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Simple HTML template embedded in code
SIMPLE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Test Server</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .success { color: #28a745; font-size: 24px; margin-bottom: 20px; }
        .info { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 10px 0; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
        button:hover { background: #0056b3; }
        #result { margin-top: 20px; padding: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="success">✅ Flask Server is Working!</div>
        
        <div class="info">
            <strong>Server Status:</strong> Running successfully<br>
            <strong>Host:</strong> 127.0.0.1<br>
            <strong>Port:</strong> 5000<br>
            <strong>Time:</strong> <span id="current-time">Loading...</span>
        </div>
        
        <h3>Test API Connection:</h3>
        <button onclick="testAPI()">Test API Endpoint</button>
        <button onclick="location.reload()">Refresh Page</button>
        
        <div id="result"></div>
        
        <h3>Next Steps:</h3>
        <p>If you can see this page, Flask is working correctly. You can now try the full compliance filter interface.</p>
        
        <div style="margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
            <h4>Available Endpoints:</h4>
            <ul>
                <li><a href="/test">Test Page</a> (this page)</li>
                <li><a href="/api/status">API Status</a></li>
                <li><a href="/health">Health Check</a></li>
            </ul>
        </div>
    </div>
    
    <script>
        // Update current time
        function updateTime() {
            document.getElementById('current-time').textContent = new Date().toLocaleString();
        }
        updateTime();
        setInterval(updateTime, 1000);
        
        // Test API endpoint
        async function testAPI() {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<p style="color: blue;">Testing API connection...</p>';
            
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                if (response.ok) {
                    resultDiv.innerHTML = `
                        <div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 5px;">
                            <strong>✅ API Test Successful!</strong><br>
                            Status: ${data.status}<br>
                            Message: ${data.message}<br>
                            Timestamp: ${data.timestamp}
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px;">
                            <strong>❌ API Test Failed</strong><br>
                            Error: ${data.error || 'Unknown error'}
                        </div>
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `
                    <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px;">
                        <strong>❌ Network Error</strong><br>
                        Error: ${error.message}
                    </div>
                `;
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
@app.route('/test')
def test_page():
    """Simple test page to verify Flask is working"""
    return render_template_string(SIMPLE_TEMPLATE)

@app.route('/api/status')
def api_status():
    """API endpoint to test connectivity"""
    return jsonify({
        'status': 'success',
        'message': 'Flask server is running correctly',
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'server': 'test_server.py',
        'version': '1.0.0'
    })

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🧪 Starting Test Server...")
    print("📍 Open your browser to: http://127.0.0.1:5000")
    print("📍 Alternative URL: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("🔧 Trying alternative port 5001...")
        try:
            print("📍 Alternative URL: http://127.0.0.1:5001")
            app.run(host='127.0.0.1', port=5001, debug=False)
        except Exception as e2:
            print(f"❌ Alternative port also failed: {e2}")
            print("💡 Try running: pip install Flask")