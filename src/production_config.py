#!/usr/bin/env python3
"""
Production Configuration for Enterprise Compliance Filter
Optimized for security, performance, and scalability
"""

import os
import secrets
from datetime import timedelta
from typing import Dict, Any

class ProductionConfig:
    """Production configuration with security and performance optimizations"""
    
    # Application Settings
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Secret Key - MUST be set in environment
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
    if SECRET_KEY == secrets.token_urlsafe(32):
        print("⚠️  WARNING: Using generated SECRET_KEY. Set SECRET_KEY environment variable!")
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost/compliance_prod')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 30,
    }
    
    # Redis Configuration for Caching and Sessions
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 3600
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    JWT_DECODE_LEEWAY = timedelta(seconds=10)
    
    # OAuth Configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
    MICROSOFT_CLIENT_ID = os.environ.get('MICROSOFT_CLIENT_ID')
    MICROSOFT_CLIENT_SECRET = os.environ.get('MICROSOFT_CLIENT_SECRET')
    
    # Security Configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-API-Key']
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "1000 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', '/var/log/compliance-filter/app.log')
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Performance Settings
    CACHE_ENABLED = True
    CACHE_DEFAULT_TIMEOUT = 3600
    INTELLIGENT_CACHE_SIZE = 10000
    SEMANTIC_CACHE_TTL = 7200
    
    # Compliance Filter Settings
    AI_MODELS_ENABLED = os.environ.get('AI_MODELS_ENABLED', 'true').lower() == 'true'
    PATTERN_DETECTION_ENABLED = True
    SEMANTIC_ANALYSIS_ENABLED = True
    ADVANCED_DETECTION_TIMEOUT = 5.0
    
    # Monitoring Configuration
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    PROMETHEUS_ENABLED = os.environ.get('PROMETHEUS_ENABLED', 'true').lower() == 'true'
    HEALTH_CHECK_ENABLED = True
    
    # Email Configuration (for notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Backup Configuration
    BACKUP_ENABLED = os.environ.get('BACKUP_ENABLED', 'true').lower() == 'true'
    BACKUP_SCHEDULE = os.environ.get('BACKUP_SCHEDULE', '0 2 * * *')  # Daily at 2 AM
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', 30))
    
    # SSL/TLS Configuration
    SSL_CERT_PATH = os.environ.get('SSL_CERT_PATH')
    SSL_KEY_PATH = os.environ.get('SSL_KEY_PATH')
    FORCE_HTTPS = os.environ.get('FORCE_HTTPS', 'true').lower() == 'true'
    
    @staticmethod
    def get_database_config() -> Dict[str, Any]:
        """Get optimized database configuration"""
        return {
            'url': ProductionConfig.DATABASE_URL,
            'pool_size': 20,
            'max_overflow': 30,
            'pool_recycle': 3600,
            'pool_pre_ping': True,
            'echo': False,
            'connect_args': {
                'connect_timeout': 10,
                'server_side_cursors': True
            }
        }
    
    @staticmethod
    def get_redis_config() -> Dict[str, Any]:
        """Get Redis configuration for caching and sessions"""
        return {
            'url': ProductionConfig.REDIS_URL,
            'decode_responses': True,
            'socket_timeout': 5,
            'socket_connect_timeout': 5,
            'retry_on_timeout': True,
            'health_check_interval': 30
        }
    
    @staticmethod
    def get_gunicorn_config() -> Dict[str, Any]:
        """Get Gunicorn configuration for production"""
        workers = int(os.environ.get('GUNICORN_WORKERS', 4))
        return {
            'bind': f"0.0.0.0:{os.environ.get('PORT', 5000)}",
            'workers': workers,
            'worker_class': 'gevent',
            'worker_connections': 1000,
            'max_requests': 1000,
            'max_requests_jitter': 100,
            'preload_app': True,
            'timeout': 60,
            'keepalive': 5,
            'access_logfile': '-',
            'error_logfile': '-',
            'log_level': 'info',
            'capture_output': True,
            'enable_stdio_inheritance': True
        }
    
    @staticmethod
    def validate_config():
        """Validate production configuration"""
        required_vars = [
            'SECRET_KEY', 'DATABASE_URL', 'JWT_SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Validate database URL
        if not ProductionConfig.DATABASE_URL.startswith(('postgresql://', 'mysql://', 'sqlite://')):
            raise ValueError("Invalid DATABASE_URL format")
        
        print("✅ Production configuration validated successfully")

# Security Headers Configuration
SECURITY_HEADERS = {
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Content-Security-Policy': (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'"
    ),
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
}

# Rate Limiting Rules
RATE_LIMITS = {
    'auth_login': "5 per minute",
    'auth_register': "3 per minute", 
    'analyze_content': "100 per hour",
    'api_general': "1000 per hour",
    'mfa_verify': "10 per minute"
}

if __name__ == '__main__':
    # Validate configuration when run directly
    try:
        ProductionConfig.validate_config()
        print("🎉 Production configuration is ready!")
        print(f"📊 Workers: {ProductionConfig.get_gunicorn_config()['workers']}")
        print(f"🗄️  Database: {ProductionConfig.DATABASE_URL.split('@')[1] if '@' in ProductionConfig.DATABASE_URL else 'SQLite'}")
        print(f"⚡ Redis: {ProductionConfig.REDIS_URL}")
        print(f"🔒 Security: {'HTTPS' if ProductionConfig.FORCE_HTTPS else 'HTTP'}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        exit(1)