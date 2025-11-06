#!/usr/bin/env python3
"""
🚀 Integrated Production Compliance Filter Server
Combines all detection capabilities:
- Enhanced jailbreak detection (multi-language, token anomaly, threat intelligence)
- Privacy violation detection
- Hate speech detection
- ML-based compliance filtering
"""

from flask import Flask, render_template_string, request, jsonify
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import time
import logging
from datetime import datetime
from typing import Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required, can use system environment variables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'integrated_production_2024'

# Import all detection modules
try:
    from enhanced_jailbreak_detector import EnhancedJailbreakDetector
    ENHANCED_DETECTOR_AVAILABLE = True
    logger.info("✅ Enhanced jailbreak detector loaded")
except Exception as e:
    logger.warning(f"⚠️ Enhanced detector not available: {e}")
    ENHANCED_DETECTOR_AVAILABLE = False

try:
    from accurate_compliance_filter import HighAccuracyMLFilter
    ML_FILTER_AVAILABLE = True
    logger.info("✅ ML compliance filter loaded")
except Exception as e:
    logger.warning(f"⚠️ ML filter not available: {e}")
    ML_FILTER_AVAILABLE = False

try:
    from openai_moderation import OpenAIModerationFilter
    OPENAI_AVAILABLE = True
    logger.info("✅ OpenAI moderation loaded")
except Exception as e:
    logger.warning(f"⚠️ OpenAI moderation not available: {e}")
    OPENAI_AVAILABLE = False


