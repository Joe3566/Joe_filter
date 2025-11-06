#!/usr/bin/env python3
"""
Lightweight Web Interface for LLM Compliance Filter
Simplified version without heavy dependencies for quick testing
"""

from flask import Flask, render_template_string, request, jsonify
import sys
import os
from pathlib import Path
import time
import json
from datetime import datetime

app = Flask(__name__)

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Global variables for statistics
stats = {
    'total_checks': 0,
    'actions': {'allow': 0, 'warn': 0, 'block': 0},
    'recent_checks': []
}

# Try to import compliance filter, fallback to mock if not available
try:
    from src.compliance_filter import ComplianceFilter
    compliance_filter = ComplianceFilter()
    FILTER_AVAILABLE = True
    print("✅ Compliance filter loaded successfully")
except Exception as e:
    print(f"⚠️ Could not load compliance filter: {e}")
    print("🔄 Running in demo mode with mock responses")
    compliance_filter = None
    FILTER_AVAILABLE = False

# HTML template embedded in Python
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Compliance Filter</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .nav { 
            display: flex; 
            background: #34495e; 
            justify-content: center;
        }
        .nav button { 
            background: none; 
            border: none; 
            color: white; 
            padding: 15px 30px; 
            cursor: pointer; 
            transition: background 0.3s;
            border-bottom: 3px solid transparent;
        }
        .nav button:hover { background: rgba(255,255,255,0.1); }
        .nav button.active { 
            background: rgba(255,255,255,0.1); 
            border-bottom-color: #3498db;
        }
        .content { padding: 30px; min-height: 500px; }
        .page { display: none; }
        .page.active { display: block; }
        
        /* Dashboard styles */
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { 
            background: linear-gradient(135deg, #3498db, #2ecc71);
            color: white; 
            padding: 25px; 
            border-radius: 10px; 
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .stat-number { font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }
        .stat-label { font-size: 0.9em; opacity: 0.9; }
        
        /* Form styles */
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; }
        textarea, input, select { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 8px; 
            font-size: 16px;
            transition: border-color 0.3s;
        }
        textarea:focus, input:focus, select:focus { 
            outline: none; 
            border-color: #3498db; 
        }
        .btn { 
            background: linear-gradient(135deg, #3498db, #2ecc71);
            color: white; 
            border: none; 
            padding: 12px 24px; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 16px;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn-secondary { background: linear-gradient(135deg, #95a5a6, #7f8c8d); }
        
        /* Results styles */
        .result { 
            margin-top: 20px; 
            padding: 20px; 
            border-radius: 10px; 
            display: none;
        }
        .result.show { display: block; }
        .result.allow { background: #d4edda; border-left: 5px solid #28a745; }
        .result.warn { background: #fff3cd; border-left: 5px solid #ffc107; }
        .result.block { background: #f8d7da; border-left: 5px solid #dc3545; }
        
        .activity-list { background: #f8f9fa; padding: 20px; border-radius: 10px; }
        .activity-item { 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            padding: 10px 0; 
            border-bottom: 1px solid #dee2e6;
        }
        .activity-item:last-child { border-bottom: none; }
        .status-badge { 
            padding: 4px 12px; 
            border-radius: 20px; 
            font-size: 0.8em; 
            font-weight: bold;
        }
        .status-allow { background: #d4edda; color: #155724; }
        .status-warn { background: #fff3cd; color: #856404; }
        .status-block { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ LLM Compliance Filter</h1>
            <p>Advanced content compliance checking and monitoring</p>
            {% if not filter_available %}
            <p style="color: #ffc107;">⚠️ Running in Demo Mode</p>
            {% endif %}
        </div>
        
        <div class="nav">
            <button onclick="showPage('dashboard')" class="active">📊 Dashboard</button>
            <button onclick="showPage('check')">🔍 Check Content</button>
            <button onclick="showPage('settings')">⚙️ Settings</button>
        </div>
        
        <div class="content">
            <!-- Dashboard Page -->
            <div id="dashboard" class="page active">
                <h2>Dashboard</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="total-checks">{{ stats.total_checks }}</div>
                        <div class="stat-label">Total Checks</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="allowed-count">{{ stats.actions.allow }}</div>
                        <div class="stat-label">Allowed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="warning-count">{{ stats.actions.warn }}</div>
                        <div class="stat-label">Warnings</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="blocked-count">{{ stats.actions.block }}</div>
                        <div class="stat-label">Blocked</div>
                    </div>
                </div>
                
                <h3>Recent Activity</h3>
                <div class="activity-list" id="activity-list">
                    {% if stats.recent_checks %}
                        {% for check in stats.recent_checks[-10:] %}
                        <div class="activity-item">
                            <div>
                                <strong>{{ check.timestamp }}</strong><br>
                                <small>{{ check.reasoning[:50] }}...</small>
                            </div>
                            <span class="status-badge status-{{ check.action }}">{{ check.action.upper() }}</span>
                        </div>
                        {% endfor %}
                    {% else %}
                        <div class="activity-item">
                            <div>No activity yet. Try checking some content!</div>
                        </div>
                    {% endif %}
                </div>
            </div>
            
            <!-- Check Content Page -->
            <div id="check" class="page">
                <h2>Check Content Compliance</h2>
                <div class="form-group">
                    <label for="content-text">Enter text to check:</label>
                    <textarea id="content-text" rows="6" placeholder="Type or paste the content you want to check for compliance..."></textarea>
                </div>
                <button class="btn" onclick="checkCompliance()">🔍 Check Compliance</button>
                <button class="btn btn-secondary" onclick="clearCheck()">🗑️ Clear</button>
                
                <div id="check-result" class="result">
                    <div id="result-content"></div>
                </div>
                
                <div style="margin-top: 30px;">
                    <h3>Try These Examples:</h3>
                    <button class="btn btn-secondary" onclick="setExample('Hello, how are you today? This is perfectly safe content.')">✅ Safe Content</button>
                    <button class="btn btn-secondary" onclick="setExample('Contact me at john.doe@email.com or call 555-123-4567')">⚠️ Privacy Risk</button>
                    <button class="btn btn-secondary" onclick="setExample('I hate everyone from that stupid country')">❌ Harmful Content</button>
                </div>
            </div>
            
            <!-- Settings Page -->
            <div id="settings" class="page">
                <h2>Settings & Configuration</h2>
                <div class="form-group">
                    <label>Detection Sensitivity:</label>
                    <select id="sensitivity">
                        <option value="low">Low (Lenient)</option>
                        <option value="medium" selected>Medium (Balanced)</option>
                        <option value="high">High (Strict)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="enable-logging" checked> Enable detailed logging
                    </label>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="enable-caching" checked> Cache results for better performance
                    </label>
                </div>
                <button class="btn" onclick="saveSettings()">💾 Save Settings</button>
                
                <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                    <h3>System Information</h3>
                    <p><strong>Filter Status:</strong> {% if filter_available %}✅ Active{% else %}⚠️ Demo Mode{% endif %}</p>
                    <p><strong>Version:</strong> 1.0.0</p>
                    <p><strong>Last Updated:</strong> <span id="last-updated">{{ current_time }}</span></p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Page navigation
        function showPage(pageId) {
            // Hide all pages
            document.querySelectorAll('.page').forEach(page => {
                page.classList.remove('active');
            });
            
            // Remove active class from all nav buttons
            document.querySelectorAll('.nav button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected page
            document.getElementById(pageId).classList.add('active');
            
            // Activate corresponding nav button
            event.target.classList.add('active');
        }
        
        // Check compliance
        async function checkCompliance() {
            const text = document.getElementById('content-text').value.trim();
            if (!text) {
                alert('Please enter some text to check.');
                return;
            }
            
            const resultDiv = document.getElementById('check-result');
            const contentDiv = document.getElementById('result-content');
            
            contentDiv.innerHTML = '<p>🔄 Checking compliance...</p>';
            resultDiv.className = 'result show';
            
            try {
                const response = await fetch('/api/check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    const actionIcons = {
                        'allow': '✅',
                        'warn': '⚠️',
                        'block': '❌'
                    };
                    
                    contentDiv.innerHTML = `
                        <h3>${actionIcons[result.action]} ${result.action.toUpperCase()}</h3>
                        <p><strong>Overall Score:</strong> ${result.overall_score}</p>
                        <p><strong>Processing Time:</strong> ${result.processing_time}s</p>
                        <p><strong>Reasoning:</strong> ${result.reasoning}</p>
                    `;
                    
                    resultDiv.className = `result show ${result.action}`;
                    
                    // Update dashboard
                    updateDashboard();
                } else {
                    contentDiv.innerHTML = `<p>❌ Error: ${result.error}</p>`;
                    resultDiv.className = 'result show block';
                }
            } catch (error) {
                contentDiv.innerHTML = `<p>❌ Network Error: ${error.message}</p>`;
                resultDiv.className = 'result show block';
            }
        }
        
        // Set example text
        function setExample(text) {
            document.getElementById('content-text').value = text;
        }
        
        // Clear check
        function clearCheck() {
            document.getElementById('content-text').value = '';
            document.getElementById('check-result').classList.remove('show');
        }
        
        // Save settings
        function saveSettings() {
            alert('Settings saved successfully!');
        }
        
        // Update dashboard
        async function updateDashboard() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('total-checks').textContent = stats.total_checks || 0;
                document.getElementById('allowed-count').textContent = stats.actions.allow || 0;
                document.getElementById('warning-count').textContent = stats.actions.warn || 0;
                document.getElementById('blocked-count').textContent = stats.actions.block || 0;
            } catch (error) {
                console.error('Error updating dashboard:', error);
            }
        }
        
        // Update dashboard every 5 seconds
        setInterval(updateDashboard, 5000);
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(HTML_TEMPLATE, 
                                stats=stats, 
                                filter_available=FILTER_AVAILABLE,
                                current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/api/check', methods=['POST'])
def api_check():
    """API endpoint for compliance checking"""
    global stats
    
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        start_time = time.time()
        
        if FILTER_AVAILABLE and compliance_filter:
            # Use real compliance filter
            result = compliance_filter.check_compliance(text)
            response = {
                'action': result.action.value,
                'overall_score': round(result.overall_score, 3),
                'processing_time': round(time.time() - start_time, 3),
                'reasoning': result.reasoning,
                'timestamp': datetime.now().isoformat()
            }
        else:
            # Mock response for demo mode
            processing_time = time.time() - start_time + 0.1  # Add slight delay
            
            # Simple mock logic
            if any(word in text.lower() for word in ['hate', 'stupid', 'kill', 'die']):
                action = 'block'
                score = 0.85
                reasoning = "Content contains potentially harmful language."
            elif any(word in text.lower() for word in ['email', '@', '.com', 'phone', '555-', 'call me']):
                action = 'warn'
                score = 0.65
                reasoning = "Content may contain privacy-sensitive information."
            else:
                action = 'allow'
                score = 0.15
                reasoning = "Content appears safe and compliant."
            
            response = {
                'action': action,
                'overall_score': score,
                'processing_time': round(processing_time, 3),
                'reasoning': reasoning,
                'timestamp': datetime.now().isoformat()
            }
        
        # Update statistics
        stats['total_checks'] += 1
        stats['actions'][response['action']] += 1
        stats['recent_checks'].append({
            'action': response['action'],
            'score': response['overall_score'],
            'reasoning': response['reasoning'],
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'processing_time': response['processing_time']
        })
        
        # Keep only last 50 checks
        if len(stats['recent_checks']) > 50:
            stats['recent_checks'] = stats['recent_checks'][-50:]
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """Get current statistics"""
    return jsonify(stats)

if __name__ == '__main__':
    print("🚀 Starting Simplified Compliance Filter Web Interface")
    print("=" * 60)
    print(f"📊 Filter Status: {'✅ Active' if FILTER_AVAILABLE else '⚠️ Demo Mode'}")
    print("📍 Web Interface: http://127.0.0.1:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("🔧 Trying alternative port 5001...")
        try:
            print("📍 Alternative URL: http://127.0.0.1:5001")
            app.run(host='127.0.0.1', port=5001, debug=False)
        except Exception as e2:
            print(f"❌ Alternative port failed: {e2}")
            print("💡 Check if Flask is installed: pip install Flask")