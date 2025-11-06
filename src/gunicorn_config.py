#!/usr/bin/env python3
"""
Gunicorn Configuration for Enterprise Compliance Filter
Optimized for production performance and reliability
"""

import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
backlog = 2048

# Worker processes
workers = int(os.environ.get('GUNICORN_WORKERS', min(4, multiprocessing.cpu_count() * 2 + 1)))
worker_class = 'gevent'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Worker timeout and keepalive
timeout = 60
keepalive = 5
graceful_timeout = 30

# Logging configuration
access_logfile = '-'  # stdout
error_logfile = '-'   # stderr
log_level = os.environ.get('LOG_LEVEL', 'info').lower()
capture_output = True
enable_stdio_inheritance = True

# Log format
access_logformat = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'enterprise-compliance-filter'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = '/tmp'

# SSL (if certificates are provided)
if os.environ.get('SSL_CERT_PATH') and os.environ.get('SSL_KEY_PATH'):
    keyfile = os.environ.get('SSL_KEY_PATH')
    certfile = os.environ.get('SSL_CERT_PATH')
    ssl_version = 2  # TLS
    ciphers = 'HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA'

# Worker configuration based on environment
if os.environ.get('DEPLOYMENT_ENV') == 'high_traffic':
    # High traffic configuration
    workers = min(8, multiprocessing.cpu_count() * 4)
    worker_connections = 2000
    max_requests = 2000
    max_requests_jitter = 200
elif os.environ.get('DEPLOYMENT_ENV') == 'memory_optimized':
    # Memory optimized configuration
    workers = min(2, multiprocessing.cpu_count())
    worker_connections = 500
    max_requests = 500
    max_requests_jitter = 50

# Health check configuration
def when_ready(server):
    """Called just after the server is started"""
    server.log.info("🚀 Enterprise Compliance Filter server is ready!")
    server.log.info(f"👷 Workers: {workers}")
    server.log.info(f"🔗 Listening on: {bind}")
    server.log.info(f"🎯 Worker class: {worker_class}")

def on_starting(server):
    """Called just before the master process is initialized"""
    server.log.info("🔄 Starting Enterprise Compliance Filter server...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP"""
    server.log.info("♻️ Reloading Enterprise Compliance Filter server...")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT"""
    worker.log.info("⚠️ Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked"""
    server.log.info(f"👶 Forking worker: {worker.pid}")

def post_fork(server, worker):
    """Called just after a worker has been forked"""
    server.log.info(f"✅ Worker forked: {worker.pid}")

def post_worker_init(worker):
    """Called just after a worker has initialized the application"""
    worker.log.info(f"🎉 Worker {worker.pid} initialized successfully")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal"""
    worker.log.error(f"💥 Worker {worker.pid} aborted")

# Environment-specific optimizations
if os.environ.get('ENVIRONMENT') == 'production':
    # Production optimizations
    preload_app = True
    enable_stdio_inheritance = True
    
    # Memory optimizations
    max_requests = 1000
    max_requests_jitter = 100
    
    # Security
    limit_request_line = 8192
    limit_request_fields = 200
    limit_request_field_size = 8192

print(f"""
🔧 Gunicorn Configuration Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 Bind Address: {bind}
👷 Workers: {workers}
⚡ Worker Class: {worker_class}
🔗 Worker Connections: {worker_connections}
⏱️  Timeout: {timeout}s
📝 Log Level: {log_level}
🔒 SSL: {'Enabled' if os.environ.get('SSL_CERT_PATH') else 'Disabled'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")