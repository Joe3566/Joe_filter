# 🚀 Production Deployment Guide

Complete guide for deploying the Enterprise Compliance Filter to production environments.

## 🎯 Overview

This guide covers multiple deployment options:
- **Docker Compose** - Quick local/VPS deployment
- **AWS** - ECS, Elastic Beanstalk, EKS
- **Google Cloud** - Cloud Run, GKE
- **Microsoft Azure** - Container Instances, AKS
- **Heroku** - Platform-as-a-Service deployment

## 📋 Prerequisites

### Required Tools
```bash
# Core tools
docker --version          # Docker 20+
docker-compose --version  # Docker Compose 1.29+
git --version             # Git 2.30+

# Cloud-specific tools (install as needed)
aws --version             # AWS CLI v2
gcloud --version          # Google Cloud SDK
az --version              # Azure CLI
heroku --version          # Heroku CLI
kubectl version           # Kubernetes CLI
```

### Environment Variables
Create a `.env.production` file with required variables:

```bash
# Essential Configuration
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://user:pass@host:6379/0

# Security Settings
FORCE_HTTPS=true
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Performance Settings
GUNICORN_WORKERS=4
DEPLOYMENT_ENV=production

# Monitoring (Optional)
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_ENABLED=true

# OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id  
GITHUB_CLIENT_SECRET=your-github-client-secret
```

## 🐳 Docker Compose Deployment

### Quick Start
```bash
# 1. Clone and prepare
git clone https://github.com/Joe3566/enterprise-compliance-filter.git
cd enterprise-compliance-filter

# 2. Configure environment
cp .env.example .env.production
# Edit .env.production with your values

# 3. Deploy stack
docker-compose --env-file .env.production up -d

# 4. Check status
docker-compose ps
```

### Production Stack Services
- **app** - Main application (port 5000)
- **db** - PostgreSQL database (port 5432)
- **redis** - Redis cache (port 6379)
- **nginx** - Reverse proxy (ports 80/443)
- **prometheus** - Metrics collection (port 9090)
- **grafana** - Monitoring dashboard (port 3000)

### Custom Configurations

#### High Traffic Setup
```bash
DEPLOYMENT_ENV=high_traffic docker-compose up -d
```

#### Memory Optimized Setup
```bash
DEPLOYMENT_ENV=memory_optimized docker-compose up -d
```

#### With Monitoring
```bash
docker-compose --profile monitoring up -d
```

## ☁️ AWS Deployment

### Option 1: Amazon ECS (Recommended)
```bash
# Configure AWS credentials
aws configure

# Set environment variables
export AWS_REGION=us-east-1
export ENVIRONMENT=production
export DEPLOYMENT_TYPE=ecs

# Deploy
chmod +x deploy-aws.sh
./deploy-aws.sh
```

**Features:**
- ✅ Auto-scaling
- ✅ Load balancing
- ✅ Health checks
- ✅ Rolling updates
- ✅ Integration with AWS services

### Option 2: Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Deploy
export DEPLOYMENT_TYPE=eb
./deploy-aws.sh
```

**Features:**
- ✅ Simple deployment
- ✅ Auto-scaling
- ✅ Monitoring
- ✅ Easy configuration

### Option 3: Amazon EKS
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Deploy
export DEPLOYMENT_TYPE=eks
./deploy-aws.sh
```

**Features:**
- ✅ Kubernetes orchestration
- ✅ High availability
- ✅ Advanced networking
- ✅ Helm chart support

### AWS Resource Setup
```bash
# Create required AWS resources
export SETUP_RESOURCES=true
./deploy-aws.sh
```

This creates:
- RDS PostgreSQL instance
- ElastiCache Redis cluster
- ECR repository
- IAM roles
- Security groups

## 🌐 Google Cloud Deployment

### Cloud Run (Serverless)
```bash
# Configure gcloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/compliance-filter
gcloud run deploy compliance-filter \
  --image gcr.io/YOUR_PROJECT_ID/compliance-filter \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FLASK_ENV=production
```

### Google Kubernetes Engine (GKE)
```bash
# Create cluster
gcloud container clusters create compliance-cluster \
  --zone us-central1-a \
  --num-nodes 3

# Deploy
kubectl apply -f k8s/
```

## 💙 Microsoft Azure Deployment

### Container Instances
```bash
# Login to Azure
az login

# Create resource group
az group create --name compliance-rg --location eastus

# Deploy container
az container create \
  --resource-group compliance-rg \
  --name compliance-filter \
  --image your-registry/compliance-filter:latest \
  --dns-name-label compliance-filter \
  --ports 5000
```

