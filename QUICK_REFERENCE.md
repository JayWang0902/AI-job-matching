# CI/CD Quick Reference

## 🚀 Common Commands

### On EC2 Server

```bash
# Navigate to project
cd ~/AI-job-matching

# Pull latest images and restart
docker compose pull && docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f backend
docker compose logs -f celery
docker compose logs -f frontend

# Restart specific service
docker compose restart backend

# Stop all services
docker compose down

# Rebuild from scratch (local only)
docker compose build --no-cache
docker compose up -d
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# From outside (replace with your domain)
curl http://your-domain.com:8000/health

# Check if containers are healthy
docker compose ps | grep healthy
```

### Rollback to Previous Version

```bash
# On EC2
cd ~/AI-job-matching

# Set specific version
export IMAGE_TAG=<commit-sha>  # e.g., a1b2c3d4
docker compose pull
docker compose up -d

# Or rollback code
git log --oneline  # Find commit
git reset --hard <commit-sha>
docker compose pull
docker compose up -d
```

### Cleanup

```bash
# Remove old images (keep last 3 days)
docker image prune -a --filter "until=72h"

# Remove build cache
docker builder prune -af

# Remove stopped containers
docker container prune -f

# Full cleanup (careful!)
docker system prune -af --volumes
```

## 🔧 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker compose logs <service>

# Check if port is in use
sudo netstat -tulpn | grep :8000

# Verify environment
docker compose config

# Restart specific service
docker compose restart <service>
```

### Images Not Pulling

```bash
# Login to registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Verify image exists
docker pull ghcr.io/jaywang0902/ai-job-matching-backend:latest

# Check environment variables
echo $DOCKER_REGISTRY
echo $IMAGE_TAG
```

### Permission Errors

```bash
# Fix file permissions for non-root containers
sudo chown -R 1000:1000 /path/to/volume
```

## 📊 Monitoring

### Check Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Image sizes
docker images | grep ai-job-matching
```

### Log Management

```bash
# Tail last 100 lines
docker compose logs --tail=100

# Follow specific service
docker compose logs -f backend

# Since specific time
docker compose logs --since 30m backend

# Save logs to file
docker compose logs > logs.txt
```

## 🔐 Security

### Update Secrets

```bash
# On EC2, edit .env
nano ~/AI-job-matching/.env

# Restart services to pick up changes
docker compose restart
```

### Check for Updates

```bash
# Pull latest code
git pull origin main

# Pull latest images
docker compose pull

# Restart with new versions
docker compose up -d
```

## 📝 Environment Variables Reference

### Required in .env on EC2

```bash
# Core Application
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=...
OPENAI_API_KEY=sk-...

# AWS S3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
S3_BUCKET_NAME=...

# Container Registry
DOCKER_REGISTRY=ghcr.io
DOCKER_IMAGE_PREFIX=jaywang0902/ai-job-matching
IMAGE_TAG=latest

# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://your-domain.com:8000
```

## 🎯 GitHub Actions

### Manually Trigger Deployment

1. Go to GitHub repository
2. Click "Actions" tab
3. Select "CI/CD Pipeline"
4. Click "Run workflow" → "Run workflow"

### View Deployment Status

```bash
# Check latest workflow
# Go to: https://github.com/JayWang0902/AI-job-matching/actions

# Or use GitHub CLI
gh run list
gh run view <run-id>
```

## 🔄 Workflow States

### Build Stage
- ✅ Checkout code
- ✅ Setup Docker Buildx
- ✅ Login to registry
- ✅ Build & push backend
- ✅ Build & push celery
- ✅ Build & push frontend

### Deploy Stage
- ✅ Setup SSH
- ✅ Connect to EC2
- ✅ Pull latest code
- ✅ Login to registry
- ✅ Pull new images
- ✅ Stop old containers
- ✅ Start new containers
- ✅ Health check
- ✅ Cleanup old images

## 📞 Emergency Procedures

### Service Down

```bash
# Quick restart
docker compose restart

# If that doesn't work
docker compose down
docker compose up -d

# If still failing, check logs
docker compose logs --tail=200
```

### Rollback Emergency

```bash
# On EC2
cd ~/AI-job-matching

# Quick rollback to previous commit
git reset --hard HEAD~1
docker compose down
docker compose up -d

# Or use specific commit
git reset --hard <previous-working-commit>
docker compose down
docker compose up -d
```

### Out of Disk Space

```bash
# Check disk usage
df -h
docker system df

# Aggressive cleanup
docker compose down
docker system prune -af --volumes

# Then redeploy
docker compose pull
docker compose up -d
```

## 🔗 Important URLs

- **Repository**: https://github.com/JayWang0902/AI-job-matching
- **Actions**: https://github.com/JayWang0902/AI-job-matching/actions
- **Container Registry**: https://github.com/JayWang0902?tab=packages
- **Health Check**: http://your-domain.com:8000/health

## 📚 Documentation Files

- `DEPLOYMENT_GUIDE.md` - Complete deployment documentation
- `MIGRATION_GUIDE.md` - Migration from old to new pipeline
- `CI_CD_IMPROVEMENTS.md` - Summary of all changes
- `README.md` - Project overview
- `.github/copilot-instructions.md` - Development guidelines

## 💡 Tips

- Always check logs first when troubleshooting
- Use `docker compose ps` to verify service status
- Keep your `.env` file backed up
- Test changes in staging before production
- Monitor disk space regularly
- Update images weekly for security patches

## 🆘 Getting Help

1. Check logs: `docker compose logs -f`
2. Verify environment: `docker compose config`
3. Check GitHub Actions for build failures
4. Review documentation files
5. Check GitHub Issues
