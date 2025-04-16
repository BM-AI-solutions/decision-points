# Production Deployment Guide

This guide outlines the steps to deploy the application to a production environment with all security, performance, and reliability enhancements.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Application Deployment](#application-deployment)
5. [Web Server Configuration](#web-server-configuration)
6. [Security Hardening](#security-hardening)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Backup and Recovery](#backup-and-recovery)
9. [Scaling Considerations](#scaling-considerations)
10. [Maintenance Procedures](#maintenance-procedures)

## Prerequisites

- Linux server (Ubuntu 22.04 LTS recommended)
- Python 3.10 or higher
- PostgreSQL 14 or higher
- Redis 6.2 or higher
- Nginx 1.20 or higher
- SSL certificate (Let's Encrypt recommended)
- Domain name configured with DNS

## Environment Setup

1. **Create a dedicated user for the application**:

```bash
sudo adduser dualagent
sudo usermod -aG sudo dualagent
```

2. **Install required system packages**:

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib redis-server nginx certbot python3-certbot-nginx supervisor git
```

3. **Clone the repository**:

```bash
sudo mkdir -p /var/www/dualagent
sudo chown dualagent:dualagent /var/www/dualagent
cd /var/www/dualagent
git clone https://github.com/yourusername/dualagentsystem.git .
```

4. **Create and activate a virtual environment**:

```bash
python3 -m venv venv
source venv/bin/activate
```

5. **Install production dependencies**:

```bash
pip install -r backend/requirements-production.txt
```

6. **Set up environment variables**:

```bash
cp backend/.env.production.template backend/.env.production
# Edit the .env.production file with your production values
nano backend/.env.production
```

## Database Setup

1. **Create a PostgreSQL database and user**:

```bash
sudo -u postgres psql
```

```sql
CREATE USER dualagent WITH PASSWORD 'your_strong_password';
CREATE DATABASE decision_points OWNER dualagent;
GRANT ALL PRIVILEGES ON DATABASE decision_points TO dualagent;
\q
```

2. **Configure PostgreSQL for production**:

```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
```

Add or modify these settings:

```
max_connections = 100
shared_buffers = 1GB
effective_cache_size = 3GB
work_mem = 32MB
maintenance_work_mem = 256MB
random_page_cost = 1.1
effective_io_concurrency = 200
wal_buffers = 16MB
max_wal_size = 2GB
checkpoint_completion_target = 0.9
```

3. **Restart PostgreSQL**:

```bash
sudo systemctl restart postgresql
```

## Application Deployment

1. **Initialize the database**:

```bash
cd /var/www/dualagent
source venv/bin/activate
export FLASK_APP=backend/app_production.py
flask db upgrade
```

2. **Create a systemd service file**:

```bash
sudo nano /etc/systemd/system/dualagent.service
```

Add the following content:

```
[Unit]
Description=Dual Agent System
After=network.target postgresql.service redis.service

[Service]
User=dualagent
Group=dualagent
WorkingDirectory=/var/www/dualagent
Environment="PATH=/var/www/dualagent/venv/bin"
EnvironmentFile=/var/www/dualagent/backend/.env.production
ExecStart=/var/www/dualagent/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 --access-logfile /var/log/dualagent/access.log --error-logfile /var/log/dualagent/error.log --log-level info "backend.app_production:app"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

3. **Create log directories**:

```bash
sudo mkdir -p /var/log/dualagent
sudo chown -R dualagent:dualagent /var/log/dualagent
```

4. **Enable and start the service**:

```bash
sudo systemctl enable dualagent
sudo systemctl start dualagent
```

## Web Server Configuration

1. **Create an Nginx configuration file**:

```bash
sudo nano /etc/nginx/sites-available/dualagent
```

Add the following content:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://apis.google.com https://js.stripe.com; connect-src 'self' https://api.stripe.com; img-src 'self' data: https://www.gstatic.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; frame-src 'self' https://js.stripe.com https://accounts.google.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; upgrade-insecure-requests;" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/rss+xml application/atom+xml image/svg+xml;
    
    # Frontend static files
    location / {
        root /var/www/dualagent/frontend;
        try_files $uri $uri/ /index.html;
        expires 1d;
        add_header Cache-Control "public, max-age=86400";
    }
    
    # API proxy
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_redirect off;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
        limit_conn conn_limit_per_ip 10;
    }
    
    # Static assets with longer cache
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg)$ {
        root /var/www/dualagent/frontend;
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }
    
    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}

# Rate limiting settings
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;
```

2. **Enable the site and get SSL certificate**:

```bash
sudo ln -s /etc/nginx/sites-available/dualagent /etc/nginx/sites-enabled/
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
sudo systemctl restart nginx
```

## Security Hardening

1. **Set up a firewall**:

```bash
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

2. **Configure automatic security updates**:

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

3. **Set up fail2ban to prevent brute force attacks**:

```bash
sudo apt install -y fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

Add or modify these settings:

```
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime = 3600

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 5
bantime = 3600
```

4. **Restart fail2ban**:

```bash
sudo systemctl restart fail2ban
```

## Monitoring and Logging

1. **Set up log rotation**:

```bash
sudo nano /etc/logrotate.d/dualagent
```

Add the following content:

```
/var/log/dualagent/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 dualagent dualagent
    sharedscripts
    postrotate
        systemctl reload dualagent
    endscript
}
```

2. **Install and configure Prometheus for monitoring**:

```bash
sudo apt install -y prometheus prometheus-node-exporter
```

3. **Configure Prometheus**:

```bash
sudo nano /etc/prometheus/prometheus.yml
```

Add your application to the scrape configs:

```yaml
scrape_configs:
  - job_name: 'dualagent'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:5000']
```

4. **Restart Prometheus**:

```bash
sudo systemctl restart prometheus
```

## Backup and Recovery

1. **Set up automated database backups**:

```bash
sudo mkdir -p /var/backups/dualagent
sudo chown dualagent:dualagent /var/backups/dualagent
```

2. **Create a backup script**:

```bash
sudo nano /usr/local/bin/backup-dualagent.sh
```

Add the following content:

```bash
#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/var/backups/dualagent"
DB_NAME="decision_points"
DB_USER="dualagent"

# Database backup
pg_dump -U $DB_USER $DB_NAME | gzip > "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

# Application files backup
tar -czf "$BACKUP_DIR/files_$TIMESTAMP.tar.gz" -C /var/www dualagent

# Encrypt backups
gpg --batch --yes --passphrase-file /etc/dualagent/backup-passphrase.txt -c "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"
gpg --batch --yes --passphrase-file /etc/dualagent/backup-passphrase.txt -c "$BACKUP_DIR/files_$TIMESTAMP.tar.gz"

# Remove unencrypted files
rm "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"
rm "$BACKUP_DIR/files_$TIMESTAMP.tar.gz"

# Delete backups older than 30 days
find $BACKUP_DIR -type f -name "*.gpg" -mtime +30 -delete
```

3. **Make the script executable**:

```bash
sudo chmod +x /usr/local/bin/backup-dualagent.sh
```

4. **Create a secure passphrase file**:

```bash
sudo mkdir -p /etc/dualagent
echo "your-secure-passphrase" | sudo tee /etc/dualagent/backup-passphrase.txt
sudo chmod 600 /etc/dualagent/backup-passphrase.txt
```

5. **Schedule the backup with cron**:

```bash
sudo crontab -e
```

Add the following line to run the backup daily at 2 AM:

```
0 2 * * * /usr/local/bin/backup-dualagent.sh
```

## Scaling Considerations

1. **Horizontal scaling**:
   - Deploy multiple application instances behind a load balancer
   - Use sticky sessions if needed for user state
   - Consider containerization with Docker and Kubernetes

2. **Database scaling**:
   - Implement read replicas for read-heavy workloads
   - Consider database sharding for very large datasets
   - Use connection pooling to manage database connections efficiently

3. **Caching strategy**:
   - Implement Redis caching for frequently accessed data
   - Use CDN for static assets
   - Consider implementing edge caching with Cloudflare

## Maintenance Procedures

1. **Regular updates**:

```bash
# Pull latest code
cd /var/www/dualagent
git pull

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements-production.txt

# Run database migrations
export FLASK_APP=backend/app_production.py
flask db upgrade

# Restart the application
sudo systemctl restart dualagent
```

2. **Monitoring health**:

```bash
# Check application status
sudo systemctl status dualagent

# Check logs
sudo tail -f /var/log/dualagent/error.log

# Check database status
sudo -u postgres pg_isready
```

3. **Backup verification**:

Regularly test your backups by restoring them in a staging environment to ensure they are valid and complete.

```bash
# Decrypt a backup
gpg --batch --yes --passphrase-file /etc/dualagent/backup-passphrase.txt -d /var/backups/dualagent/db_20250306.sql.gz.gpg > /tmp/db_restore.sql.gz
gunzip /tmp/db_restore.sql.gz

# Restore to a test database
createdb -U dualagent test_restore
psql -U dualagent -d test_restore -f /tmp/db_restore.sql

# Clean up
dropdb -U dualagent test_restore
rm /tmp/db_restore.sql
```

---

## Troubleshooting

### Common Issues and Solutions

1. **Application won't start**:
   - Check logs: `sudo journalctl -u dualagent`
   - Verify environment variables: `sudo cat /var/www/dualagent/backend/.env.production`
   - Check permissions: `sudo ls -la /var/www/dualagent`

2. **Database connection issues**:
   - Check PostgreSQL is running: `sudo systemctl status postgresql`
   - Verify connection settings: `psql -U dualagent -h localhost -d decision_points`
   - Check firewall rules: `sudo ufw status`

3. **Web server issues**:
   - Check Nginx configuration: `sudo nginx -t`
   - Verify Nginx is running: `sudo systemctl status nginx`
   - Check access logs: `sudo tail -f /var/log/nginx/access.log`

4. **SSL certificate issues**:
   - Renew certificates: `sudo certbot renew`
   - Check certificate status: `sudo certbot certificates`
   - Verify certificate in browser: Check the padlock icon in your browser

---

By following this guide, you will have a production-ready deployment of the Dual Agent System with robust security, performance optimizations, and reliability enhancements.