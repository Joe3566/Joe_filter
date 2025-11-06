#!/usr/bin/env python3
"""
Minimal Working Web Interface for LLM Compliance Filter
Ultra-simple version guaranteed to work on Windows
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import sys
import os
from pathlib import Path
import time

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Try to load compliance filter
try:
    from src.compliance_filter import ComplianceFilter
    compliance_filter = ComplianceFilter()
    FILTER_WORKING = True
    print("✅ Compliance filter loaded successfully")
except Exception as e:
    print(f"⚠️ Compliance filter error: {e}")
    print("🔄 Will use demo mode")
    compliance_filter = None
    FILTER_WORKING = False

# Simple statistics
stats = {
    'total_checks': 0,
    'allow': 0,
    'warn': 0,
    'block': 0,
    'recent': []
}

# HTML page content
HTML_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Compliance Filter</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 900px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            padding: 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header { 
            background: #2c3e50; 
            color: white; 
            padding: 30px; 
            text-align: center; 
        }
        .content { 
            padding: 30px; 
        }
        .stats { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); 
            gap: 15px; 
            margin-bottom: 30px; 
        }
        .stat { 
            background: linear-gradient(135deg, #3498db, #2ecc71); 
            color: white; 
            padding: 20px; 
            text-align: center; 
            border-radius: 10px; 
        }
        .stat-number { 
            font-size: 2em; 
            font-weight: bold; 
            margin-bottom: 5px; 
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: bold; 
        }
        textarea, input, select { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 8px; 
            font-size: 16px; 
            box-sizing: border-box;
        }
        textarea:focus, input:focus, select:focus { 
            outline: none; 
            border-color: #3498db; 
        }
        .btn { 
            background: #3498db; 
            color: white; 
            border: none; 
            padding: 12px 24px; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 16px; 
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .btn:hover { 
            background: #2980b9; 
        }
        .btn-success { background: #27ae60; }
        .btn-success:hover { background: #229954; }
        .btn-warning { background: #f39c12; }
        .btn-warning:hover { background: #e67e22; }
        .btn-danger { background: #e74c3c; }
        .btn-danger:hover { background: #c0392b; }
        .result { 
            margin-top: 20px; 
            padding: 20px; 
            border-radius: 10px; 
            display: none; 
        }
        .result.show { display: block; }
        .result.allow { background: #d5f4e6; border-left: 5px solid #27ae60; }
        .result.warn { background: #fef9e7; border-left: 5px solid #f39c12; }
        .result.block { background: #fadbd8; border-left: 5px solid #e74c3c; }
        .status { 
            color: #27ae60; 
            font-weight: bold; 
        }
        .examples { 
            margin-top: 20px; 
            padding: 20px; 
            background: #f8f9fa; 
            border-radius: 10px; 
        }
        .recent { 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 10px; 
            margin-top: 20px; 
        }
        .recent-item { 
            padding: 10px 0; 
            border-bottom: 1px solid #dee2e6; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
        }
        .recent-item:last-child { border-bottom: none; }
        .badge { 
            padding: 4px 8px; 
            border-radius: 4px; 
            font-size: 0.8em; 
            font-weight: bold; 
        }
        .badge-allow { background: #d5f4e6; color: #155724; }
        .badge-warn { background: #fef9e7; color: #856404; }
        .badge-block { background: #fadbd8; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ LLM Compliance Filter</h1>
            <p>Content compliance checking and monitoring</p>
            <p class="status">Status: ''' + ('✅ Active' if FILTER_WORKING else '⚠️ Demo Mode') + '''</p>
        </div>
        
        <div class="content">
            <!-- Statistics -->
            <div class="stats">
                <div class="stat">
                    <div class="stat-number" id="total">0</div>
                    <div>Total Checks</div>
                </div>
                <div class="stat">
                    <div class="stat-number" id="allow">0</div>
                    <div>Allowed</div>
                </div>
                <div class="stat">
                    <div class="stat-number" id="warn">0</div>
                    <div>Warnings</div>
                </div>
                <div class="stat">
                    <div class="stat-number" id="block">0</div>
                    <div>Blocked</div>
                </div>
            </div>
            
            <!-- Content Check Form -->
            <div class="form-group">
                <label for="content">Enter text to check for compliance:</label>
                <textarea id="content" rows="6" placeholder="Type or paste your content here..."></textarea>
            </div>
            
            <button class="btn" onclick="checkContent()">🔍 Check Compliance</button>
            <button class="btn btn-warning" onclick="clearForm()">🗑️ Clear</button>
            
            <!-- Result Display -->
            <div id="result" class="result">
                <div id="result-content"></div>
            </div>
            
            <!-- Example Buttons -->
            <div class="examples">
                <h3>Try These Examples:</h3>
                <button class="btn btn-success" onclick="setExample('Hello, how are you today? This is a nice safe message.')">✅ Safe Content</button>
                <button class="btn btn-warning" onclick="setExample('My email is john@example.com and my phone number is 555-1234')">⚠️ Privacy Risk</button>
                <button class="btn btn-danger" onclick="setExample('I hate those stupid people from that country')">❌ Harmful Content</button>
            </div>
            
            <!-- Recent Activity -->
            <div class="recent">
                <h3>Recent Activity</h3>
                <div id="recent-list">
                    <div class="recent-item">
                        <div>No checks performed yet</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Set example content
        function setExample(text) {
            document.getElementById('content').value = text;
        }
        
        // Clear form
        function clearForm() {
            document.getElementById('content').value = '';
            document.getElementById('result').classList.remove('show');
        }
        
        // Check content compliance
        async function checkContent() {
            const text = document.getElementById('content').value.trim();
            if (!text) {
                alert('Please enter some text to check.');
                return;
            }
            
            const resultDiv = document.getElementById('result');
            const contentDiv = document.getElementById('result-content');
            
            // Show loading
            contentDiv.innerHTML = '<p>🔄 Checking compliance...</p>';
            resultDiv.className = 'result show';
            
            try {
                const response = await fetch('/check', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: 'text=' + encodeURIComponent(text)
                });
                
                const result = await response.json();
                
                if (result.error) {
                    contentDiv.innerHTML = '<p>❌ Error: ' + result.error + '</p>';
                    resultDiv.className = 'result show block';
                } else {
                    const icons = {
                        'allow': '✅',
                        'warn': '⚠️', 
                        'block': '❌'
                    };
                    
                    contentDiv.innerHTML = 
                        '<h3>' + icons[result.action] + ' ' + result.action.toUpperCase() + '</h3>' +
                        '<p><strong>Score:</strong> ' + result.score + '</p>' +
                        '<p><strong>Processing Time:</strong> ' + result.processing_time + 's</p>' +
                        '<p><strong>Reasoning:</strong> ' + result.reasoning + '</p>';
                    
                    resultDiv.className = 'result show ' + result.action;
                    
                    // Update stats
                    updateStats();
                }
            } catch (error) {
                contentDiv.innerHTML = '<p>❌ Network Error: ' + error.message + '</p>';
                resultDiv.className = 'result show block';
            }
        }
        
        // Update statistics
        async function updateStats() {
            try {
                const response = await fetch('/stats');
                const data = await response.json();
                
                document.getElementById('total').textContent = data.total_checks;
                document.getElementById('allow').textContent = data.allow;
                document.getElementById('warn').textContent = data.warn;
                document.getElementById('block').textContent = data.block;
                
                // Update recent activity
                const recentDiv = document.getElementById('recent-list');
                if (data.recent && data.recent.length > 0) {
                    recentDiv.innerHTML = data.recent.slice(-5).reverse().map(item => 
                        '<div class="recent-item">' +
                        '<div><strong>' + item.time + '</strong><br>' + item.reasoning.substring(0, 50) + '...</div>' +
                        '<span class="badge badge-' + item.action + '">' + item.action.toUpperCase() + '</span>' +
                        '</div>'
                    ).join('');
                }
            } catch (error) {
                console.error('Error updating stats:', error);
            }
        }
        
        // Auto-update stats every 5 seconds
        setInterval(updateStats, 5000);
        
        // Initial stats load
        updateStats();
    </script>
</body>
</html>'''

class ComplianceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Serve main page
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        
        elif self.path == '/stats':
            # Serve statistics
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode('utf-8'))
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/check':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Parse form data
            parsed_data = urllib.parse.parse_qs(post_data)
            text = parsed_data.get('text', [''])[0]
            
            if not text.strip():
                result = {'error': 'Text is required'}
            else:
                result = check_compliance_simple(text)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        # Suppress default logging to keep output clean
        pass

def check_compliance_simple(text):
    """Simple compliance checking function"""
    global stats
    
    start_time = time.time()
    
    try:
        if FILTER_WORKING and compliance_filter:
            # Use real compliance filter
            result = compliance_filter.check_compliance(text)
            response = {
                'action': result.action.value,
                'score': round(result.overall_score, 3),
                'processing_time': round(time.time() - start_time, 3),
                'reasoning': result.reasoning
            }
        else:
            # Simple mock logic for demo
            text_lower = text.lower()
            
            if any(word in text_lower for word in ['hate', 'stupid', 'kill', 'die', 'murder']):
                action = 'block'
                score = 0.85
                reasoning = "Content contains potentially harmful language."
            elif any(word in text_lower for word in ['email', '@', '.com', 'phone', '555-', 'call']):
                action = 'warn'
                score = 0.65
                reasoning = "Content may contain privacy-sensitive information."
            else:
                action = 'allow'
                score = 0.15
                reasoning = "Content appears safe and compliant."
            
            response = {
                'action': action,
                'score': score,
                'processing_time': round(time.time() - start_time + 0.1, 3),
                'reasoning': reasoning
            }
        
        # Update statistics
        stats['total_checks'] += 1
        stats[response['action']] += 1
        stats['recent'].append({
            'action': response['action'],
            'reasoning': response['reasoning'],
            'time': time.strftime('%H:%M:%S'),
            'score': response['score']
        })
        
        # Keep only last 20 items
        if len(stats['recent']) > 20:
            stats['recent'] = stats['recent'][-20:]
        
        return response
        
    except Exception as e:
        return {'error': f'Processing error: {str(e)}'}

def run_server(port=5000):
    """Run the HTTP server"""
    server_address = ('127.0.0.1', port)
    
    try:
        httpd = HTTPServer(server_address, ComplianceHandler)
        print(f"✅ Server starting on http://127.0.0.1:{port}")
        print("🌐 Open your browser to http://127.0.0.1:5000")
        print("🛑 Press Ctrl+C to stop the server")
        print()
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        httpd.shutdown()
    except OSError as e:
        if e.errno == 10048:  # Address already in use
            print(f"❌ Port {port} is already in use")
            print("🔧 Trying alternative port...")
            run_server(port + 1)
        else:
            print(f"❌ Server error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == '__main__':
    print("🚀 Starting Minimal Compliance Filter Web Interface")
    print("=" * 55)
    print(f"📊 Filter Status: {'✅ Active' if FILTER_WORKING else '⚠️ Demo Mode'}")
    print("🔧 Using Python's built-in HTTP server (no Flask required)")
    print()
    
    run_server()