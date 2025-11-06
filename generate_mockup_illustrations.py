#!/usr/bin/env python3
"""
Generate visual mockup illustrations of the LLM Compliance Filter system.

This script creates an interactive HTML page showcasing the system mockups
with embedded diagrams and real-time simulation data.
"""

import os
import re
import json
import random
import datetime
from pathlib import Path

def generate_mockup_data():
    """Generate realistic mockup data for the system illustration."""
    current_time = datetime.datetime.now()
    
    return {
        'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'system_status': {
            'uptime_percent': 99.97,
            'total_requests_today': random.randint(20000, 30000),
            'current_rps': round(random.uniform(10, 20), 1),
            'avg_response_time': random.randint(60, 80),
            'cache_hit_rate': round(random.uniform(90, 96), 1),
            'error_rate': round(random.uniform(0.1, 0.5), 1),
        },
        'violations_today': {
            'privacy_blocked': random.randint(1000, 1500),
            'hate_speech_blocked': random.randint(50, 150),
            'total_blocks': 0,  # Will calculate below
        },
        'resource_usage': {
            'cpu_percent': random.randint(40, 70),
            'memory_gb': round(random.uniform(2.0, 3.5), 1),
            'memory_total_gb': 8,
            'active_connections': random.randint(70, 120),
            'max_connections': 200,
        },
        'recent_activity': generate_recent_activity(),
    }

def generate_recent_activity():
    """Generate realistic recent activity data."""
    activities = []
    actions = ['ALLOW', 'WARN', 'BLOCK']
    action_weights = [0.7, 0.2, 0.1]  # Most requests are allowed
    
    for i in range(10):
        time_offset = i * 30  # 30 seconds apart
        timestamp = (datetime.datetime.now() - datetime.timedelta(seconds=time_offset))
        
        action = random.choices(actions, weights=action_weights)[0]
        score = generate_score_for_action(action)
        sample_text = generate_sample_text(action)
        
        activities.append({
            'timestamp': timestamp.strftime('%H:%M'),
            'action': action,
            'score': score,
            'text_preview': sample_text,
            'icon': get_action_icon(action),
            'css_class': get_action_css_class(action)
        })
    
    return activities

def generate_score_for_action(action):
    """Generate realistic score based on action."""
    if action == 'ALLOW':
        return round(random.uniform(0.0, 0.3), 2)
    elif action == 'WARN':
        return round(random.uniform(0.4, 0.6), 2)
    else:  # BLOCK
        return round(random.uniform(0.7, 1.0), 2)

def generate_sample_text(action):
    """Generate sample text based on action type."""
    allow_texts = [
        "How does machine learning work?",
        "What's the weather like today?",
        "Can you help me with coding?",
        "Tell me about artificial intelligence",
        "How to improve productivity?",
    ]
    
    warn_texts = [
        "Contact us at support@... (truncated)",
        "Our company phone is... (truncated)", 
        "Visit our website at... (truncated)",
        "Email us for more info... (truncated)",
    ]
    
    block_texts = [
        "Personal information... (blocked)",
        "Inappropriate content... (blocked)",
        "Sensitive data detected... (blocked)",
        "Privacy violation... (blocked)",
    ]
    
    if action == 'ALLOW':
        return random.choice(allow_texts)
    elif action == 'WARN':
        return random.choice(warn_texts)
    else:
        return random.choice(block_texts)

def get_action_icon(action):
    """Get emoji icon for action."""
    icons = {'ALLOW': '✅', 'WARN': '⚠️', 'BLOCK': '🚫'}
    return icons.get(action, '❓')

def get_action_css_class(action):
    """Get CSS class for action styling."""
    classes = {'ALLOW': 'success', 'WARN': 'warning', 'BLOCK': 'danger'}
    return classes.get(action, 'secondary')

