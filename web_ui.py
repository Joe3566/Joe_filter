#!/usr/bin/env python3
"""
Web-based User Interface for LLM Compliance Filter

A comprehensive web dashboard for managing, monitoring, and using the compliance filter.
Features:
- Real-time compliance checking
- Analytics and reporting
- Configuration management  
- Training data management
- Performance monitoring
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time
import logging
from typing import Dict, List, Any

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.compliance_filter import ComplianceFilter, ComplianceAction
    from src.training_system import TrainingDataCollector, HarmfulContentCategory, TRAINING_AVAILABLE
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'compliance-filter-secret-key-change-in-production'
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
compliance_filter = None
training_collector = None

# Statistics storage (in production, use a proper database)
compliance_stats = {
    'total_checks': 0,
    'actions': {'allow': 0, 'warn': 0, 'block': 0},
    'categories': {},
    'hourly_stats': {},
    'recent_checks': []
}

def initialize_components():
    """Initialize compliance filter components."""
    global compliance_filter, training_collector
    
    try:
        logger.info("Initializing compliance filter...")
        compliance_filter = ComplianceFilter()
        
        logger.info("Initializing training data collector...")
        training_collector = TrainingDataCollector()
            
        logger.info("All components initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise

def update_stats(result, processing_time: float):
    """Update compliance statistics."""
    global compliance_stats
    
    compliance_stats['total_checks'] += 1
    compliance_stats['actions'][result.action.value] += 1
    
    # Update hourly stats
    hour = datetime.now().strftime('%H:00')
    if hour not in compliance_stats['hourly_stats']:
        compliance_stats['hourly_stats'][hour] = {'allow': 0, 'warn': 0, 'block': 0}
    compliance_stats['hourly_stats'][hour][result.action.value] += 1
    
    # Track categories if violations found
    if result.privacy_violations:
        for violation in result.privacy_violations:
            cat = violation.violation_type.value
            if cat not in compliance_stats['categories']:
                compliance_stats['categories'][cat] = 0
            compliance_stats['categories'][cat] += 1
    
    # Store recent check (limit to last 100)
    recent_check = {
        'timestamp': datetime.now().isoformat(),
        'action': result.action.value,
        'score': result.overall_score,
        'processing_time': processing_time,
        'reasoning': result.reasoning[:100] + "..." if len(result.reasoning) > 100 else result.reasoning
    }
    
    compliance_stats['recent_checks'].append(recent_check)
    if len(compliance_stats['recent_checks']) > 100:
        compliance_stats['recent_checks'] = compliance_stats['recent_checks'][-100:]

# Routes

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/check')
def check_page():
    """Compliance checking page."""
    return render_template('check.html')

@app.route('/analytics')
def analytics():
    """Analytics and reporting page."""
    return render_template('analytics.html')

@app.route('/training')
def training():
    """Training data management page."""
    return render_template('training.html')

@app.route('/settings')
def settings():
    """Configuration and settings page."""
    return render_template('settings.html')

# API Endpoints

@app.route('/api/check', methods=['POST'])
def api_check_compliance():
    """API endpoint for compliance checking."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        if not text.strip():
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        # Perform compliance check
        start_time = time.time()
        result = compliance_filter.check_compliance(text)
        processing_time = time.time() - start_time
        
        # Update statistics
        update_stats(result, processing_time)
        
        # Prepare response
        response = {
            'action': result.action.value,
            'overall_score': round(result.overall_score, 3),
            'hate_speech_score': round(result.hate_speech_score, 3),
            'privacy_score': round(result.privacy_score, 3),
            'privacy_violations': [
                {
                    'type': v.violation_type.value,
                    'text': v.text_span,
                    'confidence': round(v.confidence, 3)
                } for v in result.privacy_violations
            ],
            'processing_time': round(processing_time, 3),
            'reasoning': result.reasoning,
            'timestamp': result.timestamp
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Compliance check error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """Get compliance statistics."""
    return jsonify(compliance_stats)

@app.route('/api/training/categories')
def api_training_categories():
    """Get training data categories."""
    if not training_collector:
        return jsonify({'error': 'Training system not available'}), 503
    
    try:
        distribution = training_collector.get_category_distribution()
        categories = []
        
        for category, counts in distribution.items():
            categories.append({
                'name': category,
                'total': counts['safe'] + counts['harmful'],
                'harmful': counts['harmful'],
                'safe': counts['safe']
            })
        
        return jsonify({'categories': categories, 'total_examples': len(training_collector.examples)})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/training/add_example', methods=['POST'])
def api_add_training_example():
    """Add a training example."""
    if not training_collector:
        return jsonify({'error': 'Training system not available'}), 503
    
    try:
        data = request.get_json()
        required_fields = ['text', 'is_harmful', 'category']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        example_id = training_collector.add_example(
            text=data['text'],
            is_harmful=data['is_harmful'],
            category=HarmfulContentCategory(data['category']),
            confidence=data.get('confidence', 0.9),
            source=data.get('source', 'web_ui'),
            verified=True
        )
        
        return jsonify({'success': True, 'example_id': example_id})
        
    except Exception as e:
        logger.error(f"Error adding training example: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config')
def api_get_config():
    """Get current configuration."""
    if not compliance_filter:
        return jsonify({'error': 'Filter not initialized'}), 503
    
    config = {
        'thresholds': compliance_filter.thresholds,
        'weights': compliance_filter.weights,
        'scoring_method': compliance_filter.scoring_method,
        'hate_speech_available': compliance_filter.hate_speech_available,
        'training_available': TRAINING_AVAILABLE
    }
    
    return jsonify(config)

@app.route('/api/config', methods=['POST'])
def api_update_config():
    """Update configuration."""
    if not compliance_filter:
        return jsonify({'error': 'Filter not initialized'}), 503
    
    try:
        data = request.get_json()
        
        if 'thresholds' in data:
            compliance_filter.update_thresholds(data['thresholds'])
        
        if 'weights' in data:
            compliance_filter.update_weights(data['weights'])
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({'error': str(e)}), 500

def create_templates():
    """Create HTML templates for the web interface."""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Create base template
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}LLM Compliance Filter{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .status-allow { color: #28a745; }
        .status-warn { color: #ffc107; }
        .status-block { color: #dc3545; }
        .sidebar { min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .sidebar .nav-link { color: white; margin: 5px 0; border-radius: 8px; }
        .sidebar .nav-link:hover { background: rgba(255,255,255,0.1); color: white; }
        .sidebar .nav-link.active { background: rgba(255,255,255,0.2); color: white; }
        .content { padding: 30px; background-color: #f8f9fa; min-height: 100vh; }
        .stats-card { transition: all 0.3s ease; border: none; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stats-card:hover { transform: translateY(-5px); box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
        .card { border-radius: 12px; border: none; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .btn { border-radius: 8px; }
        .form-control { border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container-fluid p-0">
        <div class="row g-0">
            <!-- Sidebar -->
            <nav class="col-md-2 sidebar">
                <div class="p-4">
                    <h4 class="text-white mb-4"><i class="fas fa-shield-alt"></i> Compliance Filter</h4>
                    <ul class="nav nav-pills flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="/" id="nav-dashboard"><i class="fas fa-tachometer-alt me-2"></i> Dashboard</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/check" id="nav-check"><i class="fas fa-search me-2"></i> Check Content</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/analytics" id="nav-analytics"><i class="fas fa-chart-bar me-2"></i> Analytics</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/training" id="nav-training"><i class="fas fa-brain me-2"></i> Training</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/settings" id="nav-settings"><i class="fas fa-cog me-2"></i> Settings</a>
                        </li>
                    </ul>
                </div>
            </nav>
            
            <!-- Main content -->
            <main class="col-md-10 content">
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Highlight active nav item
        document.addEventListener('DOMContentLoaded', function() {
            const path = window.location.pathname;
            const navLinks = document.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                if (link.getAttribute('href') === path) {
                    link.classList.add('active');
                }
            });
        });
    </script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    with open(templates_dir / "base.html", 'w', encoding='utf-8') as f:
        f.write(base_template)
    
    # Dashboard template
    dashboard_template = '''{% extends "base.html" %}

{% block title %}Dashboard - LLM Compliance Filter{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1><i class="fas fa-tachometer-alt text-primary me-3"></i>Compliance Dashboard</h1>
    <div class="badge bg-success fs-6" id="status">System Online</div>
</div>

<!-- Statistics Cards -->
<div class="row mb-4">
    <div class="col-md-3 mb-3">
        <div class="card stats-card bg-primary text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title">Total Checks</h6>
                        <h2 class="mb-0" id="total-checks">0</h2>
                    </div>
                    <i class="fas fa-search fa-2x opacity-75"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card stats-card bg-success text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title">Allowed</h6>
                        <h2 class="mb-0" id="allowed-count">0</h2>
                    </div>
                    <i class="fas fa-check-circle fa-2x opacity-75"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card stats-card bg-warning text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title">Warnings</h6>
                        <h2 class="mb-0" id="warning-count">0</h2>
                    </div>
                    <i class="fas fa-exclamation-triangle fa-2x opacity-75"></i>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card stats-card bg-danger text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title">Blocked</h6>
                        <h2 class="mb-0" id="blocked-count">0</h2>
                    </div>
                    <i class="fas fa-ban fa-2x opacity-75"></i>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Recent Activity -->
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-white">
                <h5 class="mb-0"><i class="fas fa-history text-primary me-2"></i>Recent Activity</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover" id="recent-activity">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Action</th>
                                <th>Score</th>
                                <th>Processing Time</th>
                                <th>Reasoning</th>
                            </tr>
                        </thead>
                        <tbody id="activity-tbody">
                            <tr>
                                <td colspan="5" class="text-center text-muted">No activity yet</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
let stats = {};

// Initialize dashboard
async function initDashboard() {
    await updateStats();
    setInterval(updateStats, 3000); // Update every 3 seconds
}

async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        stats = await response.json();
        
        document.getElementById('total-checks').textContent = stats.total_checks || 0;
        document.getElementById('allowed-count').textContent = stats.actions.allow || 0;
        document.getElementById('warning-count').textContent = stats.actions.warn || 0;
        document.getElementById('blocked-count').textContent = stats.actions.block || 0;
        
        updateRecentActivity();
        
        document.getElementById('status').textContent = 'System Online';
        document.getElementById('status').className = 'badge bg-success fs-6';
    } catch (error) {
        console.error('Error updating stats:', error);
        document.getElementById('status').textContent = 'System Error';
        document.getElementById('status').className = 'badge bg-danger fs-6';
    }
}

function updateRecentActivity() {
    const tbody = document.getElementById('activity-tbody');
    tbody.innerHTML = '';
    
    if (!stats.recent_checks || stats.recent_checks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No activity yet</td></tr>';
        return;
    }
    
    stats.recent_checks.slice(-10).reverse().forEach(check => {
        const row = tbody.insertRow();
        const time = new Date(check.timestamp).toLocaleTimeString();
        const actionClass = `status-${check.action}`;
        const actionIcon = check.action === 'allow' ? 'check-circle' : 
                          check.action === 'warn' ? 'exclamation-triangle' : 'ban';
        
        row.innerHTML = `
            <td>${time}</td>
            <td><span class="${actionClass}"><i class="fas fa-${actionIcon} me-1"></i>${check.action.toUpperCase()}</span></td>
            <td><span class="badge bg-secondary">${check.score.toFixed(3)}</span></td>
            <td>${check.processing_time.toFixed(3)}s</td>
            <td class="text-truncate" style="max-width: 200px;">${check.reasoning || 'N/A'}</td>
        `;
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initDashboard);
</script>
{% endblock %}'''
    
    with open(templates_dir / "dashboard.html", 'w', encoding='utf-8') as f:
        f.write(dashboard_template)

    # Check page template
    check_template = '''{% extends "base.html" %}

{% block title %}Check Content - LLM Compliance Filter{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1><i class="fas fa-search text-primary me-3"></i>Check Content</h1>
</div>

<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header bg-white">
                <h5 class="mb-0"><i class="fas fa-edit text-primary me-2"></i>Content Input</h5>
            </div>
            <div class="card-body">
                <form id="check-form">
                    <div class="mb-3">
                        <label for="content-text" class="form-label">Enter text to check:</label>
                        <textarea class="form-control" id="content-text" rows="6" 
                                placeholder="Enter the content you want to check for compliance..."></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary" id="check-btn">
                        <i class="fas fa-search me-2"></i>Check Compliance
                    </button>
                    <button type="button" class="btn btn-secondary ms-2" onclick="clearForm()">
                        <i class="fas fa-trash me-2"></i>Clear
                    </button>
                </form>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header bg-white">
                <h5 class="mb-0"><i class="fas fa-info-circle text-primary me-2"></i>Quick Examples</h5>
            </div>
            <div class="card-body">
                <p class="text-muted mb-3">Try these examples:</p>
                <div class="d-grid gap-2">
                    <button class="btn btn-outline-success btn-sm" onclick="setExample('What is the capital of France?')">
                        Safe Content
                    </button>
                    <button class="btn btn-outline-warning btn-sm" onclick="setExample('My email is test@example.com')">
                        Privacy Violation
                    </button>
                    <button class="btn btn-outline-danger btn-sm" onclick="setExample('I want to hurt someone badly')">
                        Harmful Content
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Results Section -->
<div class="row mt-4" id="results-section" style="display: none;">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-white">
                <h5 class="mb-0"><i class="fas fa-chart-line text-primary me-2"></i>Compliance Results</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-3">
                        <div class="text-center">
                            <div class="display-4" id="action-icon"></div>
                            <h4 id="action-text" class="mt-2"></h4>
                        </div>
                    </div>
                    <div class="col-md-9">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="border rounded p-3 text-center">
                                    <h6 class="text-muted">Overall Score</h6>
                                    <h3 id="overall-score" class="mb-0"></h3>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="border rounded p-3 text-center">
                                    <h6 class="text-muted">Hate Speech</h6>
                                    <h3 id="hate-score" class="mb-0"></h3>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="border rounded p-3 text-center">
                                    <h6 class="text-muted">Privacy</h6>
                                    <h3 id="privacy-score" class="mb-0"></h3>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-3">
                            <h6>Reasoning:</h6>
                            <p id="reasoning" class="text-muted"></p>
                        </div>
                        
                        <div id="violations-section" style="display: none;">
                            <h6>Privacy Violations:</h6>
                            <div id="violations-list"></div>
                        </div>
                        
                        <div class="mt-2">
                            <small class="text-muted">Processing Time: <span id="processing-time"></span></small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.getElementById('check-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const text = document.getElementById('content-text').value.trim();
    if (!text) {
        alert('Please enter some text to check.');
        return;
    }
    
    const checkBtn = document.getElementById('check-btn');
    checkBtn.disabled = true;
    checkBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Checking...';
    
    try {
        const response = await fetch('/api/check', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: text})
        });
        
        const result = await response.json();
        
        if (response.ok) {
            displayResults(result);
        } else {
            alert('Error: ' + (result.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Network error: ' + error.message);
    } finally {
        checkBtn.disabled = false;
        checkBtn.innerHTML = '<i class="fas fa-search me-2"></i>Check Compliance';
    }
});

function displayResults(result) {
    // Show results section
    document.getElementById('results-section').style.display = 'block';
    
    // Set action display
    const actionIcons = {
        'allow': {icon: '✓', class: 'text-success', text: 'ALLOWED'},
        'warn': {icon: '⚠', class: 'text-warning', text: 'WARNING'},
        'block': {icon: '✕', class: 'text-danger', text: 'BLOCKED'}
    };
    
    const actionInfo = actionIcons[result.action];
    document.getElementById('action-icon').innerHTML = actionInfo.icon;
    document.getElementById('action-text').textContent = actionInfo.text;
    document.getElementById('action-text').className = 'mt-2 ' + actionInfo.class;
    
    // Set scores
    document.getElementById('overall-score').textContent = result.overall_score;
    document.getElementById('hate-score').textContent = result.hate_speech_score;
    document.getElementById('privacy-score').textContent = result.privacy_score;
    
    // Set reasoning
    document.getElementById('reasoning').textContent = result.reasoning;
    
    // Set processing time
    document.getElementById('processing-time').textContent = result.processing_time + 's';
    
    // Handle privacy violations
    if (result.privacy_violations && result.privacy_violations.length > 0) {
        document.getElementById('violations-section').style.display = 'block';
        const violationsList = document.getElementById('violations-list');
        violationsList.innerHTML = '';
        
        result.privacy_violations.forEach(violation => {
            const badge = document.createElement('span');
            badge.className = 'badge bg-warning me-2 mb-1';
            badge.textContent = `${violation.type}: "${violation.text}" (${violation.confidence})`;
            violationsList.appendChild(badge);
        });
    } else {
        document.getElementById('violations-section').style.display = 'none';
    }
    
    // Scroll to results
    document.getElementById('results-section').scrollIntoView({behavior: 'smooth'});
}

function setExample(text) {
    document.getElementById('content-text').value = text;
}

function clearForm() {
    document.getElementById('content-text').value = '';
    document.getElementById('results-section').style.display = 'none';
}
</script>
{% endblock %}'''
    
    with open(templates_dir / "check.html", 'w', encoding='utf-8') as f:
        f.write(check_template)

if __name__ == '__main__':
    print("🛡️  LLM Compliance Filter - Web Interface")
    print("=" * 50)
    print("🚀 Starting web server...")
    
    # Create templates
    create_templates()
    
    # Initialize components
    initialize_components()
    
    print("✅ Components initialized")
    print("🌐 Web interface will be available at: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000/")
    print("🔍 Check Content: http://localhost:5000/check")
    print("📈 Analytics: http://localhost:5000/analytics")
    print("🧠 Training: http://localhost:5000/training")
    print("⚙️  Settings: http://localhost:5000/settings")
    print()
    print("Press Ctrl+C to stop the server")
    
    # Run the Flask app
    try:
        print("🔧 Starting Flask development server...")
        print("📝 Note: If you can't access localhost:5000, try 127.0.0.1:5000")
        app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("🔧 Trying alternative port...")
        try:
            app.run(host='127.0.0.1', port=5001, debug=False, threaded=True)
        except Exception as e2:
            print(f"❌ Alternative port failed: {e2}")
