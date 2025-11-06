#!/usr/bin/env python3
"""
Flask Web API Example for LLM Compliance Filter

A simple web API that demonstrates how to use the compliance filter
in a web service. Perfect for testing and production deployment.

Usage:
    pip install flask
    python web_api_example.py
    
Then visit: http://localhost:5000
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from flask import Flask, request, jsonify, render_template_string
    from src.compliance_filter import ComplianceFilter
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not installed. Install with: pip install flask")

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>LLM Compliance Filter API</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .result { margin: 20px 0; padding: 15px; border-radius: 5px; }
        .allow { background-color: #d4edda; border: 1px solid #c3e6cb; }
        .warn { background-color: #fff3cd; border: 1px solid #ffeaa7; }
        .block { background-color: #f8d7da; border: 1px solid #f5c6cb; }
        textarea { width: 100%; height: 100px; margin: 10px 0; }
        button { padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .stats { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ LLM Compliance Filter API</h1>
        <p>Test the compliance filter with your own text. The system will detect privacy violations and inappropriate content.</p>
        
        <h3>Single Text Check</h3>
        <textarea id="single-text" placeholder="Enter text to check for compliance...">Hello, my email is user@example.com and my phone is (555) 123-4567</textarea>
        <br>
        <button onclick="checkSingle()">Check Compliance</button>
        <div id="single-result"></div>
        
        <h3>Batch Processing</h3>
        <textarea id="batch-text" placeholder="Enter multiple texts, one per line...">What's the weather like?
My SSN is 123-45-6789
How does AI work?
Call me at (555) 123-4567
My credit card is 4532-1234-5678-9012</textarea>
        <br>
        <button onclick="checkBatch()">Check Batch</button>
        <div id="batch-result"></div>
        
        <h3>Performance Stats</h3>
        <button onclick="getStats()">Get Performance Statistics</button>
        <div id="stats-result"></div>
        
        <h3>API Endpoints</h3>
        <ul>
            <li><strong>POST /api/check</strong> - Check single text: <code>{"text": "your text"}</code></li>
            <li><strong>POST /api/batch</strong> - Check multiple texts: <code>{"texts": ["text1", "text2"]}</code></li>
            <li><strong>GET /api/stats</strong> - Get performance statistics</li>
        </ul>
    </div>

    <script>
        function checkSingle() {
            const text = document.getElementById('single-text').value;
            const resultDiv = document.getElementById('single-result');
            
            fetch('/api/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            })
            .then(response => response.json())
            .then(data => {
                const actionClass = data.action.toLowerCase();
                const actionIcon = data.action === 'allow' ? '✅' : data.action === 'warn' ? '⚠️' : '🚫';
                
                resultDiv.innerHTML = `
                    <div class="result ${actionClass}">
                        <h4>${actionIcon} ${data.action.toUpperCase()}</h4>
                        <p><strong>Score:</strong> ${data.score.toFixed(3)}</p>
                        <p><strong>Reasoning:</strong> ${data.reasoning}</p>
                        <p><strong>Processing Time:</strong> ${(data.processing_time * 1000).toFixed(1)}ms</p>
                        ${data.privacy_violations ? '<p><strong>Privacy Violations:</strong> ' + data.privacy_violations.map(v => v.type).join(', ') + '</p>' : ''}
                    </div>
                `;
            })
            .catch(error => {
                resultDiv.innerHTML = `<div class="result block"><h4>❌ Error</h4><p>${error}</p></div>`;
            });
        }
        
        function checkBatch() {
            const text = document.getElementById('batch-text').value;
            const texts = text.split('\\n').filter(t => t.trim());
            const resultDiv = document.getElementById('batch-result');
            
            fetch('/api/batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ texts: texts })
            })
            .then(response => response.json())
            .then(data => {
                let html = '<div>';
                data.results.forEach((result, index) => {
                    const actionClass = result.action.toLowerCase();
                    const actionIcon = result.action === 'allow' ? '✅' : result.action === 'warn' ? '⚠️' : '🚫';
                    
                    html += `
                        <div class="result ${actionClass}" style="margin: 10px 0;">
                            <h5>${actionIcon} Text ${index + 1}: ${result.action.toUpperCase()}</h5>
                            <p><strong>Input:</strong> "${texts[index]}"</p>
                            <p><strong>Score:</strong> ${result.score.toFixed(3)} | <strong>Reasoning:</strong> ${result.reasoning}</p>
                        </div>
                    `;
                });
                html += `<p><strong>Total Processing Time:</strong> ${(data.total_time * 1000).toFixed(1)}ms</p>`;
                html += `<p><strong>Throughput:</strong> ${data.throughput.toFixed(1)} texts/second</p>`;
                html += '</div>';
                
                resultDiv.innerHTML = html;
            })
            .catch(error => {
                resultDiv.innerHTML = `<div class="result block"><h4>❌ Error</h4><p>${error}</p></div>`;
            });
        }
        
        function getStats() {
            const resultDiv = document.getElementById('stats-result');
            
            fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                const stats = data.performance_metrics || {};
                const cache = data.cache_stats || {};
                const system = data.system_metrics || {};
                const opts = data.performance_optimizations_enabled || {};
                
                resultDiv.innerHTML = `
                    <div class="stats">
                        <h4>📊 Performance Statistics</h4>
                        <p><strong>Total Requests:</strong> ${stats.total_requests || 0}</p>
                        <p><strong>Average Response Time:</strong> ${((stats.avg_response_time || 0) * 1000).toFixed(1)}ms</p>
                        <p><strong>Requests per Second:</strong> ${(stats.requests_per_second || 0).toFixed(1)}</p>
                        <p><strong>Cache Hit Rate:</strong> ${(cache.overall_hit_rate || 0).toFixed(1)}%</p>
                        <p><strong>Memory Usage:</strong> ${(system.memory_mb || 0).toFixed(1)}MB</p>
                        <p><strong>Optimizations:</strong> 
                            Caching: ${opts.caching ? '✅' : '❌'} | 
                            Monitoring: ${opts.monitoring ? '✅' : '❌'} | 
                            Parallel: ${opts.parallel_processing ? '✅' : '❌'}
                        </p>
                    </div>
                `;
            })
            .catch(error => {
                resultDiv.innerHTML = `<div class="result block"><h4>❌ Error</h4><p>${error}</p></div>`;
            });
        }
    </script>
</body>
</html>
"""

