#!/usr/bin/env python3
"""
🤖 SIMPLE ML COMPLIANCE FILTER SERVER
Robust and reliable ML-based compliance filtering server.
"""

from flask import Flask, render_template_string, request, jsonify
import sys
import os
import json
import time
import uuid
from datetime import datetime
import logging
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple_ml_compliance_2024'

# Import ML filter
try:
    from robust_ml_filter import RobustMLComplianceFilter
    ML_AVAILABLE = True
    print("✅ ML filter module loaded successfully")
except Exception as e:
    print(f"⚠️ ML filter not available: {e}")
    ML_AVAILABLE = False

class SimpleSystemState:
    def __init__(self):
        self.ml_filter = None
        self.is_initialized = False
        self.metrics = {
            'total_processed': 0,
            'violations_detected': 0,
            'avg_response_time': 0.0,
            'accuracy_rate': 0.0
        }
        self.lock = threading.Lock()
        
    def initialize(self):
        if ML_AVAILABLE and not self.is_initialized:
            try:
                print("🤖 Initializing ML compliance filter...")
                self.ml_filter = RobustMLComplianceFilter()
                
                # Load models (don't retrain)
                training_results = self.ml_filter.load_models()
                if training_results:
                    self.metrics['accuracy_rate'] = training_results.get('test_accuracy', 0.0) * 100
                    print(f"✅ Models loaded. Accuracy: {self.metrics['accuracy_rate']:.1f}%")
                else:
                    print("🔧 Training new models...")
                    training_results = self.ml_filter.train(force_retrain=True)
                    self.metrics['accuracy_rate'] = training_results.get('test_accuracy', 0.0) * 100
                    print(f"✅ Models trained. Accuracy: {self.metrics['accuracy_rate']:.1f}%")
                
                self.is_initialized = True
                return True
            except Exception as e:
                print(f"❌ Failed to initialize: {e}")
                return False
        return False

system = SimpleSystemState()

