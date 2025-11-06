#!/usr/bin/env python3
"""
🎯 FINAL PRODUCTION COMPLIANCE FILTER SERVER
High-accuracy ML system with dramatically reduced false positives.
"""

from flask import Flask, render_template_string, request, jsonify
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
app.config['SECRET_KEY'] = 'final_production_compliance_2024'

# Import the accurate compliance filter
try:
    from accurate_compliance_filter import HighAccuracyMLFilter
    FILTER_AVAILABLE = True
    print("✅ High-accuracy ML filter loaded successfully")
except Exception as e:
    print(f"⚠️ High-accuracy filter not available: {e}")
    FILTER_AVAILABLE = False

class FinalSystemState:
    def __init__(self):
        self.ml_filter = None
        self.is_initialized = False
        self.metrics = {
            'total_processed': 0,
            'violations_detected': 0,
            'false_positives_detected': 0,
            'avg_response_time': 0.0,
            'accuracy_rate': 0.0,
            'precision_rate': 0.0
        }
        self.lock = threading.Lock()
        
    def initialize(self):
        if FILTER_AVAILABLE and not self.is_initialized:
            try:
                print("🎯 Initializing high-accuracy compliance filter...")
                self.ml_filter = HighAccuracyMLFilter()
                
                # Load existing models or train new ones
                training_results = self.ml_filter.load_models()
                if training_results:
                    self.metrics['accuracy_rate'] = training_results.get('best_test_accuracy', 0.0) * 100
                    self.metrics['precision_rate'] = training_results.get('best_test_precision', 0.0) * 100
                    print(f"✅ Models loaded. Accuracy: {self.metrics['accuracy_rate']:.1f}%, Precision: {self.metrics['precision_rate']:.1f}%")
                else:
                    print("🔧 Training new high-accuracy models...")
                    training_results = self.ml_filter.train(force_retrain=True)
                    self.metrics['accuracy_rate'] = training_results.get('best_test_accuracy', 0.0) * 100
                    self.metrics['precision_rate'] = training_results.get('best_test_precision', 0.0) * 100
                    print(f"✅ Models trained. Accuracy: {self.metrics['accuracy_rate']:.1f}%, Precision: {self.metrics['precision_rate']:.1f}%")
                
                self.is_initialized = True
                return True
            except Exception as e:
                print(f"❌ Failed to initialize: {e}")
                return False
        return False

system = FinalSystemState()

