import os
from app import app as application
from config import config

# Set the configuration
config_name = os.getenv('FLASK_ENV', 'production')
application.config.from_object(config[config_name])

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    application.run(host='0.0.0.0', port=port)