def create_app():
    """Create and configure the Flask application."""
    if not FLASK_AVAILABLE:
        print("Error: Flask is required but not installed.")
        print("Install with: pip install flask")
        return None
    
    app = Flask(__name__)
    
    # Create optimized compliance filter
    print("Initializing LLM Compliance Filter...")
    compliance_filter = ComplianceFilter.create_optimized()
    print("✅ Compliance filter ready!")
    
    @app.route('/')
    def home():
        """Serve the web interface."""
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/api/check', methods=['POST'])
    def check_compliance():
        """Check compliance of a single text."""
        try:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({'error': 'Missing "text" field'}), 400
            
            text = data['text']
            result = compliance_filter.check_compliance(text)
            
            response = {
                'action': result.action.value,
                'score': result.overall_score,
                'hate_speech_score': result.hate_speech_score,
                'privacy_score': result.privacy_score,
                'reasoning': result.reasoning,
                'processing_time': result.processing_time,
                'timestamp': result.timestamp,
                'privacy_violations': [
                    {
                        'type': v.violation_type.value,
                        'confidence': v.confidence,
                        'description': v.description
                    } for v in result.privacy_violations
                ]
            }
            
            return jsonify(response)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/batch', methods=['POST'])
    def batch_check():
        """Check compliance of multiple texts."""
        try:
            data = request.get_json()
            if not data or 'texts' not in data:
                return jsonify({'error': 'Missing "texts" field'}), 400
            
            texts = data['texts']
            if not isinstance(texts, list):
                return jsonify({'error': '"texts" must be a list'}), 400
            
            import time
            start_time = time.time()
            
            # Use parallel processing for better performance
            results = compliance_filter.batch_check_compliance(texts, parallel=True)
            
            total_time = time.time() - start_time
            
            response = {
                'results': [
                    {
                        'action': r.action.value,
                        'score': r.overall_score,
                        'reasoning': r.reasoning,
                        'processing_time': r.processing_time
                    } for r in results
                ],
                'total_time': total_time,
                'throughput': len(texts) / total_time if total_time > 0 else 0,
                'count': len(results)
            }
            
            return jsonify(response)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """Get performance statistics."""
        try:
            stats = compliance_filter.get_performance_stats()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': 'LLM Compliance Filter API',
            'version': '1.0.0',
            'optimizations_enabled': True
        })
    
    return app, compliance_filter

def main():
    """Run the Flask application."""
    print("🚀 Starting LLM Compliance Filter Web API")
    print("=" * 60)
    
    app_info = create_app()
    if app_info is None:
        return False
    
    app, filter_instance = app_info
    
    try:
        print("\n🌟 Server starting...")
        print("📱 Web Interface: http://localhost:5000")
        print("🔧 API Endpoint: http://localhost:5000/api/check")
        print("📊 Health Check: http://localhost:5000/api/health")
        print("\n💡 Example API calls:")
        print('curl -X POST http://localhost:5000/api/check -H "Content-Type: application/json" -d \'{"text":"Hello, my email is test@example.com"}\'')
        print("\n🛑 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run the Flask app
        app.run(
            host='0.0.0.0',  # Allow external connections
            port=5000,
            debug=False,  # Disable debug mode for better performance
            threaded=True  # Enable threading for better concurrency
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        filter_instance.cleanup()
        return True
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        filter_instance.cleanup()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
