# Website FAQ Generator - Production Deployment Guide

## Prerequisites

1. Linux server (Ubuntu 20.04 LTS recommended)
2. Python 3.8+ installed
3. Nginx installed
4. Supervisor installed
5. OpenAI API key

## Installation Steps

1. Clone the repository:
```bash
git clone <your-repo-url>
cd website_faq_generator
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
playwright install-deps
```

5. Create environment file:
```bash
cp .env.example .env
# Edit .env with your settings
nano .env
```

Required environment variables:
```
FLASK_ENV=production
SECRET_KEY=<your-secret-key>
OPENAI_API_KEY=<your-openai-api-key>
```

6. Create log directories:
```bash
sudo mkdir -p /var/log/faq_generator
sudo mkdir -p /var/log/supervisord
sudo chown -R www-data:www-data /var/log/faq_generator
sudo chown -R www-data:www-data /var/log/supervisord
```

7. Configure Supervisor:
```bash
sudo cp supervisor.conf /etc/supervisor/conf.d/faq_generator.conf
# Edit the configuration file with your paths
sudo nano /etc/supervisor/conf.d/faq_generator.conf
sudo supervisorctl reread
sudo supervisorctl update
```

8. Configure Nginx:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    location /static {
        alias /path/to/website_faq_generator/static;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

9. Enable and start services:
```bash
sudo supervisorctl start faq_generator
sudo service nginx restart
```

## Monitoring and Maintenance

1. View application logs:
```bash
tail -f /var/log/faq_generator/err.log
tail -f /var/log/faq_generator/out.log
```

2. Monitor processes:
```bash
sudo supervisorctl status
```

3. Restart application:
```bash
sudo supervisorctl restart faq_generator
```

## Security Considerations

1. Set up SSL/TLS using Let's Encrypt:
```bash
sudo certbot --nginx -d your-domain.com
```

2. Configure firewall:
```bash
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

3. Regular updates:
```bash
sudo apt update
sudo apt upgrade
pip install --upgrade -r requirements.txt
```

## Performance Optimization

1. Configure caching if needed:
```python
# Add Redis caching
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
```

2. Monitor memory usage:
```bash
# Install monitoring tools
sudo apt install htop
```

3. Set up rate limiting:
- The application includes Flask-Limiter
- Configure limits in config.py

## Backup

1. Set up regular backups of:
- Screenshots directory
- Log files
- Environment configuration

2. Backup script example:
```bash
#!/bin/bash
backup_dir="/path/to/backups"
date=$(date +%Y%m%d)
tar -czf $backup_dir/faq_generator_$date.tar.gz /path/to/website_faq_generator
```

## Troubleshooting

1. If the application fails to start:
- Check supervisor logs
- Verify environment variables
- Check permissions

2. If scraping fails:
- Verify Playwright installation
- Check network connectivity
- Review timeout settings

3. If OpenAI API fails:
- Verify API key
- Check rate limits
- Review error logs

## Scaling

For higher traffic:
1. Increase Gunicorn workers
2. Add load balancer
3. Implement caching
4. Consider containerization with Docker

## Monitoring

The application includes:
1. Prometheus metrics
2. Sentry error tracking
3. Access and error logs

Set up monitoring dashboards using:
- Grafana
- Prometheus
- Sentry

## Regular Maintenance Tasks

1. Log rotation:
```bash
# Add to /etc/logrotate.d/faq_generator
/var/log/faq_generator/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        supervisorctl restart faq_generator
    endscript
}
```

2. Database backups (if added later)
3. Security updates
4. SSL certificate renewal
