# Simple Gunicorn config for debugging timeouts
import os

# Use Railway's PORT environment variable or fallback to 8080
port = os.environ.get('PORT', '8080')
bind = f"0.0.0.0:{port}"
workers = 1  # Single worker for easier debugging
timeout = 120  # 2 minutes timeout
loglevel = "debug"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
