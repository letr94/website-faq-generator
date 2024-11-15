import multiprocessing

# Gunicorn configuration for production
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
timeout = 120  # Increased timeout for long-running scraping tasks
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True
