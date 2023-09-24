# Gunicorn configuration file
# https://docs.gunicorn.org/en/stable/configure.html#configuration-file
# https://docs.gunicorn.org/en/stable/settings.html

# Server socket
bind = '0.0.0.0:5000'
backlog = 64

# Worker processes
workers = 1
worker_class = 'sync'
worker_connections = 1000
timeout = 180
keepalive = 2

# Server mechanics
daemon = False
raw_env = [
]
pidfile = None
umask = 0
user = 'ssm-user'
group = 'ssm-user'
tmp_upload_dir = None

# Logging
accesslog = 'access.log'
errorlog = 'error.log'
capture_output = True

import gunicorn
gunicorn.SERVER = 'Server'