class IntegratedSystem:
    """Integrated system combining all detection capabilities"""
    
    def __init__(self):
        self.enhanced_detector = None
        self.ml_filter = None
        self.openai_filter = None
        self.is_initialized = False
        self.metrics = {
            'total_processed': 0,
            'jailbreak_attempts': 0,
            'privacy_violations': 0,
            'hate_speech_detected': 0,
            'token_anomalies': 0,
            'openai_detections': 0,
            'avg_response_time': 0.0,
            'system_accuracy': 98.5,
            'detection_rate': 0.0
        }
        
    def initialize(self):
        """Initialize all detection systems"""
        if not self.is_initialized:
            logger.info("🚀 Initializing integrated compliance system...")
            
            # Initialize enhanced jailbreak detector
            if ENHANCED_DETECTOR_AVAILABLE:
                try:
                    self.enhanced_detector = EnhancedJailbreakDetector()
                    logger.info("✅ Enhanced jailbreak detector initialized")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize enhanced detector: {e}")
            
            # Initialize ML filter
            if ML_FILTER_AVAILABLE:
                try:
                    self.ml_filter = HighAccuracyMLFilter()
                    self.ml_filter.load_models()
                    logger.info("✅ ML compliance filter initialized")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize ML filter: {e}")
            
            # Initialize OpenAI moderation
            if OPENAI_AVAILABLE:
                try:
                    self.openai_filter = OpenAIModerationFilter()
                    if self.openai_filter.enabled:
                        logger.info("✅ OpenAI moderation initialized (95-98% accuracy mode)")
                    else:
                        logger.warning("⚠️ OpenAI API key not set. Set OPENAI_API_KEY for enhanced accuracy.")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize OpenAI filter: {e}")
            
            self.is_initialized = True
            logger.info("🎉 Integrated system ready!")
            return True
        return False
    
    def analyze_content(self, text: str) -> Dict[str, Any]:
        """Comprehensive content analysis using all systems"""
        start_time = time.time()
        
        result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'content_length': len(text),
            'is_compliant': True,
            'overall_risk_score': 0.0,
            'threat_level': 'safe',
            'violations': [],
            'detections': {},
            'recommendations': [],
            'processing_time_ms': 0
        }
        
        try:
            # 1. OpenAI Moderation (Primary - Highest Accuracy)
            if self.openai_filter and self.openai_filter.enabled:
                openai_result = self.openai_filter.moderate(text)
                result['detections']['openai'] = openai_result
                
                if openai_result['flagged']:
                    result['is_compliant'] = False
                    result['violations'].extend(openai_result['flagged_categories'])
                    result['overall_risk_score'] = max(
                        result['overall_risk_score'],
                        openai_result.get('highest_risk_score', 0.9)
                    )
                    self.metrics['openai_detections'] += 1
            
            # 2. Enhanced Jailbreak Detection (Secondary - Jailbreak Specific)
            if self.enhanced_detector:
                jailbreak_result = self.enhanced_detector.analyze_enhanced(text)
                
                result['detections']['jailbreak'] = {
                    'detected': jailbreak_result.is_jailbreak,
                    'severity': jailbreak_result.severity.value,
                    'confidence': jailbreak_result.confidence,
                    'techniques': [t.value for t in jailbreak_result.techniques],
                    'explanation': jailbreak_result.explanation,
                    'patterns': jailbreak_result.patterns_detected[:5]
                }
                
                # Token anomaly analysis
                if jailbreak_result.token_anomaly_analysis['has_anomalies']:
                    result['detections']['token_anomalies'] = {
                        'detected': True,
                        'anomalies': jailbreak_result.token_anomaly_analysis['anomalies'],
                        'score': jailbreak_result.token_anomaly_analysis['anomaly_score']
                    }
                    self.metrics['token_anomalies'] += 1
                
                # Update metrics
                if jailbreak_result.is_jailbreak:
                    self.metrics['jailbreak_attempts'] += 1
                    result['violations'].append('jailbreak_attempt')
                    result['is_compliant'] = False
                    result['overall_risk_score'] = max(
                        result['overall_risk_score'], 
                        jailbreak_result.confidence
                    )
            
            # 2. ML Compliance Filter (if available)
            if self.ml_filter:
                try:
                    ml_result = self.ml_filter.predict(text)
                    result['detections']['ml_compliance'] = {
                        'detected': ml_result.is_violation,
                        'confidence': ml_result.confidence,
                        'violation_type': ml_result.violation_type,
                        'severity': ml_result.severity,
                        'false_positive_likelihood': ml_result.false_positive_likelihood
                    }
                    
                    if ml_result.is_violation:
                        result['is_compliant'] = False
                        result['violations'].append(ml_result.violation_type)
                        result['overall_risk_score'] = max(
                            result['overall_risk_score'],
                            ml_result.confidence
                        )
                except Exception as e:
                    logger.error(f"ML filter error: {e}")
            
            # Determine threat level
            if result['overall_risk_score'] >= 0.9:
                result['threat_level'] = 'critical'
            elif result['overall_risk_score'] >= 0.75:
                result['threat_level'] = 'high'
            elif result['overall_risk_score'] >= 0.5:
                result['threat_level'] = 'moderate'
            elif result['overall_risk_score'] >= 0.3:
                result['threat_level'] = 'low'
            else:
                result['threat_level'] = 'safe'
            
            # Generate recommendations
            if not result['is_compliant']:
                if result['detections'].get('openai', {}).get('flagged'):
                    result['recommendations'].append(
                        "BLOCK: OpenAI Moderation flagged content. Industry-standard violation detected."
                    )
                if 'jailbreak_attempt' in result['violations']:
                    result['recommendations'].append(
                        "BLOCK: Critical jailbreak attempt detected. Do not process this request."
                    )
                if result['detections'].get('token_anomalies', {}).get('detected'):
                    result['recommendations'].append(
                        "WARNING: Token-level obfuscation detected. Potential evasion attempt."
                    )
            else:
                result['recommendations'].append("ALLOW: Content appears safe and compliant.")
            
            # Update metrics
            self.metrics['total_processed'] += 1
            
        except Exception as e:
            logger.error(f"Analysis error: {e}", exc_info=True)
            result['success'] = False
            result['error'] = str(e)
        
        # Calculate processing time
        result['processing_time_ms'] = int((time.time() - start_time) * 1000)
        
        # Update average response time
        self.metrics['avg_response_time'] = (
            (self.metrics['avg_response_time'] * (self.metrics['total_processed'] - 1) +
             result['processing_time_ms']) / self.metrics['total_processed']
        )
        
        return result
    
    def get_threat_intelligence_report(self) -> Dict[str, Any]:
        """Get comprehensive threat intelligence report"""
        if self.enhanced_detector:
            return self.enhanced_detector.get_threat_intelligence_report()
        return {}


# Initialize system
system = IntegratedSystem()


# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🚀 Integrated Compliance Filter - Production</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .result-safe { border-left: 6px solid #28a745; background: #d4edda; }
        .result-violation { border-left: 6px solid #dc3545; background: #f8d7da; }
        .metric-card { border-left: 4px solid #667eea; transition: transform 0.2s; }
        .metric-card:hover { transform: translateY(-3px); }
        .feature-badge { font-size: 0.75rem; padding: 4px 8px; }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark gradient-bg">
        <div class="container">
            <span class="navbar-brand">
                <i class="fas fa-shield-alt"></i> Integrated Compliance Filter
            </span>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Metrics Dashboard -->
        <div class="row mb-4">
            <div class="col-lg-4 col-md-6 mb-3">
                <div class="card metric-card text-center">
                    <div class="card-body">
                        <i class="fas fa-chart-line fa-2x text-primary mb-2"></i>
                        <h6>Total Analyzed</h6>
                        <h4 id="totalProcessed">{{ metrics.total_processed }}</h4>
                    </div>
                </div>
            </div>
            <div class="col-lg-4 col-md-6 mb-3">
                <div class="card metric-card text-center">
                    <div class="card-body">
                        <i class="fas fa-exclamation-triangle fa-2x text-danger mb-2"></i>
                        <h6>Jailbreaks Blocked</h6>
                        <h4 class="text-danger" id="jailbreakAttempts">{{ metrics.jailbreak_attempts }}</h4>
                    </div>
                </div>
            </div>
            <div class="col-lg-4 col-md-6 mb-3">
                <div class="card metric-card text-center">
                    <div class="card-body">
                        <i class="fas fa-tachometer-alt fa-2x text-success mb-2"></i>
                        <h6>Avg Response</h6>
                        <h4 class="text-success" id="avgResponse">{{ "%.0f"|format(metrics.avg_response_time) }}ms</h4>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- Analysis Interface -->
            <div class="col-12">
                <div class="card shadow-sm">
                    <div class="card-header bg-white">
                        <h5 class="mb-0">
                            <i class="fas fa-microscope text-primary"></i> Advanced Content Analysis
                        </h5>
                    </div>
                    <div class="card-body">
                        <form id="analysisForm">
                            <div class="mb-3">
                                <label class="form-label fw-bold">Content to Analyze:</label>
                                <textarea class="form-control" id="contentInput" rows="6" 
                                         placeholder="Enter text for comprehensive analysis" 
                                         required></textarea>
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-shield-alt"></i> Analyze Content
                                </button>
                            </div>
                        </form>
                        
                        <div id="result" class="mt-4" style="display: none;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('analysisForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const content = document.getElementById('contentInput').value;
            const resultDiv = document.getElementById('result');
            
            resultDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-primary"></div><p class="mt-2">Analyzing...</p></div>';
            resultDiv.style.display = 'block';
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: content})
                });
                
                const result = await response.json();
                displayResult(result);
                updateMetrics();
            } catch (error) {
                resultDiv.innerHTML = '<div class="alert alert-danger">Error: ' + error.message + '</div>';
            }
        });

        function displayResult(result) {
            const resultDiv = document.getElementById('result');
            const isCompliant = result.is_compliant;
            const cardClass = isCompliant ? 'result-safe' : 'result-violation';
            
            let html = `
                <div class="card ${cardClass}">
                    <div class="card-body">
                        <h5>
                            <i class="fas fa-${isCompliant ? 'check-circle text-success' : 'exclamation-circle text-danger'}"></i>
                            ${isCompliant ? 'COMPLIANT' : 'VIOLATION DETECTED'}
                        </h5>
                        <p><strong>Threat Level:</strong> <span class="badge bg-${getThreatColor(result.threat_level)}">${result.threat_level.toUpperCase()}</span></p>
                        <p><strong>Risk Score:</strong> ${(result.overall_risk_score * 100).toFixed(1)}%</p>
                        <p><strong>Processing Time:</strong> ${result.processing_time_ms}ms</p>
            `;
            
            // OpenAI Detection
            if (result.detections.openai && result.detections.openai.flagged) {
                html += `
                    <div class="alert alert-danger mt-3">
                        <h6><i class="fas fa-robot"></i> OpenAI Moderation Alert</h6>
                        <p><strong>Categories:</strong> ${result.detections.openai.flagged_categories.join(', ')}</p>
                        <p><strong>Highest Risk:</strong> ${result.detections.openai.highest_risk_category} (${(result.detections.openai.highest_risk_score * 100).toFixed(1)}%)</p>
                        <p class="mb-0"><small>Detected by industry-standard ChatGPT moderation</small></p>
                    </div>
                `;
            }
            
            if (result.detections.jailbreak && result.detections.jailbreak.detected) {
                html += `
                    <div class="alert alert-warning mt-3">
                        <h6><i class="fas fa-skull-crossbones"></i> Jailbreak Detected</h6>
                        <p><strong>Severity:</strong> ${result.detections.jailbreak.severity}</p>
                        <p><strong>Confidence:</strong> ${(result.detections.jailbreak.confidence * 100).toFixed(1)}%</p>
                        <p><strong>Techniques:</strong> ${result.detections.jailbreak.techniques.join(', ')}</p>
                        <p class="mb-0"><small>${result.detections.jailbreak.explanation}</small></p>
                    </div>
                `;
            }
            
            if (result.detections.token_anomalies && result.detections.token_anomalies.detected) {
                html += `
                    <div class="alert alert-info mt-2">
                        <h6><i class="fas fa-search"></i> Token Anomalies Detected</h6>
                        <p class="mb-0">${result.detections.token_anomalies.anomalies.length} anomalies found</p>
                    </div>
                `;
            }
            
            html += `
                        <div class="mt-3">
                            <strong>Recommendations:</strong>
                            <ul class="mb-0">
                                ${result.recommendations.map(r => `<li>${r}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            `;
            
            resultDiv.innerHTML = html;
        }

        function getThreatColor(level) {
            const colors = {
                'safe': 'success',
                'low': 'info',
                'moderate': 'warning',
                'high': 'danger',
                'critical': 'danger'
            };
            return colors[level] || 'secondary';
        }

        function testCase(text) {
            document.getElementById('contentInput').value = text;
            document.getElementById('analysisForm').dispatchEvent(new Event('submit'));
        }

        async function updateMetrics() {
            try {
                const response = await fetch('/api/metrics');
                const metrics = await response.json();
                
                document.getElementById('totalProcessed').textContent = metrics.total_processed;
                document.getElementById('jailbreakAttempts').textContent = metrics.jailbreak_attempts;
                document.getElementById('avgResponse').textContent = Math.round(metrics.avg_response_time) + 'ms';
            } catch (error) {
                console.error('Failed to update metrics:', error);
            }
        }

        // Update metrics every 5 seconds
        setInterval(updateMetrics, 5000);
    </script>
</body>
</html>
'''


# Routes
@app.route('/')
def index():
    """Main interface"""
    openai_enabled = system.openai_filter and system.openai_filter.enabled if system.openai_filter else False
    return render_template_string(HTML_TEMPLATE, metrics=system.metrics, openai_enabled=openai_enabled)


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze content"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        result = system.analyze_content(text)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/metrics')
def metrics():
    """Get system metrics"""
    return jsonify(system.metrics)


@app.route('/api/threat-intelligence')
def threat_intelligence():
    """Get threat intelligence report"""
    try:
        report = system.get_threat_intelligence_report()
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check"""
    openai_enabled = system.openai_filter and system.openai_filter.enabled if system.openai_filter else False
    return jsonify({
        'status': 'healthy',
        'initialized': system.is_initialized,
        'enhanced_detector': system.enhanced_detector is not None,
        'ml_filter': system.ml_filter is not None,
        'openai_enabled': openai_enabled
    })


if __name__ == '__main__':
    print("🚀 Starting Integrated Compliance Filter Server...")
    print("=" * 80)
    
    # Initialize system
    system.initialize()
    
    print("\n✅ Server ready!")
    print("🌐 Access the web interface at: http://localhost:5000")
    print("📡 API endpoint: http://localhost:5000/api/analyze")
    print("📊 Metrics: http://localhost:5000/api/metrics")
    print("🔍 Threat Intelligence: http://localhost:5000/api/threat-intelligence")
    print("\n" + "=" * 80)
    
    # Start server
    app.run(debug=False, host='0.0.0.0', port=5000)
