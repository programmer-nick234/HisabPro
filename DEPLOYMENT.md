# HisabPro Deployment Guide

This guide will help you deploy HisabPro to production environments.

## Prerequisites

- A server with Ubuntu 20.04+ or similar Linux distribution
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)
- PostgreSQL database
- Redis server
- Razorpay account
- SendGrid account

## Option 1: Manual Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib redis-server nginx git

# Install Node.js 18+ (if not available in package manager)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 2. Database Setup

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE hisabpro;
CREATE USER hisabpro_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE hisabpro TO hisabpro_user;
\q
```

### 3. Application Setup

```bash
# Clone repository
git clone <your-repo-url> /opt/hisabpro
cd /opt/hisabpro

# Create application user
sudo useradd -r -s /bin/false hisabpro
sudo chown -R hisabpro:hisabpro /opt/hisabpro
```

### 4. Backend Deployment

```bash
cd /opt/hisabpro/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
sudo nano .env
```

Add the following to `.env`:

```env
DEBUG=False
SECRET_KEY=your_very_secure_secret_key_here
DB_NAME=hisabpro
DB_USER=hisabpro_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret
SENDGRID_API_KEY=your_sendgrid_api_key
EMAIL_FROM=noreply@yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
REDIS_URL=redis://localhost:6379/0
```

```bash
# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

### 5. Frontend Deployment

```bash
cd /opt/hisabpro/frontend

# Install dependencies
npm install

# Create environment file
sudo nano .env.local
```

Add the following to `.env.local`:

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_RAZORPAY_KEY_ID=your_razorpay_key_id
```

```bash
# Build for production
npm run build
```

### 6. Systemd Services

Create backend service:

```bash
sudo nano /etc/systemd/system/hisabpro-backend.service
```

```ini
[Unit]
Description=HisabPro Django Backend
After=network.target

[Service]
Type=notify
User=hisabpro
Group=hisabpro
WorkingDirectory=/opt/hisabpro/backend
Environment=PATH=/opt/hisabpro/backend/venv/bin
ExecStart=/opt/hisabpro/backend/venv/bin/gunicorn hisabpro.wsgi:application --bind 127.0.0.1:8000 --workers 3
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

Create frontend service:

```bash
sudo nano /etc/systemd/system/hisabpro-frontend.service
```

```ini
[Unit]
Description=HisabPro Next.js Frontend
After=network.target

[Service]
Type=simple
User=hisabpro
Group=hisabpro
WorkingDirectory=/opt/hisabpro/frontend
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start services:

```bash
sudo systemctl enable hisabpro-backend hisabpro-frontend
sudo systemctl start hisabpro-backend hisabpro-frontend
```

### 7. Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/hisabpro
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /opt/hisabpro/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/hisabpro/backend/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/hisabpro /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Set up auto-renewal
sudo crontab -e
```

Add this line to crontab:

```
0 12 * * * /usr/bin/certbot renew --quiet
```

## Option 2: Docker Deployment

### 1. Install Docker and Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: hisabpro
      POSTGRES_USER: hisabpro_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DEBUG=False
      - DB_NAME=hisabpro
      - DB_USER=hisabpro_user
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
      - RAZORPAY_KEY_ID=${RAZORPAY_KEY_ID}
      - RAZORPAY_KEY_SECRET=${RAZORPAY_KEY_SECRET}
      - RAZORPAY_WEBHOOK_SECRET=${RAZORPAY_WEBHOOK_SECRET}
      - SENDGRID_API_KEY=${SENDGRID_API_KEY}
      - EMAIL_FROM=${EMAIL_FROM}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
      - CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS}
    depends_on:
      - db
      - redis
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
      - NEXT_PUBLIC_RAZORPAY_KEY_ID=${NEXT_PUBLIC_RAZORPAY_KEY_ID}
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - static_volume:/var/www/static
      - media_volume:/var/www/media
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

### 3. Production Dockerfiles

Backend (`backend/Dockerfile.prod`):

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/staticfiles /app/media

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "hisabpro.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

Frontend (`frontend/Dockerfile.prod`):

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine AS runner

WORKDIR /app

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]
```

### 4. Deploy with Docker

```bash
# Create production environment file
cp env.example .env.prod
# Edit .env.prod with your production values

# Deploy
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

## Option 3: Cloud Platform Deployment

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

### Render Deployment

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt && python manage.py migrate`
4. Set start command: `gunicorn hisabpro.wsgi:application --bind 0.0.0.0:$PORT`

### Vercel Deployment (Frontend)

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

## Monitoring and Maintenance

### 1. Logs

```bash
# View application logs
sudo journalctl -u hisabpro-backend -f
sudo journalctl -u hisabpro-frontend -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Database Backups

```bash
# Create backup script
sudo nano /opt/hisabpro/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="hisabpro"
DB_USER="hisabpro_user"

mkdir -p $BACKUP_DIR
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/hisabpro_$DATE.sql
gzip $BACKUP_DIR/hisabpro_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "hisabpro_*.sql.gz" -mtime +7 -delete
```

```bash
chmod +x /opt/hisabpro/backup.sh

# Add to crontab for daily backups
sudo crontab -e
# Add: 0 2 * * * /opt/hisabpro/backup.sh
```

### 3. Updates

```bash
# Pull latest changes
cd /opt/hisabpro
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Update frontend
cd ../frontend
npm install
npm run build

# Restart services
sudo systemctl restart hisabpro-backend hisabpro-frontend
```

## Security Considerations

1. **Firewall**: Configure UFW to only allow necessary ports
2. **SSL**: Always use HTTPS in production
3. **Secrets**: Use environment variables for sensitive data
4. **Updates**: Keep system and dependencies updated
5. **Backups**: Regular database and file backups
6. **Monitoring**: Set up monitoring and alerting

## Troubleshooting

### Common Issues

1. **Database Connection**: Check PostgreSQL service and credentials
2. **Static Files**: Ensure nginx can access static files directory
3. **Permissions**: Check file permissions for application user
4. **Port Conflicts**: Ensure ports 80, 443, 3000, 8000 are available
5. **SSL Certificate**: Verify Let's Encrypt certificate renewal

### Performance Optimization

1. **Database**: Add indexes for frequently queried fields
2. **Caching**: Use Redis for session and cache storage
3. **CDN**: Use CDN for static files
4. **Compression**: Enable gzip compression in nginx
5. **Monitoring**: Use tools like New Relic or DataDog

## Support

For issues and questions:
- Check the logs for error messages
- Review the Django and Next.js documentation
- Create an issue in the GitHub repository
