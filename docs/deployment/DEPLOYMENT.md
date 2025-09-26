
# Deployment Guide

## Quick Production Deployment

1. **Prepare Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Deploy with Docker**:
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

3. **Set up SSL**:
   ```bash
   # Install certbot
   sudo apt install certbot python3-certbot-nginx
   
   # Get SSL certificate
   sudo certbot --nginx -d your-domain.com
   ```

4. **Start Monitoring**:
   ```bash
   docker-compose -f docker-compose.monitoring.yml up -d
   ```

5. **Set up Automated Backups**:
   ```bash
   # Add to crontab
   0 2 * * * /path/to/scripts/backup.sh
   ```

## Kubernetes Deployment

1. **Apply manifests**:
   ```bash
   kubectl apply -f k8s/
   ```

2. **Create secrets**:
   ```bash
   kubectl create secret generic db-secrets \
     --from-literal=database=vip_ride_platform \
     --from-literal=username=postgres \
     --from-literal=password=your-password \
     -n vip-ride-platform
   ```

## Monitoring URLs

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin123)
- Application: https://your-domain.com
