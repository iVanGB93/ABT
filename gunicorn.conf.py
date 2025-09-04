# Gunicorn configuration for Railway deployment
import multiprocessing
import os

# Server socket - Use Railway's PORT environment variable or fallback to 8080
port = os.environ.get('PORT', '8080')
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes - Optimized for Railway
workers = max(1, min(multiprocessing.cpu_count() * 2 + 1, 4))  # Cap at 4 workers for Railway
worker_class = "sync"
worker_connections = 1000
timeout = 120  # Extended timeout for Railway (was causing the WORKER TIMEOUT)
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# Restart workers after this many requests, to help prevent memory leaks
preload_app = True

# Railway specific optimizations
max_worker_memory = 512 * 1024 * 1024  # 512MB per worker
worker_tmp_dir = '/dev/shm'  # Use shared memory for better performance (if available)

# Logging - Railway optimized
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
accesslog = "-"  # Log to stdout for Railway
errorlog = "-"   # Log to stderr for Railway

# Process naming
proc_name = 'abt_gunicorn'

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (not needed for Railway)
keyfile = None
certfile = None
