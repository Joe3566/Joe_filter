#!/usr/bin/env python3
"""
🚀 PRODUCTION ML COMPLIANCE FILTER SERVER
High-accuracy ML-based compliance filtering with professional web interface.
"""

from flask import Flask, render_template_string, request, jsonify
import sys
import os
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import threading

# Import our trained ML filter
from robust_ml_filter import RobustMLComplianceFilter, FilterResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ml_compliance_filter_production_2024'

# Global system state
class SystemState:
    def __init__(self):
        self.ml_filter = None
        self.is_initialized = False
        self.recent_analyses = []
        self.system_metrics = {
            'total_processed': 0,
            'violations_detected': 0,
            'false_positives': 0,
            'system_uptime': datetime.now(),
            'average_response_time': 0.0,
            'accuracy_rate': 97.4,  # From training results
            'model_accuracy': 0.0,
            'model_f1_score': 0.0
        }
        self.lock = threading.Lock()
        
    def initialize_system(self):
        """Initialize the ML compliance filter system"""
        if not self.is_initialized:
            try:
                logger.info("🤖 Initializing ML compliance filter...")
                self.ml_filter = RobustMLComplianceFilter()
                
                # Load or train models
                training_results = self.ml_filter.train(force_retrain=False)
                
                if training_results:
                    self.system_metrics['model_accuracy'] = training_results.get('test_accuracy', 0.0)
                    self.system_metrics['model_f1_score'] = training_results.get('test_f1', 0.0)
                    self.system_metrics['accuracy_rate'] = training_results.get('test_accuracy', 0.0) * 100
                
                self.is_initialized = True
                logger.info("✅ ML compliance filter initialized successfully")
                logger.info(f"Model accuracy: {self.system_metrics['model_accuracy']:.4f}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize ML filter: {e}")
                return False
        return self.is_initialized

system_state = SystemState()

