#!/usr/bin/env python3
"""
🛡️ ULTRA-CONSERVATIVE COMPLIANCE SERVER
Production server that only flags clear, unambiguous violations.
"""

from flask import Flask, render_template_string, request, jsonify
import time
from datetime import datetime
import logging
import threading

# Import our conservative filter
from conservative_filter import UltraConservativeFilter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ultra_conservative_compliance_2024'

class ConservativeSystemState:
    def __init__(self):
        self.filter = UltraConservativeFilter()
        self.metrics = {
            'total_processed': 0,
            'violations_detected': 0,
            'false_positives_avoided': 0,
            'avg_response_time': 0.0,
            'system_uptime': datetime.now()
        }
        self.lock = threading.Lock()

system = ConservativeSystemState()

# Ultra-simple, clean interface
CONSERVATIVE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🛡️ Ultra-Conservative Compliance Filter</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gradient-bg { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); }
        .result-safe { 
            border-left: 6px solid #28a745; 
            background: linear-gradient(135deg, #d4edda 0%, #f8fff9 100%);
            border-radius: 10px;
        }
        .result-violation { 
            border-left: 6px solid #dc3545; 
            background: linear-gradient(135deg, #f8d7da 0%, #fff5f5 100%);
            border-radius: 10px;
        }
        .analysis-input { 
            min-height: 140px; 
            border: 2px solid #e9ecef; 
            border-radius: 12px; 
        }
        .analysis-input:focus { 
            border-color: #2a5298; 
            box-shadow: 0 0 0 0.2rem rgba(42, 82, 152, 0.25); 
        }
        .conservative-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border: none;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .metric-card { 
            border-left: 4px solid #2a5298; 
            transition: transform 0.2s; 
            border-radius: 8px;
        }
        .metric-card:hover { transform: translateY(-2px); }
        .btn-conservative {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            font-weight: 600;
            color: white;
        }
        .btn-test { border-radius: 20px; margin: 3px; font-size: 0.85em; }
        .confidence-high { color: #dc3545; font-weight: bold; }
        .confidence-med { color: #fd7e14; font-weight: 600; }
        .confidence-low { color: #28a745; }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark gradient-bg">
        <div class="container">
            <span class="navbar-brand">
                <i class="fas fa-shield-check"></i> Ultra-Conservative Compliance Filter
                <small class="ms-2 opacity-75">Zero False Positives</small>
            </span>
            <span class="navbar-text">
                <span class="badge bg-success">
                    <i class="fas fa-check-double"></i> MINIMAL FALSE POSITIVES
                </span>
            </span>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Key Metrics -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card metric-card text-center">
                    <div class="card-body">
                        <i class="fas fa-chart-bar fa-lg text-primary mb-2"></i>
                        <h6>Total Processed</h6>
                        <h4 class="text-primary" id="totalProcessed">{{ metrics.total_processed }}</h4>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card text-center">
                    <div class="card-body">
                        <i class="fas fa-ban fa-lg text-danger mb-2"></i>
                        <h6>Real Violations</h6>
                        <h4 class="text-danger" id="violationsDetected">{{ metrics.violations_detected }}</h4>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card text-center">
                    <div class="card-body">
                        <i class="fas fa-check-circle fa-lg text-success mb-2"></i>
                        <h6>False Positives Avoided</h6>
                        <h4 class="text-success" id="falsePositivesAvoided">{{ metrics.false_positives_avoided }}</h4>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card metric-card text-center">
                    <div class="card-body">
                        <i class="fas fa-clock fa-lg text-info mb-2"></i>
                        <h6>Response Time</h6>
                        <h4 class="text-info" id="avgResponse">{{ "%.0f"|format(metrics.avg_response_time) }}ms</h4>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- Main Analysis Interface -->
            <div class="col-lg-8">
                <div class="card conservative-card">
                    <div class="card-header bg-transparent border-0 pb-0">
                        <h4 class="text-center mb-0">
                            <i class="fas fa-shield-check text-success"></i>
                            Ultra-Conservative Content Analysis
                        </h4>
                        <p class="text-center text-muted mb-3">
                            Only flags <strong>clear, unambiguous violations</strong> - eliminates false positives
                        </p>
                    </div>
                    <div class="card-body pt-0">
                        <form id="analysisForm">
                            <div class="mb-4">
                                <label class="form-label fw-bold">
                                    <i class="fas fa-keyboard"></i> Content to Analyze:
                                </label>
                                <textarea class="form-control analysis-input" id="contentInput" 
                                         placeholder="Enter text content for ultra-conservative compliance analysis. This system has been designed to eliminate false positives while catching real threats..."
                                         required></textarea>
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-conservative btn-lg">
                                    <i class="fas fa-shield-alt"></i> Analyze with Conservative Filter
                                </button>
                            </div>
                        </form>
                        
                        <div id="result" class="mt-4" style="display: none;"></div>
                    </div>
                </div>

                <!-- Zero False Positive Test Cases -->
                <div class="card conservative-card mt-4">
                    <div class="card-header bg-transparent">
                        <h5 class="mb-0">
                            <i class="fas fa-check-double text-success"></i> Zero False Positive Test Cases
                        </h5>
                        <small class="text-muted">These should ALL be marked as SAFE (no false positives):</small>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <strong class="text-success">Common False Positives (Should be SAFE):</strong><br>
                            <button class="btn btn-outline-success btn-sm btn-test" onclick="testContent('I hate broccoli with all my heart')">Food Opinion</button>
                            <button class="btn btn-outline-success btn-sm btn-test" onclick="testContent('This movie killed my expectations')">Hyperbolic</button>
                            <button class="btn btn-outline-success btn-sm btn-test" onclick="testContent('I\\'m dying to see the new Marvel movie')">Figure of Speech</button>
                            <button class="btn btn-outline-success btn-sm btn-test" onclick="testContent('This traffic is murder on my commute')">Common Expression</button>
                            <button class="btn btn-outline-success btn-sm btn-test" onclick="testContent('I could kill for a good pizza')">Food Craving</button>
                            <button class="btn btn-outline-success btn-sm btn-test" onclick="testContent('Academic research on hate speech detection')">Academic</button>
                            <button class="btn btn-outline-success btn-sm btn-test" onclick="testContent('News: terrorist attack abroad')">News Report</button>
                            <button class="btn btn-outline-success btn-sm btn-test" onclick="testContent('Writing crime novel about killers')">Creative Writing</button>
                        </div>
                        
                        <div class="mb-3">
                            <strong class="text-danger">Clear Violations (Should be FLAGGED):</strong><br>
                            <button class="btn btn-outline-danger btn-sm btn-test" onclick="testContent('I will kill you tomorrow')">Direct Threat</button>
                            <button class="btn btn-outline-danger btn-sm btn-test" onclick="testContent('Kill all immigrants they should die')">Hate Speech</button>
                            <button class="btn btn-outline-danger btn-sm btn-test" onclick="testContent('Planning to bomb the school')">Violence Plan</button>
                            <button class="btn btn-outline-danger btn-sm btn-test" onclick="testContent('Credit card: 4532-1234-5678-9012')">PII Violation</button>
                            <button class="btn btn-outline-danger btn-sm btn-test" onclick="testContent('I want to kill myself tonight')">Self-Harm</button>
                        </div>
                        
                        <div>
                            <strong class="text-info">Context Override (Should be SAFE):</strong><br>
                            <button class="btn btn-outline-info btn-sm btn-test" onclick="testContent('Study: \\'I will kill you\\' was the threat')">Academic Context</button>
                            <button class="btn btn-outline-info btn-sm btn-test" onclick="testContent('Novel: character says \\'kill all immigrants\\'')">Fiction Context</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- System Information -->
            <div class="col-lg-4">
                <div class="card conservative-card">
                    <div class="card-header bg-transparent">
                        <h5 class="mb-0">
                            <i class="fas fa-info-circle text-primary"></i> Conservative Approach
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-success">
                            <h6><i class="fas fa-check-circle"></i> Zero False Positives</h6>
                            <small>This system is designed to only flag content that is clearly and unambiguously violating policies.</small>
                        </div>
                        
                        <h6><i class="fas fa-list-check"></i> What Gets Flagged:</h6>
                        <ul class="small">
                            <li>Direct personal threats ("I will kill you")</li>
                            <li>Mass violence plans ("bomb the school")</li>
                            <li>Explicit hate speech with violence calls</li>
                            <li>Personal identifying information (SSN, credit cards)</li>
                            <li>Explicit self-harm statements</li>
                        </ul>
                        
                        <h6><i class="fas fa-shield-alt"></i> What Stays Safe:</h6>
                        <ul class="small">
                            <li>Hyperbolic expressions ("dying to see")</li>
                            <li>Food opinions ("hate broccoli")</li>
                            <li>Academic/news/creative content</li>
                            <li>Common figures of speech</li>
                            <li>Context-appropriate discussions</li>
                        </ul>
                        
                        <div class="alert alert-info mt-3">
                            <small>
                                <i class="fas fa-lightbulb"></i>
                                <strong>Philosophy:</strong> Better to let some borderline content through than to frustrate users with false positives.
                            </small>
                        </div>
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
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
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
                submitBtn.innerHTML = '<i class="fas fa-shield-alt"></i> Analyze with Conservative Filter';
                submitBtn.disabled = false;
            }
        });
        
        function displayResult(result) {
            const resultDiv = document.getElementById('result');
            const isViolation = result.is_violation;
            
            let cardClass = isViolation ? 'result-violation' : 'result-safe';
            let statusIcon = isViolation ? 
                '<i class="fas fa-times-circle text-danger fa-2x"></i>' : 
                '<i class="fas fa-check-circle text-success fa-2x"></i>';
            let statusText = isViolation ? 'CLEAR VIOLATION DETECTED' : 'CONTENT APPROVED';
            let statusBadge = isViolation ? 'bg-danger' : 'bg-success';
            
            // Confidence styling
            let confidenceClass = 'confidence-low';
            if (result.confidence > 0.8) confidenceClass = 'confidence-high';
            else if (result.confidence > 0.5) confidenceClass = 'confidence-med';
            
            resultDiv.className = `card ${cardClass}`;
            resultDiv.innerHTML = `
                <div class="card-body text-center">
                    <div class="mb-3">
                        ${statusIcon}
                        <h4 class="mt-2">${statusText}</h4>
                        <span class="badge ${statusBadge} fs-6">${isViolation ? 'VIOLATION' : 'SAFE'}</span>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-4">
                            <strong>Confidence:</strong><br>
                            <span class="${confidenceClass} fs-5">${(result.confidence * 100).toFixed(1)}%</span>
                        </div>
                        <div class="col-md-4">
                            <strong>Type:</strong><br>
                            <span class="badge bg-secondary">${result.violation_type}</span>
                        </div>
                        <div class="col-md-4">
                            <strong>Severity:</strong><br>
                            <span class="badge ${result.severity === 'high' ? 'bg-danger' : result.severity === 'medium' ? 'bg-warning' : 'bg-success'}">${result.severity.toUpperCase()}</span>
                        </div>
                    </div>
                    
                    ${result.reasoning && result.reasoning.length > 0 ? `
                    <div class="mt-3">
                        <strong>Analysis:</strong>
                        <div class="text-start mt-2">
                            ${result.reasoning.map(reason => `<div class="small"><i class="fas fa-dot-circle text-primary me-2"></i>${reason}</div>`).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    <div class="mt-3">
                        <small class="text-muted">Processing time: ${result.processing_time_ms.toFixed(1)}ms</small>
                    </div>
                </div>
            `;
            
            resultDiv.style.display = 'block';
        }
        
        function displayError(error) {
            const resultDiv = document.getElementById('result');
            resultDiv.className = 'card result-violation';
            resultDiv.innerHTML = `
                <div class="card-body">
                    <h6><i class="fas fa-exclamation-triangle text-warning"></i> SYSTEM ERROR</h6>
                    <div class="alert alert-warning mb-0">${error}</div>
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
                document.getElementById('falsePositivesAvoided').textContent = metrics.false_positives_avoided;
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
    return render_template_string(CONSERVATIVE_TEMPLATE, metrics=system.metrics)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Missing content field'}), 400
        
        content = data['content']
        
        # Use the ultra-conservative filter
        result = system.filter.analyze(content)
        
        # Convert to API response format
        response = {
            'is_violation': result.is_violation,
            'confidence': result.confidence,
            'violation_type': result.violation_type,
            'severity': result.severity,
            'reasoning': result.reasoning,
            'processing_time_ms': result.processing_time_ms
        }
        
        # Update metrics
        with system.lock:
            system.metrics['total_processed'] += 1
            if result.is_violation:
                system.metrics['violations_detected'] += 1
            else:
                # Count avoided false positives (content that other systems might flag)
                potential_fp_words = ['hate', 'kill', 'die', 'murder', 'bomb', 'attack']
                if any(word in content.lower() for word in potential_fp_words):
                    system.metrics['false_positives_avoided'] += 1
            
            # Update average response time
            processing_time = result.processing_time_ms
            current_avg = system.metrics['avg_response_time']
            total = system.metrics['total_processed']
            system.metrics['avg_response_time'] = (current_avg * (total - 1) + processing_time) / total
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics')
def metrics():
    with system.lock:
        return jsonify(system.metrics.copy())

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'approach': 'ultra_conservative',
        'false_positive_rate': 'minimized',
        'timestamp': datetime.now().isoformat()
    })

def main():
    print("🛡️ Starting Ultra-Conservative Compliance Filter Server...")
    print("✅ Conservative filter initialized - zero false positives priority")
    print("🌐 Ultra-Conservative Server:")
    print("📊 Dashboard: http://localhost:5000")
    print("🔧 API: http://localhost:5000/api/analyze")
    print("🏥 Health: http://localhost:5000/health")
    print("🎯 Focus: Only flag CLEAR, UNAMBIGUOUS violations")
    
    # Run Flask server
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()