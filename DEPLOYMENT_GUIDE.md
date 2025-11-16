# Deployment Guide - Improved CI/CD Pipeline

## Overview

The deployment pipeline has been upgraded with modern best practices:

- ✅ **Multi-stage Docker builds** - Smaller, more secure images
- ✅ **Non-root users** - Enhanced container security
- ✅ **Registry-based deployment** - Faster deployments with immutable artifacts
- ✅ **Health checks** - Automated service health verification
- ✅ **Build caching** - Faster CI/CD pipeline execution
- ✅ **Proper dependency management** - Separate build and runtime dependencies

## Architecture

### New Workflow

```
GitHub Push → Build Images → Push to Registry → Deploy to EC2 → Health Check
```

**Previous workflow:**
```
GitHub Push → SSH to EC2 → Git Pull → Build on Server → Deploy
```

### Benefits of New Approach

1. **Faster Deployments**: Images are pre-built in CI, deploy only pulls and restarts
2. **Immutable Artifacts**: Same image used across environments
3. **Easy Rollback**: Can redeploy any previous image tag
4. **Better Testing**: Can test exact production image locally
5. **Security**: Build secrets never touch production server

## GitHub Actions Secrets Required

Configure these secrets in GitHub Settings → Secrets and variables → Actions:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `EC2_SSH_KEY` | Private SSH key for EC2 access | Your .pem file content |
| `EC2_HOST` | EC2 instance hostname or IP | `ec2-x-x-x-x.compute.amazonaws.com` |
| `EC2_USER` | SSH user on EC2 | `ubuntu` or `ec2-user` |
| `EC2_PROJECT_DIR` | Project directory on EC2 | `/home/ubuntu/AI-job-matching` |
| `HEALTH_URL` | Public health check URL | `http://your-domain.com:8000/health` |

**Note**: `GITHUB_TOKEN` is automatically provided by GitHub Actions.

## EC2 Server Setup

### 1. Install Docker & Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone Repository

```bash
cd ~
git clone https://github.com/JayWang0902/AI-job-matching.git
cd AI-job-matching
```

### 3. Create Production Environment File

```bash
cp .env.example .env
nano .env
```

Update with production values:
```bash
# JWT Configuration
SECRET_KEY=<generate-a-strong-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database (use managed RDS in production)
DATABASE_URL=postgresql://user:password@your-rds-endpoint:5432/dbname

# AWS S3
AWS_ACCESS_KEY_ID=<your-aws-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret>
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# OpenAI
OPENAI_API_KEY=sk-...

# Redis (use managed ElastiCache in production)
REDIS_URL=redis://your-elasticache-endpoint:6379/0

# Application
DEBUG=False
LOG_LEVEL=INFO

# Container Registry Settings
DOCKER_REGISTRY=ghcr.io
DOCKER_IMAGE_PREFIX=jaywang0902/ai-job-matching
IMAGE_TAG=latest

# API Base URL (for frontend)
NEXT_PUBLIC_API_BASE_URL=http://your-domain.com:8000
```

### 4. Set Up Docker Login on EC2

The workflow will handle login, but for manual operations:

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

### 5. Initial Deployment (Manual)

For the first deployment, you may need to run manually:

```bash
cd ~/AI-job-matching

# Pull latest code
git pull origin main

# Set environment variables for compose
export IMAGE_TAG=latest
export DOCKER_REGISTRY=ghcr.io
export DOCKER_IMAGE_PREFIX=jaywang0902/ai-job-matching

# Pull images
docker compose pull

# Start services
docker compose up -d

# Check status
docker compose ps
docker compose logs -f
```

## Local Development

### Build and Run Locally

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Run Individual Services

```bash
# Backend only
docker compose up -d backend

# Frontend only
docker compose up -d frontend

# Celery only
docker compose up -d celery
```

## Docker Images

### Image Naming Convention

```
ghcr.io/jaywang0902/ai-job-matching-backend:<commit-sha>
ghcr.io/jaywang0902/ai-job-matching-celery:<commit-sha>
ghcr.io/jaywang0902/ai-job-matching-frontend:<commit-sha>
```

Each push to `main` creates:
- A tagged image with the commit SHA (first 8 characters)
- A `latest` tag pointing to the most recent build