# Simple HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🤖 ML Compliance Filter</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .result-safe { border-left: 4px solid #28a745; background: #d4edda; }
        .result-danger { border-left: 4px solid #dc3545; background: #f8d7da; }
        .analysis-input { min-height: 120px; }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark gradient-bg">
        <div class="container">
            <span class="navbar-brand">
                🤖 ML Compliance Filter - Production Ready
            </span>
            <span class="badge bg-success">
                Accuracy: {{ "%.1f"|format(metrics.accuracy_rate) }}%
            </span>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5>Processed</h5>
                        <h3 class="text-primary" id="totalProcessed">{{ metrics.total_processed }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5>Violations</h5>
                        <h3 class="text-danger" id="violationsDetected">{{ metrics.violations_detected }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5>Response Time</h5>
                        <h3 class="text-success" id="avgResponse">{{ "%.1f"|format(metrics.avg_response_time) }}ms</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5>ML Accuracy</h5>
                        <h3 class="text-info">{{ "%.1f"|format(metrics.accuracy_rate) }}%</h3>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5>🧠 ML Content Analysis</h5>
                    </div>
                    <div class="card-body">
                        <form id="analysisForm">
                            <div class="mb-3">
                                <label class="form-label">Content to Analyze:</label>
                                <textarea class="form-control analysis-input" id="contentInput" 
                                         placeholder="Enter text for ML compliance analysis..."
                                         required></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary">
                                🔍 Analyze with ML
                            </button>
                        </form>
                        
                        <div id="result" class="mt-4" style="display: none;"></div>
                    </div>
                </div>

                <div class="card mt-4">
                    <div class="card-header">
                        <h5>🧪 Test Cases</h5>
                    </div>
                    <div class="card-body">
                        <button class="btn btn-outline-success me-2 mb-2" onclick="testContent('Hello everyone, have a great day!')">Safe Content</button>
                        <button class="btn btn-outline-warning me-2 mb-2" onclick="testContent('My SSN is 123-45-6789')">Privacy Data</button>
                        <button class="btn btn-outline-danger me-2 mb-2" onclick="testContent('I hate all immigrants and wish they would disappear')">Hate Speech</button>
                        <button class="btn btn-outline-dark me-2 mb-2" onclick="testContent('I will hunt you down and make you pay')">Threat</button>
                        <button class="btn btn-outline-info me-2 mb-2" onclick="testContent('Academic research on hate speech detection')">Academic</button>
                        <button class="btn btn-outline-secondary me-2 mb-2" onclick="testContent('I hate broccoli with all my heart')">Edge Case</button>
                    </div>
                </div>
            </div>

            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5>📊 System Status</h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled">
                            <li>🤖 <strong>ML Status:</strong> {{ 'Active' if system_ready else 'Training' }}</li>
                            <li>🎯 <strong>Accuracy:</strong> {{ "%.1f"|format(metrics.accuracy_rate) }}%</li>
                            <li>⚡ <strong>Models:</strong> Ensemble (LR+SVM+RF)</li>
                            <li>🛡️ <strong>Features:</strong> TF-IDF + Engineering</li>
                            <li>📈 <strong>Status:</strong> Production Ready</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('analysisForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const content = document.getElementById('contentInput').value;
            if (!content.trim()) return;
            
            const submitBtn = document.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '⏳ Analyzing...';
            submitBtn.disabled = true;
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content })
                });
                
                const result = await response.json();
                displayResult(result);
                
            } catch (error) {
                displayError('Analysis failed: ' + error.message);
            } finally {
                submitBtn.innerHTML = '🔍 Analyze with ML';
                submitBtn.disabled = false;
            }
        });
        
        function displayResult(result) {
            const resultDiv = document.getElementById('result');
            const isViolation = result.is_violation;
            const cardClass = isViolation ? 'result-danger' : 'result-safe';
            const statusIcon = isViolation ? '🚫' : '✅';
            const statusText = isViolation ? 'VIOLATION DETECTED' : 'CONTENT SAFE';
            
            resultDiv.className = `card ${cardClass}`;
            resultDiv.innerHTML = `
                <div class="card-body">
                    <h6>${statusIcon} ${statusText}</h6>
                    <p><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}%</p>
                    <p><strong>Type:</strong> ${result.violation_type}</p>
                    <p><strong>Severity:</strong> ${result.severity}</p>
                    <p><strong>Processing:</strong> ${result.processing_time_ms.toFixed(1)}ms</p>
                    ${result.reasoning && result.reasoning.length > 0 ? 
                        '<p><strong>Reasoning:</strong> ' + result.reasoning.join(', ') + '</p>' : ''}
                </div>
            `;
            resultDiv.style.display = 'block';
        }
        
        function displayError(error) {
            const resultDiv = document.getElementById('result');
            resultDiv.className = 'card result-danger';
            resultDiv.innerHTML = `
                <div class="card-body">
                    <h6>❌ ERROR</h6>
                    <p>${error}</p>
                </div>
            `;
            resultDiv.style.display = 'block';
        }
        
        function testContent(content) {
            document.getElementById('contentInput').value = content;
            document.getElementById('analysisForm').dispatchEvent(new Event('submit'));
        }

        // Update metrics every 10 seconds
        setInterval(async function() {
            try {
                const response = await fetch('/api/metrics');
                const metrics = await response.json();
                document.getElementById('totalProcessed').textContent = metrics.total_processed;
                document.getElementById('violationsDetected').textContent = metrics.violations_detected;
                document.getElementById('avgResponse').textContent = metrics.avg_response_time.toFixed(1) + 'ms';
            } catch (error) {
                console.error('Metrics update failed:', error);
            }
        }, 10000);
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE, 
                                metrics=system.metrics,
                                system_ready=system.is_initialized)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Missing content field'}), 400
        
        content = data['content']
        start_time = time.time()
        
        if system.is_initialized and system.ml_filter:
            try:
                ml_result = system.ml_filter.predict(content)
                result = {
                    'is_violation': ml_result.is_violation,
                    'confidence': ml_result.confidence,
                    'violation_type': ml_result.violation_type,
                    'severity': ml_result.severity,
                    'reasoning': ml_result.reasoning,
                    'processing_time_ms': ml_result.processing_time_ms,
                    'model_scores': ml_result.model_scores
                }
            except Exception as e:
                result = {
                    'is_violation': False,
                    'confidence': 0.0,
                    'violation_type': 'unknown',
                    'severity': 'low',
                    'reasoning': ['ML analysis failed'],
                    'processing_time_ms': (time.time() - start_time) * 1000,
                    'model_scores': {},
                    'error': str(e)
                }
        else:
            # Fallback simple analysis
            result = {
                'is_violation': any(word in content.lower() for word in ['hate', 'kill', 'bomb']),
                'confidence': 0.5,
                'violation_type': 'simple_pattern',
                'severity': 'medium',
                'reasoning': ['Simple pattern matching'],
                'processing_time_ms': (time.time() - start_time) * 1000,
                'model_scores': {}
            }
        
        # Update metrics
        with system.lock:
            system.metrics['total_processed'] += 1
            if result['is_violation']:
                system.metrics['violations_detected'] += 1
            
            # Update average response time
            processing_time = result['processing_time_ms']
            current_avg = system.metrics['avg_response_time']
            total = system.metrics['total_processed']
            system.metrics['avg_response_time'] = (current_avg * (total - 1) + processing_time) / total
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics')
def metrics():
    with system.lock:
        return jsonify(system.metrics.copy())

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'ml_ready': system.is_initialized,
        'timestamp': datetime.now().isoformat()
    })

def main():
    print("🤖 Starting Simple ML Compliance Filter Server...")
    
    # Initialize system
    if system.initialize():
        print("✅ System ready!")
    else:
        print("⚠️ Running in fallback mode")
    
    print("🌐 Server starting on http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000")
    print("🔧 API: http://localhost:5000/api/analyze")
    
    # Run with Flask development server (simpler than Waitress)
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()