def create_interactive_mockup_html(mockup_data):
    """Create interactive HTML mockup illustration."""
    
    # Calculate total blocks
    mockup_data['violations_today']['total_blocks'] = (
        mockup_data['violations_today']['privacy_blocked'] + 
        mockup_data['violations_today']['hate_speech_blocked']
    )
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ LLM Compliance Filter - Live System Mockup</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .main-container {{ background: white; border-radius: 15px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #007bff, #0056b3); color: white; border-radius: 15px 15px 0 0; }}
        .metric-card {{ background: white; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); transition: transform 0.2s; }}
        .metric-card:hover {{ transform: translateY(-5px); }}
        .activity-item {{ background: #f8f9fa; border-left: 4px solid #007bff; transition: all 0.2s; }}
        .activity-item:hover {{ background: #e9ecef; }}
        .status-indicator {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }}
        .status-online {{ background: #28a745; }}
        .status-warning {{ background: #ffc107; }}
        .pulse {{ animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} 100% {{ opacity: 1; }} }}
        .chart-placeholder {{ background: linear-gradient(45deg, #e9ecef, #f8f9fa); border: 2px dashed #6c757d; }}
        .demo-badge {{ position: absolute; top: 10px; right: 10px; background: #dc3545; color: white; padding: 5px 10px; border-radius: 20px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container-fluid p-4">
        <div class="main-container mx-auto" style="max-width: 1400px; position: relative;">
            
            <!-- Demo Badge -->
            <div class="demo-badge">
                <i class="fas fa-flask"></i> LIVE DEMO
            </div>
            
            <!-- Header -->
            <div class="header p-4">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h1 class="mb-2"><i class="fas fa-shield-alt"></i> LLM Compliance Filter</h1>
                        <p class="mb-0">Live System Dashboard - Real-time Monitoring & Analytics</p>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="d-flex align-items-center justify-content-end">
                            <span class="status-indicator status-online pulse"></span>
                            <span>System Online</span>
                        </div>
                        <small>Last updated: {mockup_data['timestamp']}</small>
                    </div>
                </div>
            </div>
            
            <!-- Key Metrics Row -->
            <div class="p-4">
                <h3 class="mb-4"><i class="fas fa-chart-line"></i> Real-Time Performance Metrics</h3>
                <div class="row g-4">
                    <div class="col-md-3">
                        <div class="metric-card p-4 text-center">
                            <div class="display-4 text-primary mb-2">{mockup_data['system_status']['current_rps']}</div>
                            <h5>Requests/Second</h5>
                            <small class="text-success"><i class="fas fa-arrow-up"></i> +12% vs yesterday</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card p-4 text-center">
                            <div class="display-4 text-success mb-2">{mockup_data['system_status']['avg_response_time']}ms</div>
                            <h5>Avg Response Time</h5>
                            <small class="text-success"><i class="fas fa-check"></i> Under SLA (200ms)</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card p-4 text-center">
                            <div class="display-4 text-warning mb-2">{mockup_data['system_status']['cache_hit_rate']}%</div>
                            <h5>Cache Hit Rate</h5>
                            <small class="text-success"><i class="fas fa-rocket"></i> Excellent</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card p-4 text-center">
                            <div class="display-4 text-danger mb-2">{mockup_data['violations_today']['total_blocks']:,}</div>
                            <h5>Blocked Today</h5>
                            <small class="text-info"><i class="fas fa-shield-alt"></i> Protected</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Main Dashboard Content -->
            <div class="row p-4 g-4">
                
                <!-- Live Compliance Check Demo -->
                <div class="col-lg-8">
                    <div class="card h-100">
                        <div class="card-header bg-primary text-white">
                            <h5><i class="fas fa-search"></i> Live Compliance Check Demo</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Enter text to check for compliance violations:</label>
                                <textarea class="form-control" rows="4" id="demo-input" placeholder="Try typing: 'Hi, my email is john@company.com and my phone is (555) 123-4567'">Hi there! My name is John Smith and my email is john.smith@company.com. I work at Acme Corp and my phone number is (555) 123-4567. Please contact me about the confidential medical records for patient ID 12345.</textarea>
                            </div>
                            <button class="btn btn-primary" onclick="runComplianceCheck()">
                                <i class="fas fa-shield-alt"></i> Check Compliance
                            </button>
                            
                            <!-- Results Panel -->
                            <div id="results-panel" class="mt-4" style="display: none;">
                                <div class="alert alert-danger">
                                    <div class="row">
                                        <div class="col-md-2 text-center">
                                            <div class="display-4">🚫</div>
                                            <strong>BLOCK</strong>
                                        </div>
                                        <div class="col-md-10">
                                            <h6>Compliance Analysis Result:</h6>
                                            <div class="row">
                                                <div class="col-md-6">
                                                    <strong>Overall Score:</strong> 0.847 (High Risk)<br>
                                                    <strong>Processing Time:</strong> 134ms<br>
                                                    <strong>Action:</strong> Content Blocked
                                                </div>
                                                <div class="col-md-6">
                                                    <strong>Privacy Score:</strong> 0.891<br>
                                                    <strong>Hate Speech Score:</strong> 0.234<br>
                                                    <strong>Model Used:</strong> toxic-bert-v2.1
                                                </div>
                                            </div>
                                            <hr>
                                            <h6>Violations Detected:</h6>
                                            <ul class="mb-0">
                                                <li><strong>Email Address:</strong> j***@company.com (95% confidence)</li>
                                                <li><strong>Phone Number:</strong> (555) ***-**** (89% confidence)</li>
                                                <li><strong>Medical Reference:</strong> patient ID (76% confidence)</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- System Health -->
                <div class="col-lg-4">
                    <div class="card h-100">
                        <div class="card-header bg-success text-white">
                            <h5><i class="fas fa-heartbeat"></i> System Health</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <div class="d-flex justify-content-between">
                                    <span>CPU Usage</span>
                                    <span>{mockup_data['resource_usage']['cpu_percent']}%</span>
                                </div>
                                <div class="progress">
                                    <div class="progress-bar" style="width: {mockup_data['resource_usage']['cpu_percent']}%"></div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <div class="d-flex justify-content-between">
                                    <span>Memory Usage</span>
                                    <span>{mockup_data['resource_usage']['memory_gb']}GB / {mockup_data['resource_usage']['memory_total_gb']}GB</span>
                                </div>
                                <div class="progress">
                                    <div class="progress-bar bg-warning" style="width: {mockup_data['resource_usage']['memory_gb'] / mockup_data['resource_usage']['memory_total_gb'] * 100}%"></div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <div class="d-flex justify-content-between">
                                    <span>DB Connections</span>
                                    <span>{mockup_data['resource_usage']['active_connections']} / {mockup_data['resource_usage']['max_connections']}</span>
                                </div>
                                <div class="progress">
                                    <div class="progress-bar bg-info" style="width: {mockup_data['resource_usage']['active_connections'] / mockup_data['resource_usage']['max_connections'] * 100}%"></div>
                                </div>
                            </div>
                            
                            <hr>
                            <h6>Service Status:</h6>
                            <div class="row text-center">
                                <div class="col-6">
                                    <div class="text-success">
                                        <i class="fas fa-check-circle fa-2x"></i>
                                        <div>API Gateway</div>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="text-success">
                                        <i class="fas fa-check-circle fa-2x"></i>
                                        <div>Cache Layer</div>
                                    </div>
                                </div>
                                <div class="col-6 mt-2">
                                    <div class="text-success">
                                        <i class="fas fa-check-circle fa-2x"></i>
                                        <div>Database</div>
                                    </div>
                                </div>
                                <div class="col-6 mt-2">
                                    <div class="text-success">
                                        <i class="fas fa-check-circle fa-2x"></i>
                                        <div>ML Models</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Live Activity Feed -->
            <div class="p-4">
                <h4><i class="fas fa-stream"></i> Live Activity Feed</h4>
                <div class="card">
                    <div class="card-body">
                        <div class="row">
"""
    
    # Add recent activity items
    for activity in mockup_data['recent_activity']:
        html_content += f"""
                            <div class="col-md-6 mb-2">
                                <div class="activity-item p-3 rounded border-start border-{activity['css_class']} border-4">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div>
                                            <span class="badge bg-{activity['css_class']}">{activity['icon']} {activity['action']}</span>
                                            <span class="ms-2">Score: {activity['score']}</span>
                                        </div>
                                        <small class="text-muted">{activity['timestamp']}</small>
                                    </div>
                                    <div class="mt-1">
                                        <small class="text-muted">"{activity['text_preview']}"</small>
                                    </div>
                                </div>
                            </div>
        """
    
    html_content += f"""
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Performance Charts -->
            <div class="p-4">
                <h4><i class="fas fa-chart-area"></i> Performance Analytics</h4>
                <div class="row g-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h6><i class="fas fa-clock"></i> Response Time Trends (24h)</h6>
                            </div>
                            <div class="card-body">
                                <div class="chart-placeholder p-4 text-center">
                                    <div class="mb-3">
                                        <i class="fas fa-chart-line fa-3x text-muted"></i>
                                    </div>
                                    <h6>Interactive Chart Placeholder</h6>
                                    <p class="text-muted">In production, this shows real-time response time trends with interactive hover details</p>
                                    <div class="row text-center mt-3">
                                        <div class="col-3">
                                            <div class="text-success">
                                                <strong>Avg</strong><br>
                                                {mockup_data['system_status']['avg_response_time']}ms
                                            </div>
                                        </div>
                                        <div class="col-3">
                                            <div class="text-info">
                                                <strong>P95</strong><br>
                                                145ms
                                            </div>
                                        </div>
                                        <div class="col-3">
                                            <div class="text-warning">
                                                <strong>P99</strong><br>
                                                267ms
                                            </div>
                                        </div>
                                        <div class="col-3">
                                            <div class="text-danger">
                                                <strong>Max</strong><br>
                                                423ms
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h6><i class="fas fa-shield-alt"></i> Compliance Statistics</h6>
                            </div>
                            <div class="card-body">
                                <div class="row text-center">
                                    <div class="col-6">
                                        <div class="metric-card p-3">
                                            <div class="display-6 text-danger">{mockup_data['violations_today']['privacy_blocked']:,}</div>
                                            <h6>Privacy Violations</h6>
                                            <small class="text-muted">Blocked today</small>
                                        </div>
                                    </div>
                                    <div class="col-6">
                                        <div class="metric-card p-3">
                                            <div class="display-6 text-warning">{mockup_data['violations_today']['hate_speech_blocked']:,}</div>
                                            <h6>Hate Speech</h6>
                                            <small class="text-muted">Blocked today</small>
                                        </div>
                                    </div>
                                </div>
                                <hr>
                                <h6>Detection Breakdown:</h6>
                                <div class="row">
                                    <div class="col-6">
                                        <small>• Email: 567 (46%)</small><br>
                                        <small>• Phone: 234 (19%)</small><br>
                                        <small>• SSN: 123 (10%)</small>
                                    </div>
                                    <div class="col-6">
                                        <small>• Credit Cards: 89 (7%)</small><br>
                                        <small>• Medical Info: 156 (13%)</small><br>
                                        <small>• Other: 65 (5%)</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- API Integration Example -->
            <div class="p-4">
                <h4><i class="fas fa-code"></i> API Integration Example</h4>
                <div class="card">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Python SDK Example:</h6>
                                <pre class="bg-dark text-light p-3 rounded"><code>from compliance_filter import ComplianceClient

client = ComplianceClient(api_key="your-key")

result = client.check_compliance(
    text="Contact me at user@example.com",
    user_context={{"user_id": "12345"}}
)

print(f"Action: {{result.action}}")
print(f"Score: {{result.score}}")
</code></pre>
                            </div>
                            <div class="col-md-6">
                                <h6>REST API Response:</h6>
                                <pre class="bg-light p-3 rounded"><code>{{
  "action": "BLOCK",
  "score": 0.847,
  "hate_speech_score": 0.234,
  "privacy_score": 0.891,
  "violations": [
    {{
      "type": "email",
      "confidence": 0.95,
      "text": "user@example.com"
    }}
  ],
  "processing_time": 0.134,
  "timestamp": "2024-09-16T07:15:30Z"
}}
</code></pre>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="p-4 bg-light">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h6>🛡️ LLM Compliance Filter - Production-Ready System</h6>
                        <p class="mb-0 text-muted">
                            Enterprise-grade compliance filtering with 99.9% uptime, sub-100ms response times,
                            and intelligent caching. Protecting {mockup_data['system_status']['total_requests_today']:,}+ requests daily.
                        </p>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="text-success">
                            <i class="fas fa-shield-check fa-2x"></i>
                            <div>System Operational</div>
                            <small>Uptime: {mockup_data['system_status']['uptime_percent']}%</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function runComplianceCheck() {{
            const button = event.target;
            const resultsPanel = document.getElementById('results-panel');
            
            // Show loading state
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            button.disabled = true;
            
            // Simulate API call delay
            setTimeout(() => {{
                resultsPanel.style.display = 'block';
                resultsPanel.scrollIntoView({{ behavior: 'smooth' }});
                
                // Reset button
                button.innerHTML = '<i class="fas fa-shield-alt"></i> Check Compliance';
                button.disabled = false;
            }}, 1500);
        }}
        
        // Auto-refresh data every 30 seconds (in production)
        setInterval(() => {{
            // This would refresh metrics from API
            console.log('Refreshing real-time data...');
        }}, 30000);
        
        // Add some interactive elements
        document.querySelectorAll('.metric-card').forEach(card => {{
            card.addEventListener('click', () => {{
                card.style.transform = 'scale(1.05)';
                setTimeout(() => {{
                    card.style.transform = 'translateY(-5px)';
                }}, 150);
            }});
        }});
    </script>
</body>
</html>
    """
    
    return html_content

def main():
    """Generate the interactive system mockup illustration."""
    print("🎨 Generating Interactive System Mockup Illustration...")
    
    # Generate realistic mockup data
    mockup_data = generate_mockup_data()
    
    # Create interactive HTML
    html_content = create_interactive_mockup_html(mockup_data)
    
    # Save HTML file
    output_file = "system_mockup_illustration.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Generated: {output_file}")
    print(f"📊 System Stats Included:")
    print(f"   • Requests Today: {mockup_data['system_status']['total_requests_today']:,}")
    print(f"   • Current RPS: {mockup_data['system_status']['current_rps']}")
    print(f"   • Cache Hit Rate: {mockup_data['system_status']['cache_hit_rate']}%")
    print(f"   • Violations Blocked: {mockup_data['violations_today']['total_blocks']:,}")
    print(f"\\n🌐 Open {output_file} to see the live system mockup!")
    
    # Try to open the file
    try:
        os.system(f"start {output_file}")
    except:
        pass

if __name__ == "__main__":
    main()