### Azure Kubernetes Service (AKS)
```bash
# Create AKS cluster
az aks create \
  --resource-group compliance-rg \
  --name compliance-cluster \
  --node-count 3 \
  --generate-ssh-keys

# Deploy
kubectl apply -f k8s/
```

## 🟣 Heroku Deployment

### Quick Deploy
```bash
# Install Heroku CLI
npm install -g heroku

# Login and create app
heroku login
heroku create your-compliance-app

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=your-database-url

# Deploy
git push heroku main
```

### Heroku with Add-ons
```bash
# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis
heroku addons:create heroku-redis:hobby-dev

# Add monitoring
heroku addons:create sentry:f1
```

## 🔧 Production Configuration

### Database Setup

#### PostgreSQL Production Settings
```sql
-- Create database and user
CREATE DATABASE compliance_prod;
CREATE USER compliance_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE compliance_prod TO compliance_user;

-- Performance optimizations
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.7;
ALTER SYSTEM SET wal_buffers = '16MB';
```

#### Redis Production Settings
```bash
# Redis configuration for production
redis-cli CONFIG SET maxmemory 512mb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
redis-cli CONFIG SET save "900 1 300 10 60 10000"
```

### SSL/TLS Configuration

#### Let's Encrypt with Certbot
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificates
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Custom SSL Certificates
```bash
# Place certificates
cp your-cert.crt /etc/ssl/certs/
cp your-key.key /etc/ssl/private/

# Update environment
export SSL_CERT_PATH=/etc/ssl/certs/your-cert.crt
export SSL_KEY_PATH=/etc/ssl/private/your-key.key
```

## 📊 Monitoring Setup

### Prometheus + Grafana
```bash
# Deploy with monitoring
docker-compose --profile monitoring up -d

# Access dashboards
open http://localhost:9090  # Prometheus
open http://localhost:3000  # Grafana (admin/admin)
```

### Application Metrics
The application exposes metrics at `/metrics`:
- Request count and duration
- Cache hit rates
- Database connection pool
- Compliance filter performance

### Health Checks
- **Liveness**: `/health` - Application health
- **Readiness**: `/ready` - Ready to serve traffic
- **Metrics**: `/metrics` - Prometheus metrics

## 🚨 Production Checklist

### Security
- [ ] Environment variables configured
- [ ] HTTPS enabled with valid certificates
- [ ] Database credentials secured
- [ ] API keys in environment/secrets
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] CORS properly configured

### Performance
- [ ] Database optimized for production
- [ ] Redis caching configured
- [ ] CDN configured for static assets
- [ ] Gunicorn workers optimized
- [ ] Database connection pooling
- [ ] Application monitoring setup

### Reliability
- [ ] Health checks configured
- [ ] Auto-scaling policies set
- [ ] Backup strategy implemented
- [ ] Disaster recovery plan
- [ ] Load balancer configured
- [ ] Rolling deployment strategy

### Monitoring
- [ ] Application metrics collection
- [ ] Error tracking (Sentry)
- [ ] Log aggregation
- [ ] Performance monitoring
- [ ] Uptime monitoring
- [ ] Alerting configured

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Deploy to ECS
      run: |
        chmod +x deploy-aws.sh
        ./deploy-aws.sh
```

## 📞 Support & Troubleshooting

### Common Issues

#### Database Connection
```bash
# Test database connection
docker-compose exec app python -c "from auth_system import AuthSystem; print('✅ DB OK' if AuthSystem().db else '❌ DB Failed')"
```

#### Redis Connection
```bash
# Test Redis connection
docker-compose exec redis redis-cli ping
```

#### Application Health
```bash
# Check application health
curl http://localhost:5000/health
curl http://localhost:5000/ready
```

### Logs
```bash
# View application logs
docker-compose logs app -f

# View specific service logs
docker-compose logs db redis nginx
```

### Performance Tuning
```bash
# Monitor resource usage
docker stats

# Check database performance
docker-compose exec db pg_stat_statements

# Monitor cache performance
docker-compose exec redis redis-cli info stats
```

## 🎉 Success Metrics

After successful deployment, you should see:
- ✅ Application responding at your domain
- ✅ Health checks passing
- ✅ Authentication working
- ✅ Database connections stable
- ✅ Cache hit rate > 80%
- ✅ Response times < 200ms
- ✅ Error rate < 0.1%

---

**🚀 Congratulations! Your Enterprise Compliance Filter is production-ready!**

For support, open an issue at: https://github.com/Joe3566/enterprise-compliance-filter/issues