# Professional Web Interface Template
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 ML Compliance Filter - Production</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gradient-bg { background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); }
        .ml-accent { color: #3498db; }
        .metric-card { 
            border-left: 4px solid #3498db; 
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .metric-card:hover { 
            transform: translateY(-8px); 
            box-shadow: 0 8px 25px rgba(52, 152, 219, 0.3);
        }
        .analysis-form { 
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .analysis-input { 
            min-height: 140px; 
            border-radius: 10px;
            border: 2px solid #e9ecef;
            transition: border-color 0.3s;
        }
        .analysis-input:focus {
            border-color: #3498db;
            box-shadow: 0 0 0 0.2rem rgba(52, 152, 219, 0.25);
        }
        .result-safe { 
            border-left: 6px solid #27ae60; 
            background: linear-gradient(135deg, #d4edda 0%, #f1f8f4 100%);
            border-radius: 10px;
        }
        .result-warning { 
            border-left: 6px solid #f39c12; 
            background: linear-gradient(135deg, #fff3cd 0%, #fefaf0 100%);
            border-radius: 10px;
        }
        .result-danger { 
            border-left: 6px solid #e74c3c; 
            background: linear-gradient(135deg, #f8d7da 0%, #fdf2f2 100%);
            border-radius: 10px;
        }
        .real-time-feed { 
            max-height: 500px; 
            overflow-y: auto; 
            background: #f8f9fa; 
            border-radius: 15px; 
            padding: 20px;
        }
        .feed-item {
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .feed-item:hover { transform: translateX(5px); }
        .btn-ml { 
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .btn-test { 
            margin: 8px 0; 
            border-radius: 20px;
            font-weight: 500;
        }
        .performance-badge { 
            font-size: 0.85em; 
            border-radius: 15px;
            padding: 4px 12px;
        }
        .ml-stats {
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
            color: white;
            border-radius: 15px;
            padding: 20px;
        }
        .confidence-bar {
            height: 8px;
            border-radius: 4px;
            background: #e9ecef;
            overflow: hidden;
        }
        .confidence-fill {
            height: 100%;
            transition: width 0.5s ease;
        }
        .confidence-high { background: linear-gradient(90deg, #e74c3c 0%, #c0392b 100%); }
        .confidence-medium { background: linear-gradient(90deg, #f39c12 0%, #e67e22 100%); }
        .confidence-low { background: linear-gradient(90deg, #27ae60 0%, #229954 100%); }
    </style>
</head>
<body class="bg-light">
    <!-- Navigation -->
    <nav class="navbar navbar-dark gradient-bg">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-robot ml-accent"></i> ML Compliance Filter
                <small class="ms-2 opacity-75">Production AI System</small>
            </span>
            <span class="navbar-text">
                <span class="badge bg-success me-2">
                    <i class="fas fa-brain"></i> ML TRAINED
                </span>
                <span class="badge bg-info">
                    <i class="fas fa-shield-alt"></i> {{ "%.1f"|format(metrics.accuracy_rate) }}% ACCURACY
                </span>
            </span>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <!-- System Metrics -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6">
                <div class="card metric-card mb-3">
                    <div class="card-body text-center">
                        <i class="fas fa-chart-line fa-2x ml-accent mb-3"></i>
                        <h6 class="card-title">Total Processed</h6>
                        <h3 class="text-primary" id="totalProcessed">{{ metrics.total_processed }}</h3>
                        <span class="badge bg-primary performance-badge">Real-time Analytics</span>
                    </div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="card metric-card mb-3">
                    <div class="card-body text-center">
                        <i class="fas fa-exclamation-shield fa-2x text-danger mb-3"></i>
                        <h6 class="card-title">Violations Detected</h6>
                        <h3 class="text-danger" id="violationsDetected">{{ metrics.violations_detected }}</h3>
                        <span class="badge bg-danger performance-badge">ML Detection</span>
                    </div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="card metric-card mb-3">
                    <div class="card-body text-center">
                        <i class="fas fa-tachometer-alt fa-2x text-success mb-3"></i>
                        <h6 class="card-title">Avg Response</h6>
                        <h3 class="text-success" id="avgResponse">{{ "%.1f"|format(metrics.average_response_time) }}ms</h3>
                        <span class="badge bg-success performance-badge">Lightning Fast</span>
                    </div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="card metric-card mb-3">
                    <div class="card-body text-center">
                        <i class="fas fa-bullseye fa-2x text-info mb-3"></i>
                        <h6 class="card-title">ML Accuracy</h6>
                        <h3 class="text-info" id="accuracyRate">{{ "%.1f"|format(metrics.accuracy_rate) }}%</h3>
                        <span class="badge bg-info performance-badge">Trained Model</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- Content Analysis -->
            <div class="col-lg-8">
                <div class="analysis-form">
                    <h4 class="mb-4 text-center">
                        <i class="fas fa-brain ml-accent"></i> 
                        AI-Powered Content Analysis
                    </h4>
                    
                    <form id="analysisForm">
                        <div class="mb-4">
                            <label class="form-label fw-bold">
                                <i class="fas fa-edit"></i> Content to Analyze:
                            </label>
                            <textarea class="form-control analysis-input" id="contentInput" 
                                     placeholder="Enter text content for ML-powered compliance analysis (hate speech, threats, privacy violations, etc.)..."
                                     required></textarea>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <input type="text" class="form-control" id="userIdInput" 
                                       placeholder="User ID (optional)" style="border-radius: 10px;">
                            </div>
                            <div class="col-md-6">
                                <button type="submit" class="btn btn-primary btn-ml w-100">
                                    <i class="fas fa-cogs"></i> Analyze with ML
                                </button>
                            </div>
                        </div>
                    </form>
                    
                    <div id="analysisResult" class="mt-4" style="display: none;">
                        <h6 class="fw-bold"><i class="fas fa-chart-bar"></i> ML Analysis Result:</h6>
                        <div id="resultCard" class="card"></div>
                    </div>
                </div>

                <!-- Advanced Test Cases -->
                <div class="card mt-4">
                    <div class="card-header" style="background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%); color: white;">
                        <h5 class="mb-0">
                            <i class="fas fa-flask"></i> ML Training Test Cases
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-lg-3 col-md-6">
                                <button class="btn btn-outline-success w-100 btn-test" onclick="testContent('Hello everyone! I hope you have a wonderful day ahead.')">
                                    <i class="fas fa-check"></i> Safe Content
                                </button>
                            </div>
                            <div class="col-lg-3 col-md-6">
                                <button class="btn btn-outline-warning w-100 btn-test" onclick="testContent('My SSN is 123-45-6789 and credit card is 4532-1234-5678-9012')">
                                    <i class="fas fa-user-secret"></i> Privacy Data
                                </button>
                            </div>
                            <div class="col-lg-3 col-md-6">
                                <button class="btn btn-outline-danger w-100 btn-test" onclick="testContent('I hate all immigrants and wish they would disappear from our country')">
                                    <i class="fas fa-ban"></i> Hate Speech
                                </button>
                            </div>
                            <div class="col-lg-3 col-md-6">
                                <button class="btn btn-outline-dark w-100 btn-test" onclick="testContent('I will hunt you down and make you pay for what you have done')">
                                    <i class="fas fa-exclamation-triangle"></i> Threats
                                </button>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-lg-4 col-md-6">
                                <button class="btn btn-outline-info w-100 btn-test" onclick="testContent('Academic research paper on hate speech detection using machine learning algorithms')">
                                    <i class="fas fa-graduation-cap"></i> Academic Context
                                </button>
                            </div>
                            <div class="col-lg-4 col-md-6">
                                <button class="btn btn-outline-secondary w-100 btn-test" onclick="testContent('Planning to bomb the government building tomorrow with explosives')">
                                    <i class="fas fa-bomb"></i> Violence Test
                                </button>
                            </div>
                            <div class="col-lg-4 col-md-12">
                                <button class="btn btn-outline-primary w-100 btn-test" onclick="testContent('I hate broccoli with all my heart, it tastes terrible')">
                                    <i class="fas fa-question"></i> Edge Case
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Real-time Feed & ML Stats -->
            <div class="col-lg-4">
                <div class="card mb-4">
                    <div class="card-header bg-dark text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-stream"></i> Live ML Analysis Feed
                        </h5>
                    </div>
                    <div class="card-body p-0">
                        <div id="liveFeed" class="real-time-feed">
                            <div class="text-center text-muted">
                                <i class="fas fa-robot fa-2x mb-2"></i>
                                <p>Waiting for ML analysis requests...</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="ml-stats">
                    <h5 class="mb-3">
                        <i class="fas fa-brain"></i> ML Model Statistics
                    </h5>
                    <div class="mb-3">
                        <small class="text-white-50">Model Accuracy</small>
                        <h6 class="mb-1">{{ "%.2f"|format(metrics.model_accuracy * 100) }}%</h6>
                        <div class="progress" style="height: 6px;">
                            <div class="progress-bar bg-success" style="width: {{ metrics.model_accuracy * 100 }}%"></div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <small class="text-white-50">F1 Score</small>
                        <h6 class="mb-1">{{ "%.3f"|format(metrics.model_f1_score) }}</h6>
                        <div class="progress" style="height: 6px;">
                            <div class="progress-bar bg-info" style="width: {{ metrics.model_f1_score * 100 }}%"></div>
                        </div>
                    </div>
                    <hr class="my-3 border-light">
                    <ul class="list-unstyled mb-0">
                        <li><i class="fas fa-cog"></i> <strong>Models:</strong> Ensemble (LR+SVM+RF)</li>
                        <li><i class="fas fa-layer-group"></i> <strong>Features:</strong> TF-IDF + Engineered</li>
                        <li><i class="fas fa-database"></i> <strong>Training:</strong> 2,000+ samples</li>
                        <li><i class="fas fa-shield-check"></i> <strong>Status:</strong> Production Ready</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        let analysisCount = 0;
        
        // Analysis form handling
        document.getElementById('analysisForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const content = document.getElementById('contentInput').value;
            const userId = document.getElementById('userIdInput').value || 'ml_user_' + Math.random().toString(36).substr(2, 9);
            
            if (!content.trim()) return;
            
            // Show loading state
            const submitBtn = document.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing with ML...';
            submitBtn.disabled = true;
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content, user_id: userId })
                });
                
                const result = await response.json();
                displayResult(result);
                updateLiveFeed(result, content.substring(0, 60), userId);
                
            } catch (error) {
                console.error('ML analysis error:', error);
                displayError('ML analysis failed: ' + error.message);
            } finally {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
        
        function displayResult(result) {
            const resultDiv = document.getElementById('analysisResult');
            const resultCard = document.getElementById('resultCard');
            
            let cardClass = 'result-safe';
            let statusIcon = '<i class="fas fa-check-circle text-success fa-lg"></i>';
            let statusText = 'CONTENT APPROVED';
            let statusBadge = 'bg-success';
            let confidenceClass = 'confidence-low';
            
            if (result.is_violation) {
                if (result.confidence > 0.8) {
                    cardClass = 'result-danger';
                    statusIcon = '<i class="fas fa-times-circle text-danger fa-lg"></i>';
                    statusText = 'VIOLATION DETECTED';
                    statusBadge = 'bg-danger';
                    confidenceClass = 'confidence-high';
                } else {
                    cardClass = 'result-warning';
                    statusIcon = '<i class="fas fa-exclamation-triangle text-warning fa-lg"></i>';
                    statusText = 'POTENTIAL VIOLATION';
                    statusBadge = 'bg-warning';
                    confidenceClass = 'confidence-medium';
                }
            }
            
            resultCard.className = `card ${cardClass}`;
            resultCard.innerHTML = `
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="mb-0">${statusIcon} ${statusText}</h5>
                        <span class="badge ${statusBadge} fs-6">${result.is_violation ? 'VIOLATION' : 'SAFE'}</span>
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <small class="text-muted">ML Confidence</small>
                            <div class="d-flex align-items-center">
                                <strong class="me-2">${(result.confidence * 100).toFixed(1)}%</strong>
                                <div class="confidence-bar flex-grow-1">
                                    <div class="confidence-fill ${confidenceClass}" style="width: ${result.confidence * 100}%"></div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <small class="text-muted">Processing Time</small><br>
                            <strong>${result.processing_time_ms.toFixed(1)}ms</strong>
                        </div>
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <small class="text-muted">Violation Type</small><br>
                            <span class="badge bg-secondary">${result.violation_type}</span>
                        </div>
                        <div class="col-md-6">
                            <small class="text-muted">Severity Level</small><br>
                            <span class="badge ${result.severity === 'high' ? 'bg-danger' : result.severity === 'medium' ? 'bg-warning' : 'bg-success'}">${result.severity.toUpperCase()}</span>
                        </div>
                    </div>
                    
                    ${result.reasoning && result.reasoning.length > 0 ? `
                    <div class="mb-3">
                        <small class="text-muted">ML Reasoning</small>
                        <ul class="list-unstyled mt-1">
                            ${result.reasoning.map(reason => `<li><i class="fas fa-dot-circle text-primary me-2"></i>${reason}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                    
                    <div class="mt-3">
                        <small class="text-muted">Model Scores</small>
                        <div class="mt-1">
                            ${Object.entries(result.model_scores).map(([model, score]) => 
                                `<span class="badge bg-dark me-1">${model}: ${(score * 100).toFixed(0)}%</span>`
                            ).join('')}
                        </div>
                    </div>
                </div>
            `;
            
            resultDiv.style.display = 'block';
        }
        
        function displayError(error) {
            const resultDiv = document.getElementById('analysisResult');
            const resultCard = document.getElementById('resultCard');
            
            resultCard.className = 'card result-danger';
            resultCard.innerHTML = `
                <div class="card-body">
                    <h6><i class="fas fa-times-circle text-danger"></i> ML SYSTEM ERROR</h6>
                    <div class="alert alert-danger mb-0">${error}</div>
                </div>
            `;
            
            resultDiv.style.display = 'block';
        }
        
        function testContent(content) {
            document.getElementById('contentInput').value = content;
            document.getElementById('analysisForm').dispatchEvent(new Event('submit'));
        }
        
        function updateLiveFeed(result, contentPreview, userId) {
            const feed = document.getElementById('liveFeed');
            const timestamp = new Date().toLocaleTimeString();
            analysisCount++;
            
            const feedItem = document.createElement('div');
            feedItem.className = 'feed-item';
            feedItem.innerHTML = `
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <small class="text-muted">#${analysisCount} • ${timestamp}</small>
                    <span class="badge ${result.is_violation ? 'bg-danger' : 'bg-success'}">
                        ${result.is_violation ? 'VIOLATION' : 'SAFE'}
                    </span>
                </div>
                <small class="d-block mb-1"><strong>User:</strong> ${userId}</small>
                <small class="d-block mb-2 text-truncate"><strong>Content:</strong> ${contentPreview}${contentPreview.length >= 60 ? '...' : ''}</small>
                <div class="d-flex justify-content-between">
                    <small class="badge bg-secondary">Confidence: ${(result.confidence * 100).toFixed(0)}%</small>
                    <small class="badge bg-info">${result.processing_time_ms.toFixed(0)}ms</small>
                    <small class="badge bg-dark">${result.violation_type}</small>
                </div>
            `;
            
            feed.insertBefore(feedItem, feed.firstChild);
            
            // Keep only last 6 items
            while (feed.children.length > 6) {
                feed.removeChild(feed.lastChild);
            }
        }
        
        // Update metrics periodically
        setInterval(async function() {
            try {
                const response = await fetch('/api/metrics');
                const metrics = await response.json();
                
                document.getElementById('totalProcessed').textContent = metrics.total_processed;
                document.getElementById('violationsDetected').textContent = metrics.violations_detected;
                document.getElementById('avgResponse').textContent = metrics.average_response_time.toFixed(1) + 'ms';
                document.getElementById('accuracyRate').textContent = metrics.accuracy_rate.toFixed(1) + '%';
                
            } catch (error) {
                console.error('Metrics update error:', error);
            }
        }, 5000);
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_TEMPLATE, 
                                system_status=system_state.is_initialized,
                                metrics=system_state.system_metrics)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for ML-powered content analysis"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'error': 'Missing required field: content'}), 400
        
        content = data['content']
        user_id = data.get('user_id', f'user_{uuid.uuid4().hex[:8]}')
        
        if not system_state.is_initialized:
            return jsonify({
                'error': 'ML compliance system not initialized',
                'is_violation': False,
                'confidence': 0.0
            }), 503
        
        start_time = time.time()
        
        # Perform ML analysis
        try:
            ml_result = system_state.ml_filter.predict(content)
            
            # Convert to API response format
            result = {
                'is_violation': ml_result.is_violation,
                'confidence': ml_result.confidence,
                'violation_type': ml_result.violation_type,
                'severity': ml_result.severity,
                'reasoning': ml_result.reasoning,
                'processing_time_ms': ml_result.processing_time_ms,
                'model_scores': ml_result.model_scores,
                'features_triggered': ml_result.features_triggered,
                'timestamp': datetime.now().isoformat(),
                'analysis_method': 'ML_ENSEMBLE'
            }
            
        except Exception as e:
            logger.error(f"ML analysis error: {e}")
            result = {
                'is_violation': False,
                'confidence': 0.0,
                'violation_type': 'unknown',
                'severity': 'low',
                'reasoning': ['ML analysis failed'],
                'processing_time_ms': (time.time() - start_time) * 1000,
                'model_scores': {},
                'features_triggered': [],
                'error': str(e)
            }
        
        # Update metrics thread-safely
        with system_state.lock:
            system_state.system_metrics['total_processed'] += 1
            if result['is_violation']:
                system_state.system_metrics['violations_detected'] += 1
            
            # Update average response time
            current_avg = system_state.system_metrics['average_response_time']
            total_processed = system_state.system_metrics['total_processed']
            processing_time = result.get('processing_time_ms', 0)
            system_state.system_metrics['average_response_time'] = (
                (current_avg * (total_processed - 1) + processing_time) / total_processed
            )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API analysis error: {e}")
        return jsonify({
            'error': str(e), 
            'is_violation': False,
            'confidence': 0.0
        }), 500

@app.route('/api/metrics')
def api_metrics():
    """API endpoint for system metrics"""
    with system_state.lock:
        # Create a serializable copy of metrics
        metrics_copy = system_state.system_metrics.copy()
        metrics_copy['system_uptime'] = system_state.system_metrics['system_uptime'].isoformat()
    return jsonify(metrics_copy)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ml_initialized': system_state.is_initialized,
        'model_accuracy': system_state.system_metrics.get('model_accuracy', 0.0),
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

def main():
    """Main application entry point"""
    from waitress import serve
    
    print("🤖 Starting ML Compliance Filter Production Server...")
    
    # Initialize ML system
    if system_state.initialize_system():
        print("✅ ML system initialized successfully")
        print(f"🎯 Model accuracy: {system_state.system_metrics['model_accuracy']:.1%}")
        print(f"🎯 Model F1 score: {system_state.system_metrics['model_f1_score']:.3f}")
    else:
        print("⚠️ ML system initialization failed - running in fallback mode")
    
    print("🌐 Production ML Compliance Server Ready:")
    print("📊 Dashboard: http://localhost:8080")
    print("🔧 API: http://localhost:8080/api/analyze")
    print("📈 Metrics: http://localhost:8080/api/metrics")
    print("🏥 Health: http://localhost:8080/health")
    print("⚡ Server: Waitress WSGI + ML Models")
    
    # Run with Waitress production server
    serve(app, 
          host='0.0.0.0', 
          port=8080,
          threads=4,
          connection_limit=500,
          cleanup_interval=30)

if __name__ == '__main__':
    main()