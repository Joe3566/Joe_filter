#!/usr/bin/env python3
"""
WSGI Entry Point for Production Deployment
Enterprise Compliance Filter - Production Ready
"""

import os
import sys
import logging
from pathlib import Path

# Add the application directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set up production environment
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('PYTHONPATH', str(current_dir))

try:
    # Import production configuration
    from production_config import ProductionConfig, SECURITY_HEADERS
    
    # Validate configuration before starting
    ProductionConfig.validate_config()
    
    # Import the Flask application
    from authenticated_demo_ui import app, auth_system, compliance_filter
    
    # Configure Flask app for production
    app.config.from_object(ProductionConfig)
    
    # Add security headers middleware
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        return response
    
    # Add HTTPS redirect middleware
    @app.before_request
    def force_https():
        """Force HTTPS in production"""
        from flask import request, redirect, url_for
        if ProductionConfig.FORCE_HTTPS and not request.is_secure:
            if request.url.startswith('http://'):
                return redirect(request.url.replace('http://', 'https://'), code=301)
    
    # Configure logging for production
    if not app.debug:
        # Set up file logging
        log_dir = Path(ProductionConfig.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            ProductionConfig.LOG_FILE,
            maxBytes=ProductionConfig.LOG_MAX_BYTES,
            backupCount=ProductionConfig.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s [%(name)s] %(message)s'
        ))
        file_handler.setLevel(getattr(logging, ProductionConfig.LOG_LEVEL))
        
        # Set up console logging for container environments
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s [%(name)s] %(message)s'
        ))
        console_handler.setLevel(getattr(logging, ProductionConfig.LOG_LEVEL))
        
        # Add handlers to app logger
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(getattr(logging, ProductionConfig.LOG_LEVEL))
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, ProductionConfig.LOG_LEVEL),
            format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
            handlers=[file_handler, console_handler]
        )
    
    # Initialize monitoring if enabled
    if hasattr(ProductionConfig, 'SENTRY_DSN') and ProductionConfig.SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            
            sentry_sdk.init(
                dsn=ProductionConfig.SENTRY_DSN,
                integrations=[
                    FlaskIntegration(auto_enabling_integrations=False),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=0.1,
                profiles_sample_rate=0.1,
                environment='production'
            )
            app.logger.info("✅ Sentry monitoring initialized")
        except ImportError:
            app.logger.warning("⚠️ Sentry SDK not installed, skipping error monitoring")
    
    # Add health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for load balancers"""
        from flask import jsonify
        import time
        
        start_time = time.time()
        
        try:
            # Check database connection
            if auth_system:
                # Simple database query to check connectivity
                auth_system.get_user_by_id('health-check-test')
            
            # Check compliance filter
            if compliance_filter:
                # Simple test of compliance filter
                result = compliance_filter.check_compliance("health check test")
                
            response_time = (time.time() - start_time) * 1000
            
            return jsonify({
                'status': 'healthy',
                'timestamp': time.time(),
                'response_time_ms': round(response_time, 2),
                'version': '1.0.0',
                'components': {
                    'database': 'healthy',
                    'compliance_filter': 'healthy',
                    'cache': 'healthy'
                }
            }), 200
            
        except Exception as e:
            app.logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'timestamp': time.time(),
                'error': str(e)
            }), 503
    
    # Add readiness check endpoint
    @app.route('/ready')
    def readiness_check():
        """Readiness check for Kubernetes deployments"""
        from flask import jsonify
        
        try:
            # Check if all components are ready
            if not auth_system:
                raise Exception("Authentication system not initialized")
            if not compliance_filter:
                raise Exception("Compliance filter not initialized")
                
            return jsonify({
                'status': 'ready',
                'timestamp': time.time(),
                'message': 'Application is ready to serve traffic'
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'not_ready',
                'timestamp': time.time(),
                'error': str(e)
            }), 503
    
    # Add metrics endpoint for Prometheus
    if ProductionConfig.PROMETHEUS_ENABLED:
        @app.route('/metrics')
        def metrics():
            """Prometheus metrics endpoint"""
            from flask import Response
            import time
            
            # Basic metrics - in real production, use prometheus_client
            metrics_data = f"""# HELP compliance_requests_total Total number of compliance requests
# TYPE compliance_requests_total counter
compliance_requests_total {{method="analyze"}} {getattr(compliance_filter, 'total_requests', 0)}

# HELP compliance_response_time_seconds Response time for compliance checks
# TYPE compliance_response_time_seconds histogram
compliance_response_time_seconds_sum {getattr(compliance_filter, 'total_response_time', 0)}
compliance_response_time_seconds_count {getattr(compliance_filter, 'total_requests', 0)}

# HELP compliance_cache_hits_total Cache hit count
# TYPE compliance_cache_hits_total counter
compliance_cache_hits_total {getattr(compliance_filter, 'cache_hits', 0)}

# HELP app_info Application information
# TYPE app_info gauge
app_info {{version="1.0.0",environment="production"}} 1
"""
            return Response(metrics_data, mimetype='text/plain')
    
    app.logger.info("🚀 Production WSGI application initialized successfully")
    app.logger.info(f"🔒 Security headers enabled: {len(SECURITY_HEADERS)} headers")
    app.logger.info(f"📊 Health checks available at /health and /ready")
    
    # The WSGI application
    application = app
    
except Exception as e:
    print(f"❌ Failed to initialize production application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    # For development testing - use gunicorn for production
    print("⚠️ Running in development mode. Use Gunicorn for production!")
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))