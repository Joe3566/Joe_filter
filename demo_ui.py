#!/usr/bin/env python3
"""
Auto-Opening Demo Web Interface for LLM Compliance Filter
This version automatically opens in your default browser
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import webbrowser
import threading
import time
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Simple demo statistics
stats = {
    'total_checks': 0,
    'allow': 0,
    'warn': 0,
    'block': 0,
    'recent': []
}

# Try to load the real compliance filter
FILTER_WORKING = False
compliance_filter = None

def load_compliance_filter():
    """Try to load the compliance filter"""
    global compliance_filter, FILTER_WORKING
    try:
        from src.compliance_filter import ComplianceFilter
        compliance_filter = ComplianceFilter()
        FILTER_WORKING = True
        print("✅ Real compliance filter loaded successfully!")
        return True
    except Exception as e:
        print(f"⚠️ Using demo mode (couldn't load filter: {e})")
        return False

# HTML content with embedded styles and JavaScript
HTML_CONTENT = '''<!DOCTYPE html>
<html>
<head>
    <title>🛡️ LLM Compliance Filter Demo</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px; 
        }
        .container { 
            max-width: 1000px; margin: 0 auto; background: white; 
            border-radius: 20px; overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3); 
        }
        .header { 
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white; padding: 40px; text-align: center; 
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .status-badge { 
            display: inline-block; margin-top: 15px; padding: 8px 20px;
            border-radius: 25px; font-weight: bold;
            background: FILTER_STATUS_COLOR; color: white;
        }
        .content { padding: 40px; }
        
        /* Statistics Grid */
        .stats { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); 
            gap: 20px; margin-bottom: 40px; 
        }
        .stat { 
            background: linear-gradient(135deg, #3498db, #2ecc71);
            color: white; padding: 30px; text-align: center; border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .stat:hover { transform: translateY(-5px); }
        .stat-number { font-size: 3em; font-weight: bold; margin-bottom: 10px; }
        .stat-label { font-size: 1em; opacity: 0.9; }
        
        /* Form Styling */
        .form-section { 
            background: #f8f9fa; padding: 30px; border-radius: 15px; margin-bottom: 30px;
        }
        .form-group { margin-bottom: 25px; }
        label { 
            display: block; margin-bottom: 10px; font-weight: 600; 
            color: #2c3e50; font-size: 1.1em;
        }
        textarea { 
            width: 100%; padding: 15px; border: 2px solid #ddd; 
            border-radius: 10px; font-size: 16px; font-family: inherit;
            transition: border-color 0.3s ease; resize: vertical;
        }
        textarea:focus { 
            outline: none; border-color: #3498db; 
            box-shadow: 0 0 10px rgba(52, 152, 219, 0.2);
        }
        
        /* Buttons */
        .btn { 
            display: inline-block; padding: 15px 30px; border: none; 
            border-radius: 10px; font-size: 16px; font-weight: 600;
            cursor: pointer; margin: 5px; text-decoration: none;
            transition: all 0.3s ease;
        }
        .btn-primary { 
            background: linear-gradient(135deg, #3498db, #2980b9); 
            color: white; 
        }
        .btn-primary:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
        }
        .btn-success { 
            background: linear-gradient(135deg, #27ae60, #229954); 
            color: white; 
        }
        .btn-warning { 
            background: linear-gradient(135deg, #f39c12, #e67e22); 
            color: white; 
        }
        .btn-danger { 
            background: linear-gradient(135deg, #e74c3c, #c0392b); 
            color: white; 
        }
        .btn-secondary { 
            background: linear-gradient(135deg, #95a5a6, #7f8c8d); 
            color: white; 
        }
        
        /* Results */
        .result { 
            margin-top: 30px; padding: 25px; border-radius: 15px; 
            display: none; transition: all 0.5s ease;
        }
        .result.show { display: block; animation: slideIn 0.5s ease; }
        .result.allow { 
            background: linear-gradient(135deg, #d5f4e6, #c8e6d0); 
            border-left: 5px solid #27ae60; 
        }
        .result.warn { 
            background: linear-gradient(135deg, #fef9e7, #f8e8a4); 
            border-left: 5px solid #f39c12; 
        }
        .result.block { 
            background: linear-gradient(135deg, #fadbd8, #f5b7b1); 
            border-left: 5px solid #e74c3c; 
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Examples Section */
        .examples { 
            background: white; padding: 30px; border-radius: 15px; 
            border: 2px solid #ecf0f1; margin-bottom: 30px;
        }
        .examples h3 { 
            color: #2c3e50; margin-bottom: 20px; text-align: center;
        }
        .example-buttons { 
            display: flex; flex-wrap: wrap; justify-content: center; gap: 15px;
        }
        
        /* Recent Activity */
        .recent { 
            background: white; padding: 30px; border-radius: 15px; 
            border: 2px solid #ecf0f1; 
        }
        .recent h3 { color: #2c3e50; margin-bottom: 20px; }
        .recent-item { 
            padding: 15px 0; border-bottom: 1px solid #ecf0f1;
            display: flex; justify-content: space-between; align-items: center;
        }
        .recent-item:last-child { border-bottom: none; }
        .recent-time { font-weight: 600; color: #2c3e50; }
        .recent-text { color: #7f8c8d; margin-top: 5px; }
        .badge { 
            padding: 6px 12px; border-radius: 20px; font-size: 0.8em; 
            font-weight: bold; 
        }
        .badge-allow { background: #d5f4e6; color: #155724; }
        .badge-warn { background: #fef9e7; color: #856404; }
        .badge-block { background: #fadbd8; color: #721c24; }
        
        /* Loading animation */
        .loading { 
            display: inline-block; animation: spin 1s linear infinite; 
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ LLM Compliance Filter</h1>
            <p>Advanced AI-powered content compliance checking</p>
            <div class="status-badge">FILTER_STATUS_TEXT</div>
        </div>
        
        <div class="content">
            <!-- Statistics Dashboard -->
            <div class="stats">
                <div class="stat">
                    <div class="stat-number" id="total">0</div>
                    <div class="stat-label">Total Checks</div>
                </div>
                <div class="stat">
                    <div class="stat-number" id="allow">0</div>
                    <div class="stat-label">✅ Allowed</div>
                </div>
                <div class="stat">
                    <div class="stat-number" id="warn">0</div>
                    <div class="stat-label">⚠️ Warnings</div>
                </div>
                <div class="stat">
                    <div class="stat-number" id="block">0</div>
                    <div class="stat-label">❌ Blocked</div>
                </div>
            </div>
            
            <!-- Content Check Form -->
            <div class="form-section">
                <div class="form-group">
                    <label for="content">📝 Enter text to check for compliance:</label>
                    <textarea id="content" rows="6" 
                        placeholder="Type or paste your content here to check if it complies with safety and privacy guidelines..."></textarea>
                </div>
                
                <button class="btn btn-primary" onclick="checkContent()">
                    🔍 Check Compliance
                </button>
                <button class="btn btn-secondary" onclick="clearForm()">
                    🗑️ Clear
                </button>
                
                <!-- Result Display -->
                <div id="result" class="result">
                    <div id="result-content"></div>
                </div>
            </div>
            
            <!-- Example Buttons -->
            <div class="examples">
                <h3>🎯 Try These Examples</h3>
                <div class="example-buttons">
                    <button class="btn btn-success" onclick="setExample('Hello! How are you doing today? I hope you have a wonderful day.')">
                        ✅ Safe Content
                    </button>
                    <button class="btn btn-warning" onclick="setExample('Please contact me at john.smith@company.com or call me at 555-123-4567 for more information.')">
                        ⚠️ Privacy Risk
                    </button>
                    <button class="btn btn-danger" onclick="setExample('I absolutely hate those stupid people from that country and wish they would disappear.')">
                        ❌ Harmful Content
                    </button>
                </div>
            </div>
            
            <!-- Recent Activity -->
            <div class="recent">
                <h3>📊 Recent Activity</h3>
                <div id="recent-list">
                    <div class="recent-item">
                        <div>
                            <div class="recent-time">Ready to start</div>
                            <div class="recent-text">Try checking some content using the examples above</div>
                        </div>
                        <span class="badge badge-allow">READY</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Set example content
        function setExample(text) {
            document.getElementById('content').value = text;
            // Auto-scroll to form
            document.getElementById('content').scrollIntoView({ behavior: 'smooth', block: 'center' });
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
                alert('👋 Please enter some text to check first!');
                return;
            }
            
            const resultDiv = document.getElementById('result');
            const contentDiv = document.getElementById('result-content');
            
            // Show loading state
            contentDiv.innerHTML = '<p>🔄 <span class="loading">⏳</span> Analyzing content...</p>';
            resultDiv.className = 'result show';
            
            try {
                const response = await fetch('/check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: 'text=' + encodeURIComponent(text)
                });
                
                const result = await response.json();
                
                if (result.error) {
                    contentDiv.innerHTML = '<h3>❌ Error</h3><p>' + result.error + '</p>';
                    resultDiv.className = 'result show block';
                } else {
                    const icons = { 'allow': '✅', 'warn': '⚠️', 'block': '❌' };
                    const messages = {
                        'allow': 'Content is compliant and safe to use.',
                        'warn': 'Content has potential issues that should be reviewed.',
                        'block': 'Content violates compliance guidelines and should not be used.'
                    };
                    
                    contentDiv.innerHTML = `
                        <h3>${icons[result.action]} ${result.action.toUpperCase()}</h3>
                        <p style="font-size: 1.1em; margin: 15px 0;">${messages[result.action]}</p>
                        <p><strong>🎯 Confidence Score:</strong> ${result.score}</p>
                        <p><strong>⏱️ Processing Time:</strong> ${result.processing_time}s</p>
                        <p><strong>🔍 Analysis:</strong> ${result.reasoning}</p>
                    `;
                    
                    resultDiv.className = 'result show ' + result.action;
                    
                    // Update statistics
                    updateStats();
                }
            } catch (error) {
                contentDiv.innerHTML = '<h3>❌ Network Error</h3><p>Could not connect to server: ' + error.message + '</p>';
                resultDiv.className = 'result show block';
            }
        }
        
        // Update statistics display
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
                    recentDiv.innerHTML = data.recent.slice(-5).reverse().map(item => `
                        <div class="recent-item">
                            <div>
                                <div class="recent-time">${item.time}</div>
                                <div class="recent-text">${item.reasoning.substring(0, 60)}${item.reasoning.length > 60 ? '...' : ''}</div>
                            </div>
                            <span class="badge badge-${item.action}">${item.action.toUpperCase()}</span>
                        </div>
                    `).join('');
                } else {
                    recentDiv.innerHTML = `
                        <div class="recent-item">
                            <div>
                                <div class="recent-time">Ready to start</div>
                                <div class="recent-text">Try checking some content using the examples above</div>
                            </div>
                            <span class="badge badge-allow">READY</span>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error updating stats:', error);
            }
        }
        
        // Auto-update stats every 5 seconds
        setInterval(updateStats, 5000);
        
        // Initial load
        updateStats();
        
        // Welcome message
        setTimeout(() => {
            console.log('🛡️ LLM Compliance Filter Demo Ready!');
            console.log('Try the example buttons to see how it works.');
        }, 1000);
    </script>
</body>
</html>'''

class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Replace template variables
            content = HTML_CONTENT
            if FILTER_WORKING:
                content = content.replace('FILTER_STATUS_COLOR', '#27ae60')
                content = content.replace('FILTER_STATUS_TEXT', '✅ AI Filter Active')
            else:
                content = content.replace('FILTER_STATUS_COLOR', '#f39c12')
                content = content.replace('FILTER_STATUS_TEXT', '⚠️ Demo Mode')
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        
        elif self.path == '/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode('utf-8'))
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/check':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                parsed_data = urllib.parse.parse_qs(post_data)
                text = parsed_data.get('text', [''])[0]
                
                if not text.strip():
                    result = {'error': 'Text is required'}
                else:
                    result = perform_compliance_check(text)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                error_result = {'error': f'Server error: {str(e)}'}
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(error_result).encode('utf-8'))
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        # Keep logs minimal
        pass

def perform_compliance_check(text):
    """Perform compliance check with real or demo logic"""
    global stats
    
    start_time = time.time()
    
    try:
        if FILTER_WORKING and compliance_filter:
            # Use real AI compliance filter
            result = compliance_filter.check_compliance(text)
            response = {
                'action': result.action.value,
                'score': round(result.overall_score, 3),
                'processing_time': round(time.time() - start_time, 3),
                'reasoning': result.reasoning
            }
        else:
            # Demo logic with realistic responses
            text_lower = text.lower()
            
            harmful_words = ['hate', 'stupid', 'kill', 'die', 'murder', 'destroy', 'violence']
            privacy_words = ['email', '@', '.com', 'phone', '555-', 'call', 'ssn', 'social security']
            
            if any(word in text_lower for word in harmful_words):
                action = 'block'
                score = 0.87
                reasoning = "Content contains potentially harmful or offensive language that violates safety guidelines."
            elif any(word in text_lower for word in privacy_words):
                action = 'warn'
                score = 0.64
                reasoning = "Content may contain personally identifiable information (PII) that could pose privacy risks."
            else:
                action = 'allow'
                score = 0.12
                reasoning = "Content appears to be safe and compliant with guidelines."
            
            # Add realistic processing delay
            time.sleep(0.1)
            
            response = {
                'action': action,
                'score': score,
                'processing_time': round(time.time() - start_time, 3),
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
        
        # Keep only recent items
        if len(stats['recent']) > 10:
            stats['recent'] = stats['recent'][-10:]
        
        return response
        
    except Exception as e:
        return {'error': f'Processing error: {str(e)}'}

def open_browser(url, delay=2):
    """Open browser after a short delay"""
    time.sleep(delay)
    try:
        webbrowser.open(url)
        print(f"🌐 Opened browser to {url}")
    except Exception as e:
        print(f"⚠️ Could not auto-open browser: {e}")
        print(f"📍 Please manually open: {url}")

def run_demo_server(port=5000):
    """Run the demo server"""
    server_address = ('127.0.0.1', port)
    
    try:
        httpd = HTTPServer(server_address, DemoHandler)
        url = f"http://127.0.0.1:{port}"
        
        print(f"✅ Demo server starting on {url}")
        print("🚀 Auto-opening browser in 2 seconds...")
        print("🛑 Press Ctrl+C to stop")
        print()
        
        # Open browser in background thread
        threading.Thread(target=open_browser, args=(url,), daemon=True).start()
        
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
        httpd.shutdown()
    except OSError as e:
        if e.errno == 10048:  # Port in use
            print(f"❌ Port {port} is busy, trying {port + 1}...")
            run_demo_server(port + 1)
        else:
            print(f"❌ Server error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == '__main__':
    print("🎭 LLM Compliance Filter - Interactive Demo")
    print("=" * 50)
    
    # Try to load the real filter
    load_compliance_filter()
    
    print(f"📊 Mode: {'✅ AI-Powered' if FILTER_WORKING else '⚠️ Demo Simulation'}")
    print("🔧 Using built-in Python HTTP server")
    print("🌐 Will auto-open in your default browser")
    print()
    
    run_demo_server()