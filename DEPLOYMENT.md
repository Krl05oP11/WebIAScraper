# Deployment Guide - webiascrap_v0.0.0

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For version control (recommended)

### Installation

#### Linux
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### macOS
```bash
# Install Docker Desktop for Mac
brew install --cask docker
```

#### Windows
Download and install Docker Desktop from: https://www.docker.com/products/docker-desktop

## Local Development

### 1. Setup Environment

```bash
# Navigate to project directory
cd ~/Projects/webiascrap_v0.0.0

# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env  # or use your preferred editor
```

### 2. Build and Run

```bash
# Build Docker image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f app
```

### 3. Access Application

- **Application:** http://localhost:8000
- **Database:** localhost:5432 (if applicable)

### 4. Development Commands

```bash
# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Execute commands inside container
docker-compose exec app bash

# View logs
docker-compose logs -f app

# Restart specific service
docker-compose restart app
```

## Production Deployment

### 1. Server Setup

Ensure your production server has:
- Docker and Docker Compose installed
- Sufficient resources (CPU, RAM, disk)
- Firewall configured (ports 80, 443, 8000)
- Domain name configured (optional)

### 2. Security Configuration

```bash
# Generate secure secrets
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env with production values
SECRET_KEY=<generated-secret-key>
JWT_SECRET=<generated-jwt-secret>
DEBUG=false
APP_ENV=production
```

### 3. Build Production Image

```bash
# Build optimized production image
docker build -t webiascrap_v0.0.0:latest .

# Tag for registry (optional)
docker tag webiascrap_v0.0.0:latest registry.example.com/webiascrap_v0.0.0:latest
```

### 4. Deploy

```bash
# Start in production mode
docker-compose -f docker-compose.yml up -d

# Verify deployment
docker-compose ps
docker-compose logs -f
```

### 5. SSL/TLS Setup (HTTPS)

Add Nginx reverse proxy with Let's Encrypt:

```yaml
# Add to docker-compose.yml
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
```

## Cloud Deployment

### AWS ECS

```bash
# Install AWS CLI
pip install awscli

# Configure AWS
aws configure

# Push image to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag webiascrap_v0.0.0:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/webiascrap_v0.0.0:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/webiascrap_v0.0.0:latest

# Deploy to ECS using AWS Console or CLI
```

### Google Cloud Run

```bash
# Install gcloud CLI
# See: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Submit build
gcloud builds submit --tag gcr.io/PROJECT-ID/webiascrap_v0.0.0

# Deploy
gcloud run deploy webiascrap_v0.0.0 --image gcr.io/PROJECT-ID/webiascrap_v0.0.0 --platform managed
```

### DigitalOcean App Platform

```bash
# Install doctl
# See: https://docs.digitalocean.com/reference/doctl/how-to/install/

# Authenticate
doctl auth init

# Create app
doctl apps create --spec app.yaml
```

## Monitoring

### Container Health

```bash
# Check container status
docker-compose ps

# View resource usage
docker stats

# Check logs
docker-compose logs -f app

# Inspect container
docker inspect webiascrap_v0.0.0_app
```

### Application Monitoring

Consider adding:
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization
- **ELK Stack**: Log aggregation
- **Sentry**: Error tracking

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs app

# Verify environment variables
docker-compose config

# Remove and rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Issues

```bash
# Check database is running
docker-compose ps db

# Verify database credentials
docker-compose exec db psql -U admin -d webiascrap_v0.0.0

# Reset database
docker-compose down -v
docker-compose up -d
```

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :8000

# Kill process or change port in docker-compose.yml
```

### Performance Issues

```bash
# Increase container resources
docker-compose down
# Edit docker-compose.yml to add resource limits
docker-compose up -d

# Check resource usage
docker stats
```

## Backup and Recovery

### Database Backup

```bash
# Backup database
docker-compose exec db pg_dump -U admin webiascrap_v0.0.0 > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20240101.sql | docker-compose exec -T db psql -U admin webiascrap_v0.0.0
```

### Application Data

```bash
# Backup volumes
docker run --rm -v webiascrap_v0.0.0_data:/data -v $(pwd):/backup alpine tar czf /backup/data_backup.tar.gz /data

# Restore volumes
docker run --rm -v webiascrap_v0.0.0_data:/data -v $(pwd):/backup alpine tar xzf /backup/data_backup.tar.gz -C /
```

## Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose up -d --build
```

### Update Dependencies

```bash
# Rebuild image with updated dependencies
docker-compose build --no-cache
docker-compose up -d
```

### Clean Up

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove unused containers
docker container prune
```

---

For more information, consult the [README.md](README.md) or the official Docker documentation.