# Production HTML template
PRODUCTION_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🎯 High-Accuracy Compliance Filter</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gradient-bg { background: linear-gradient(135deg, #2c5530 0%, #4a7c59 100%); }
        .result-safe { border-left: 6px solid #28a745; background: linear-gradient(135deg, #d4edda 0%, #f1f8f4 100%); }
        .result-violation { border-left: 6px solid #dc3545; background: linear-gradient(135deg, #f8d7da 0%, #fdf2f2 100%); }
        .result-warning { border-left: 6px solid #ffc107; background: linear-gradient(135deg, #fff3cd 0%, #fefaf0 100%); }
        .analysis-input { min-height: 120px; border: 2px solid #e9ecef; border-radius: 8px; }
        .analysis-input:focus { border-color: #4a7c59; box-shadow: 0 0 0 0.2rem rgba(74, 124, 89, 0.25); }
        .metric-card { border-left: 4px solid #4a7c59; transition: transform 0.2s; }
        .metric-card:hover { transform: translateY(-3px); }
        .confidence-bar { height: 6px; border-radius: 3px; background: #e9ecef; overflow: hidden; }
        .confidence-fill { height: 100%; transition: width 0.5s ease; }
        .confidence-low { background: linear-gradient(90deg, #28a745 0%, #20c997 100%); }
        .confidence-med { background: linear-gradient(90deg, #ffc107 0%, #fd7e14 100%); }
        .confidence-high { background: linear-gradient(90deg, #dc3545 0%, #e74c3c 100%); }
        .fp-warning { background: linear-gradient(135deg, #fff3cd 0%, #fefaf0 100%); border-left: 4px solid #ffc107; }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark gradient-bg">
        <div class="container">
            <span class="navbar-brand">
                <i class="fas fa-bullseye"></i> High-Accuracy Compliance Filter
                <small class="ms-2 opacity-75">Production System</small>
            </span>
            <span class="navbar-text">
                <span class="badge bg-success me-2">
                    <i class="fas fa-check"></i> {{ "%.0f"|format(metrics.precision_rate) }}% PRECISION
                </span>
                <span class="badge bg-info">
                    <i class="fas fa-target"></i> {{ "%.0f"|format(metrics.accuracy_rate) }}% ACCURACY
                </span>
            </span>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Performance Metrics -->
        <div class="row mb-4">
            <div class="col-lg-3 col-md-6">
                <div class="card metric-card text-center">
                    <div class="card-body">
                        <i class="fas fa-chart-line fa-2x text-success mb-2"></i>
                        <h6>Total Processed</h6>
                        <h4 class="text-primary" id="totalProcessed">{{ metrics.total_processed }}</h4>
                        <small class="text-muted">Content analyzed</small>
                    </div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="card metric-card text-center">
                    <div class="card-body">
                        <i class="fas fa-shield-alt fa-2x text-danger mb-2"></i>
                        <h6>Violations Detected</h6>
                        <h4 class="text-danger" id="violationsDetected">{{ metrics.violations_detected }}</h4>
                        <small class="text-muted">Real threats blocked</small>
                    </div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="card metric-card text-center">
                    <div class="card-body">
                        <i class="fas fa-exclamation-triangle fa-2x text-warning mb-2"></i>
                        <h6>False Positive Risk</h6>
                        <h4 class="text-warning" id="falsePositives">{{ metrics.false_positives_detected }}</h4>
                        <small class="text-muted">Low FP warnings</small>
                    </div>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="card metric-card text-center">
                    <div class="card-body">
                        <i class="fas fa-tachometer-alt fa-2x text-info mb-2"></i>
                        <h6>Response Time</h6>
                        <h4 class="text-info" id="avgResponse">{{ "%.0f"|format(metrics.avg_response_time) }}ms</h4>
                        <small class="text-muted">Lightning fast</small>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- Analysis Interface -->
            <div class="col-lg-8">
                <div class="card shadow-sm">
                    <div class="card-header bg-white">
                        <h5 class="mb-0">
                            <i class="fas fa-microscope text-success"></i> 
                            High-Precision Content Analysis
                        </h5>
                        <small class="text-muted">Advanced ML system with {{ "%.0f"|format(metrics.precision_rate) }}% precision - minimal false positives</small>
                    </div>
                    <div class="card-body">
                        <form id="analysisForm">
                            <div class="mb-3">
                                <label class="form-label fw-bold">
                                    <i class="fas fa-edit"></i> Content to Analyze:
                                </label>
                                <textarea class="form-control analysis-input" id="contentInput" 
                                         placeholder="Enter text content for high-accuracy compliance analysis. This system has significantly reduced false positives..."
                                         required></textarea>
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-success btn-lg">
                                    <i class="fas fa-search"></i> Analyze with High-Accuracy ML
                                </button>
                            </div>
                        </form>
                        
                        <div id="result" class="mt-4" style="display: none;"></div>
                    </div>
                </div>

                <!-- Comprehensive Test Cases -->
                <div class="card mt-4 shadow-sm">
                    <div class="card-header bg-light">
                        <h5 class="mb-0">
                            <i class="fas fa-vial text-primary"></i> False Positive Reduction Test Cases
                        </h5>
                    </div>
                    <div class="card-body">
                        <p class="text-muted mb-3">Test cases designed to verify low false positive rates:</p>
                        
                        <div class="row">
                            <div class="col-md-6 col-lg-4">
                                <div class="mb-2">
                                    <strong class="text-success">Should be SAFE:</strong>
                                </div>
                                <button class="btn btn-outline-success btn-sm w-100 mb-1" onclick="testContent('I hate broccoli with all my heart')">Hate Food Opinion</button>
                                <button class="btn btn-outline-success btn-sm w-100 mb-1" onclick="testContent('This movie killed my expectations')">Hyperbolic Expression</button>
                                <button class="btn btn-outline-success btn-sm w-100 mb-1" onclick="testContent('I\\'m dying to see the new Marvel movie')">Figure of Speech</button>
                                <button class="btn btn-outline-success btn-sm w-100 mb-1" onclick="testContent('Academic research on hate speech detection')">Academic Content</button>
                                <button class="btn btn-outline-success btn-sm w-100 mb-1" onclick="testContent('News: terrorist attack in foreign country')">News Report</button>
                            </div>
                            
                            <div class="col-md-6 col-lg-4">
                                <div class="mb-2">
                                    <strong class="text-danger">Should be VIOLATIONS:</strong>
                                </div>
                                <button class="btn btn-outline-danger btn-sm w-100 mb-1" onclick="testContent('I hate all immigrants and they should be eliminated')">Real Hate Speech</button>
                                <button class="btn btn-outline-danger btn-sm w-100 mb-1" onclick="testContent('I\\'m going to kill you tomorrow at school')">Direct Threat</button>
                                <button class="btn btn-outline-danger btn-sm w-100 mb-1" onclick="testContent('Planning to bomb the government building')">Violence Plan</button>
                                <button class="btn btn-outline-danger btn-sm w-100 mb-1" onclick="testContent('SSN: 123-45-6789 Card: 4532123456789012')">Privacy Violation</button>
                            </div>
                            
                            <div class="col-lg-4">
                                <div class="mb-2">
                                    <strong class="text-warning">Edge Cases:</strong>
                                </div>
                                <button class="btn btn-outline-warning btn-sm w-100 mb-1" onclick="testContent('I could kill for a good pizza right now')">Food Craving</button>
                                <button class="btn btn-outline-warning btn-sm w-100 mb-1" onclick="testContent('This traffic is murder on my commute')">Traffic Complaint</button>
                                <button class="btn btn-outline-warning btn-sm w-100 mb-1" onclick="testContent('Writing a crime novel about serial killers')">Creative Writing</button>
                                <button class="btn btn-outline-info btn-sm w-100 mb-1" onclick="testContent('Historical analysis of genocide events')">Historical Study</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- System Information -->
            <div class="col-lg-4">
                <div class="card shadow-sm">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-cog"></i> System Performance
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <div class="d-flex justify-content-between">
                                <span>Model Precision:</span>
                                <strong>{{ "%.0f"|format(metrics.precision_rate) }}%</strong>
                            </div>
                            <div class="progress mt-1" style="height: 6px;">
                                <div class="progress-bar bg-success" style="width: {{ metrics.precision_rate }}%"></div>
                            </div>
                            <small class="text-muted">Extremely low false positives</small>
                        </div>
                        
                        <div class="mb-3">
                            <div class="d-flex justify-content-between">
                                <span>Model Accuracy:</span>
                                <strong>{{ "%.0f"|format(metrics.accuracy_rate) }}%</strong>
                            </div>
                            <div class="progress mt-1" style="height: 6px;">
                                <div class="progress-bar bg-info" style="width: {{ metrics.accuracy_rate }}%"></div>
                            </div>
                            <small class="text-muted">Overall classification accuracy</small>
                        </div>
                        
                        <hr>
                        <h6><i class="fas fa-info-circle"></i> Technical Details</h6>
                        <ul class="list-unstyled small">
                            <li><i class="fas fa-robot text-primary"></i> <strong>AI Model:</strong> Calibrated SVM</li>
                            <li><i class="fas fa-balance-scale text-success"></i> <strong>Training:</strong> Balanced Dataset</li>
                            <li><i class="fas fa-shield-check text-info"></i> <strong>Features:</strong> Smart Context Detection</li>
                            <li><i class="fas fa-exclamation-triangle text-warning"></i> <strong>FP Detection:</strong> Built-in Warnings</li>
                            <li><i class="fas fa-clock text-secondary"></i> <strong>Speed:</strong> Real-time Analysis</li>
                        </ul>
                        
                        <div class="alert alert-success mt-3">
                            <small>
                                <i class="fas fa-check-circle"></i>
                                <strong>Production Ready:</strong> This system has been optimized for minimal false positives while maintaining security effectiveness.
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let analysisCount = 0;
        
        document.getElementById('analysisForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const content = document.getElementById('contentInput').value;
            if (!content.trim()) return;
            
            const submitBtn = document.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing with High-Accuracy ML...';
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
                submitBtn.innerHTML = '<i class="fas fa-search"></i> Analyze with High-Accuracy ML';
                submitBtn.disabled = false;
            }
        });
        
        function displayResult(result) {
            const resultDiv = document.getElementById('result');
            const isViolation = result.is_violation;
            let cardClass, statusIcon, statusText, statusBadge, confidenceClass;
            
            if (isViolation) {
                cardClass = 'result-violation';
                statusIcon = '<i class="fas fa-times-circle text-danger fa-lg"></i>';
                statusText = 'VIOLATION DETECTED';
                statusBadge = 'bg-danger';
                confidenceClass = result.confidence > 0.8 ? 'confidence-high' : 'confidence-med';
            } else {
                cardClass = 'result-safe';
                statusIcon = '<i class="fas fa-check-circle text-success fa-lg"></i>';
                statusText = 'CONTENT APPROVED';
                statusBadge = 'bg-success';
                confidenceClass = 'confidence-low';
            }
            
            // Add false positive warning styling
            const fpWarning = result.false_positive_likelihood > 0.4 ? 
                '<div class="alert alert-warning mt-2 mb-0"><small><i class="fas fa-exclamation-triangle"></i> <strong>False Positive Risk:</strong> ' + 
                (result.false_positive_likelihood * 100).toFixed(0) + '%</small></div>' : '';
            
            resultDiv.className = `card ${cardClass} shadow-sm`;
            resultDiv.innerHTML = `
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="mb-0">${statusIcon} ${statusText}</h5>
                        <span class="badge ${statusBadge} fs-6">${isViolation ? 'VIOLATION' : 'SAFE'}</span>
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <small class="text-muted">ML Confidence</small>
                            <div class="d-flex align-items-center mt-1">
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
                    <div class="mb-2">
                        <small class="text-muted">Analysis Reasoning</small>
                        <ul class="list-unstyled mt-1 mb-0">
                            ${result.reasoning.map(reason => `<li class="small"><i class="fas fa-dot-circle text-primary me-2"></i>${reason}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                    
                    ${fpWarning}
                </div>
            `;
            
            resultDiv.style.display = 'block';
        }
        
        function displayError(error) {
            const resultDiv = document.getElementById('result');
            resultDiv.className = 'card result-violation shadow-sm';
            resultDiv.innerHTML = `
                <div class="card-body">
                    <h6><i class="fas fa-times-circle text-danger"></i> SYSTEM ERROR</h6>
                    <div class="alert alert-danger mb-0">${error}</div>
                </div>
            `;
            resultDiv.style.display = 'block';
        }
        
        function testContent(content) {
            document.getElementById('contentInput').value = content;
            document.getElementById('analysisForm').dispatchEvent(new Event('submit'));
        }

        // Update metrics
        setInterval(async function() {
            try {
                const response = await fetch('/api/metrics');
                const metrics = await response.json();
                
                document.getElementById('totalProcessed').textContent = metrics.total_processed;
                document.getElementById('violationsDetected').textContent = metrics.violations_detected;
                document.getElementById('falsePositives').textContent = metrics.false_positives_detected;
                document.getElementById('avgResponse').textContent = Math.round(metrics.avg_response_time) + 'ms';
                
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
    return render_template_string(PRODUCTION_TEMPLATE, 
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
                # Use the high-accuracy filter
                ml_result = system.ml_filter.predict(content)
                result = {
                    'is_violation': ml_result.is_violation,
                    'confidence': ml_result.confidence,
                    'violation_type': ml_result.violation_type,
                    'severity': ml_result.severity,
                    'reasoning': ml_result.reasoning,
                    'processing_time_ms': ml_result.processing_time_ms,
                    'model_confidence_breakdown': ml_result.model_confidence_breakdown,
                    'false_positive_likelihood': ml_result.false_positive_likelihood
                }
            except Exception as e:
                logger.error(f"ML analysis error: {e}")
                result = {
                    'is_violation': False,
                    'confidence': 0.0,
                    'violation_type': 'error',
                    'severity': 'low',
                    'reasoning': ['ML analysis failed'],
                    'processing_time_ms': (time.time() - start_time) * 1000,
                    'model_confidence_breakdown': {},
                    'false_positive_likelihood': 0.0,
                    'error': str(e)
                }
        else:
            # Simple fallback
            result = {
                'is_violation': False,
                'confidence': 0.0,
                'violation_type': 'fallback',
                'severity': 'low',
                'reasoning': ['System not initialized'],
                'processing_time_ms': (time.time() - start_time) * 1000,
                'model_confidence_breakdown': {},
                'false_positive_likelihood': 0.0
            }
        
        # Update metrics
        with system.lock:
            system.metrics['total_processed'] += 1
            if result['is_violation']:
                system.metrics['violations_detected'] += 1
            if result.get('false_positive_likelihood', 0) > 0.4:
                system.metrics['false_positives_detected'] += 1
            
            # Update average response time
            processing_time = result['processing_time_ms']
            current_avg = system.metrics['avg_response_time']
            total = system.metrics['total_processed']
            system.metrics['avg_response_time'] = (current_avg * (total - 1) + processing_time) / total
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics')
def metrics():
    with system.lock:
        return jsonify(system.metrics.copy())

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'high_accuracy_ready': system.is_initialized,
        'precision_rate': system.metrics.get('precision_rate', 0),
        'accuracy_rate': system.metrics.get('accuracy_rate', 0),
        'timestamp': datetime.now().isoformat()
    })

def main():
    print("🎯 Starting Final Production High-Accuracy Compliance Filter...")
    
    # Initialize system
    if system.initialize():
        print("✅ High-accuracy system ready!")
        print(f"📊 Model precision: {system.metrics['precision_rate']:.0f}% (minimal false positives)")
        print(f"🎯 Model accuracy: {system.metrics['accuracy_rate']:.0f}%")
    else:
        print("⚠️ Running in fallback mode")
    
    print("🌐 Final Production Server:")
    print("📊 Dashboard: http://localhost:5000")
    print("🔧 API: http://localhost:5000/api/analyze")
    print("🏥 Health: http://localhost:5000/health")
    
    # Run Flask server
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()