### Image Sizes (Approximate)

- **Backend**: ~300MB (was ~500MB)
- **Celery**: ~300MB (was ~500MB)
- **Frontend**: ~150MB (was ~400MB)

## Deployment Process

### Automatic Deployment (Recommended)

1. Push to `main` branch
2. GitHub Actions automatically:
   - Builds Docker images with multi-stage builds
   - Pushes to GitHub Container Registry (ghcr.io)
   - SSHs to EC2 server
   - Pulls new images
   - Restarts services with zero-downtime
   - Runs health checks
   - Cleans up old images

### Manual Deployment

If you need to deploy manually:

```bash
# On your local machine, trigger workflow manually via GitHub UI
# Or, SSH to server and:

ssh ubuntu@your-ec2-host

cd ~/AI-job-matching

# Pull latest images
export IMAGE_TAG=<commit-sha>  # or 'latest'
docker compose pull

# Restart services
docker compose up -d

# Check health
curl http://localhost:8000/health
```

### Rollback to Previous Version

```bash
# On EC2 server
cd ~/AI-job-matching

# Find previous image tag from GitHub Container Registry
export IMAGE_TAG=<previous-commit-sha>

# Pull old image
docker compose pull

# Restart with old image
docker compose up -d
```

## Monitoring & Logs

### Check Service Status

```bash
docker compose ps
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f celery
docker compose logs -f frontend

# Last 100 lines
docker compose logs --tail=100
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Check from outside (if exposed)
curl http://your-domain.com:8000/health
```

## Troubleshooting

### Images Not Pulling

```bash
# Verify you're logged in
docker login ghcr.io

# Check image exists
docker pull ghcr.io/jaywang0902/ai-job-matching-backend:latest

# Check compose file environment variables
echo $DOCKER_REGISTRY
echo $IMAGE_TAG
```

### Service Won't Start

```bash
# Check logs
docker compose logs backend

# Check if port is already in use
sudo netstat -tulpn | grep :8000

# Restart service
docker compose restart backend
```

### Health Check Failing

```bash
# Check if service is running
docker compose ps

# Check service logs
docker compose logs backend

# Test health endpoint manually
docker compose exec backend curl http://localhost:8000/health

# Check environment variables
docker compose exec backend env | grep DATABASE_URL
```

### Permission Issues

If you see permission errors with the new non-root user setup:

```bash
# The images now run as user 'appuser' (UID 1000)
# Ensure any mounted volumes have correct permissions
sudo chown -R 1000:1000 /path/to/volume
```

## Security Considerations

### What Changed

1. **Non-root containers**: All services now run as unprivileged users
2. **Multi-stage builds**: Build tools not included in runtime images
3. **Minimal base images**: Using `slim` variants to reduce attack surface
4. **Health checks**: Automated monitoring of service health
5. **Image signing**: All images include metadata and git SHA labels

### Best Practices

- ✅ Never commit `.env` with real secrets to Git
- ✅ Use AWS Secrets Manager or Parameter Store for production secrets
- ✅ Rotate secrets regularly
- ✅ Enable GitHub branch protection for `main`
- ✅ Use managed services (RDS, ElastiCache) in production
- ✅ Set up CloudWatch or similar for monitoring
- ✅ Enable Docker image scanning in GitHub

## Cost Optimization

### Image Storage

GitHub Container Registry provides:
- Free for public repositories
- 500MB free for private repositories
- Additional storage available

### EC2 Considerations

- Images are ~50% smaller, saving disk space
- Faster deployments reduce downtime
- Multi-stage builds use less build cache

## Next Steps

1. **Set up staging environment**: Create a separate branch/workflow for staging
2. **Add automated tests**: Extend workflow to run tests before deployment
3. **Implement blue-green deployment**: Zero-downtime deployments
4. **Set up monitoring**: CloudWatch, Datadog, or similar
5. **Database migrations**: Add Alembic migration steps to deployment
6. **CDN for frontend**: Use CloudFront for frontend assets
7. **Load balancer**: Add ALB for high availability

## Support

For issues or questions:
- Check GitHub Actions logs in the repository
- Review Docker logs on EC2: `docker compose logs`
- Open an issue in the GitHub repository
