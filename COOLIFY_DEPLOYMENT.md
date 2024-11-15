# Deploying FAQ Generator on Webdock with Coolify

## Step 1: Set Up Webdock Server

1. Create Webdock Account:
   - Go to https://webdock.io/en
   - Sign up for an account
   - Choose a server location close to your target users

2. Create Server:
   - Click "Create Server"
   - Recommended Configuration:
     - Ubuntu 22.04 LTS
     - At least 2GB RAM (for Playwright)
     - 2 CPU cores
     - 50GB SSD
   - Server Name: faq-generator
   - Choose Development Stack: Docker

## Step 2: Install Coolify

1. SSH into your Webdock server:
```bash
ssh root@your-server-ip
```

2. Install Coolify:
```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

3. After installation, access Coolify UI:
- Go to: https://your-server-ip:8000

## Step 3: Configure Coolify

1. Create New Project:
   - Name: FAQ Generator
   - Choose: Docker Compose

2. Connect GitHub Repository:
   - Add your GitHub repository
   - Select main branch
   - Enable auto-deploy

3. Configure Environment Variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   FLASK_ENV=production
   SECRET_KEY=your_secret_key
   ```

4. Configure Build Settings:
   - Build Command: docker-compose build
   - Start Command: docker-compose up -d

## Step 4: Domain Setup

1. Add Domain in Coolify:
   - Go to project settings
   - Add your domain
   - Enable HTTPS

2. Configure DNS:
   - Add A record pointing to your Webdock IP
   - Add CNAME for www subdomain

## Step 5: Monitoring

1. View Logs:
   - Go to project dashboard
   - Click "Logs" tab

2. Monitor Resources:
   - Check CPU/Memory usage
   - View container status

## Step 6: Maintenance

1. Automatic Updates:
```bash
# On the Webdock server
docker system prune -af
coolify update
```

2. Backup Screenshots:
```bash
# Set up daily backups
0 0 * * * tar -czf /backup/screenshots-$(date +%Y%m%d).tar.gz /app/static/screenshots/
```

## Security Considerations

1. Firewall Rules (already configured by Webdock):
   - Allow ports 80, 443 (HTTP/HTTPS)
   - Allow port 22 (SSH)
   - Block all other incoming traffic

2. SSL/TLS:
   - Coolify handles SSL certificates automatically
   - Renews Let's Encrypt certificates

## Troubleshooting

1. If deployment fails:
   - Check Coolify logs
   - Verify environment variables
   - Check Docker logs: `docker logs faq-generator`

2. If scraping fails:
   - Check Playwright installation
   - Verify Chrome dependencies
   - Check memory usage

3. Memory issues:
   - Monitor with: `htop`
   - Check Docker stats: `docker stats`

## Scaling

1. Vertical Scaling:
   - Upgrade Webdock server resources
   - Increase RAM/CPU as needed

2. Performance Optimization:
   - Enable Nginx caching
   - Optimize screenshot storage
   - Implement request queuing

## Backup Strategy

1. Application Data:
```bash
# Backup script
#!/bin/bash
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d)

# Backup screenshots
tar -czf $BACKUP_DIR/screenshots_$DATE.tar.gz /app/static/screenshots

# Backup environment variables
cp /app/.env $BACKUP_DIR/env_$DATE.bak

# Keep last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

2. Database (if added later):
   - Set up automated backups
   - Store backups off-site

## Monitoring Setup

1. Install Monitoring:
```bash
# Install Node Exporter
docker run -d \
  --name node-exporter \
  --restart unless-stopped \
  -p 9100:9100 \
  prom/node-exporter
```

2. Configure Alerts:
   - Set up Discord/Slack notifications
   - Monitor resource usage
   - Track application health

## Cost Optimization

1. Resource Management:
   - Monitor usage patterns
   - Adjust server size as needed
   - Clean up unused images/volumes

2. Backup Storage:
   - Implement rotation policy
   - Compress old screenshots
   - Use object storage for media
