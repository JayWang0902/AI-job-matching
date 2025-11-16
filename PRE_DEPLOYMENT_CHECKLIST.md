# Pre-Deployment Checklist

## Before You Deploy

### ☑️ GitHub Configuration

- [ ] Verify GitHub Secrets are configured
  - [ ] `EC2_SSH_KEY` exists
  - [ ] `EC2_HOST` exists
  - [ ] `EC2_USER` exists
  - [ ] `EC2_PROJECT_DIR` exists
  - [ ] `HEALTH_URL` exists
- [ ] Repository has GitHub Packages (Container Registry) enabled
- [ ] Your GitHub user has write access to packages

### ☑️ EC2 Server Preparation

- [ ] SSH access to server works
  ```bash
  ssh ubuntu@your-ec2-host
  ```
- [ ] Docker is installed and running
  ```bash
  docker --version
  docker compose version
  ```
- [ ] Project directory exists
  ```bash
  cd ~/AI-job-matching
  ```
- [ ] Current `.env` file is backed up
  ```bash
  cp .env .env.backup
  ```
- [ ] Git is configured
  ```bash
  git pull origin main  # Should work without errors
  ```

### ☑️ Environment Variables

- [ ] `.env` file on EC2 has all required variables
  - [ ] `DATABASE_URL` (pointing to RDS or managed DB)
  - [ ] `REDIS_URL` (pointing to ElastiCache or managed Redis)
  - [ ] `SECRET_KEY` (strong secret, not default)
  - [ ] `OPENAI_API_KEY` (valid API key)
  - [ ] `AWS_ACCESS_KEY_ID` (valid AWS credentials)
  - [ ] `AWS_SECRET_ACCESS_KEY` (valid AWS credentials)
  - [ ] `S3_BUCKET_NAME` (existing bucket)

- [ ] New variables added to `.env`:
  ```bash
  DOCKER_REGISTRY=ghcr.io
  DOCKER_IMAGE_PREFIX=jaywang0902/ai-job-matching
  IMAGE_TAG=latest
  NEXT_PUBLIC_API_BASE_URL=http://your-domain.com:8000
  ```

### ☑️ Service Availability

- [ ] Database is accessible from EC2
  ```bash
  # Test connection
  psql $DATABASE_URL -c "SELECT 1"
  ```
- [ ] Redis is accessible from EC2
  ```bash
  # Test connection
  redis-cli -u $REDIS_URL ping
  ```
- [ ] S3 bucket is accessible
  ```bash
  aws s3 ls s3://$S3_BUCKET_NAME
  ```
- [ ] OpenAI API key is valid
  ```bash
  curl https://api.openai.com/v1/models \
    -H "Authorization: Bearer $OPENAI_API_KEY"
  ```

### ☑️ Backup Current State

- [ ] Current `.env` backed up
- [ ] Database backed up (if applicable)
  ```bash
  pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
  ```
- [ ] Current git commit noted
  ```bash
  git log -1 --oneline
  ```
- [ ] Current running images noted
  ```bash
  docker compose images > images_backup.txt
  ```

## During Deployment

### ☑️ Code Update

- [ ] Pull latest code on EC2
  ```bash
  cd ~/AI-job-matching
  git pull origin main
  ```
- [ ] Verify new files exist
  ```bash
  ls -la Dockerfile
  ls -la docker-compose.yml
  ls -la .github/workflows/deploy.yml
  ```

### ☑️ First Build (Manual or Auto)

Choose ONE:

**Option A: Automatic (Recommended)**
- [ ] Push commit to trigger GitHub Actions
  ```bash
  git commit --allow-empty -m "Deploy new CI/CD pipeline"
  git push origin main
  ```
- [ ] Watch GitHub Actions progress
  - Go to: https://github.com/JayWang0902/AI-job-matching/actions
  - Monitor build and deploy jobs

**Option B: Manual First Build**
- [ ] Stop current containers
  ```bash
  docker compose down
  ```
- [ ] Build new images locally
  ```bash
  docker compose build
  ```
- [ ] Start services
  ```bash
  docker compose up -d
  ```

### ☑️ Health Verification

- [ ] Check container status
  ```bash
  docker compose ps
  # All should show "Up" and backend should be "healthy"
  ```
- [ ] Check logs for errors
  ```bash
  docker compose logs backend | tail -50
  docker compose logs celery | tail -50
  docker compose logs frontend | tail -50
  ```
- [ ] Test backend health endpoint
  ```bash
  curl http://localhost:8000/health
  # Should return {"status": "healthy"}
  ```
- [ ] Test frontend
  ```bash
  curl http://localhost:3000
  # Should return HTML
  ```
- [ ] Test from external network
  ```bash
  curl http://your-domain.com:8000/health
  ```

## Post-Deployment Verification

### ☑️ Application Testing

- [ ] Can login to application
- [ ] Can upload resume
- [ ] Backend API responding correctly
- [ ] Frontend loads properly
- [ ] Celery tasks are running
  ```bash
  docker compose logs celery | grep "ready"
  ```

### ☑️ System Health

- [ ] Containers running as non-root
  ```bash
  docker compose exec backend whoami
  # Should output: appuser (not root)
  ```
- [ ] Health checks passing
  ```bash
  docker compose ps | grep healthy
  ```
- [ ] No errors in logs
  ```bash
  docker compose logs --tail=100 | grep -i error
  ```
- [ ] Disk space reasonable
  ```bash
  docker system df
  df -h
  ```

### ☑️ Performance Check

- [ ] Response time acceptable
  ```bash
  time curl http://localhost:8000/health
  # Should be < 1 second
  ```
- [ ] Memory usage reasonable
  ```bash
  docker stats --no-stream
  ```
- [ ] No restart loops
  ```bash
  docker compose ps
  # Check "Status" - should not show "Restarting"
  ```

## Rollback Plan (If Needed)

### ☑️ Quick Rollback Steps

If something goes wrong:

1. [ ] Stop current deployment
   ```bash
   docker compose down
   ```

2. [ ] Restore previous code
   ```bash
   git log --oneline
   git reset --hard <previous-commit>
   ```

3. [ ] Restore `.env` if changed
   ```bash
   cp .env.backup .env
   ```

4. [ ] Rebuild and restart
   ```bash
   docker compose build
   docker compose up -d
   ```

5. [ ] Verify rollback worked
   ```bash
   docker compose ps
   curl http://localhost:8000/health
   ```

## After Successful Deployment

### ☑️ Cleanup

- [ ] Remove old images
  ```bash
  docker image prune -a --filter "until=72h"
  ```
- [ ] Remove old containers
  ```bash
  docker container prune -f
  ```
- [ ] Check disk space
  ```bash
  df -h
  ```

### ☑️ Monitoring Setup

- [ ] Set up CloudWatch logs (if using AWS)
- [ ] Configure alerts for container failures
- [ ] Set up uptime monitoring
- [ ] Document any issues encountered

### ☑️ Documentation

- [ ] Update internal docs with new deploy process
- [ ] Note any configuration changes made
- [ ] Document rollback commit if needed
- [ ] Share new deployment process with team

## Success Criteria

Deployment is successful when:

- ✅ GitHub Actions workflow completed successfully
- ✅ All containers are running and healthy
- ✅ Health endpoint returns 200 OK
- ✅ Application is accessible from browser
- ✅ Can perform key user actions (login, upload, etc.)
- ✅ No errors in logs
- ✅ Celery is processing tasks
- ✅ Response times are normal

## Common Issues & Solutions

### Issue: Images not pulling from registry

**Solution:**
```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
docker compose pull
```

### Issue: Permission denied errors

**Solution:**
```bash
# Fix ownership for non-root containers
sudo chown -R 1000:1000 /path/to/mounted/volumes
```

### Issue: Health check failing

**Solution:**
```bash
# Check if /health endpoint exists
docker compose exec backend curl http://localhost:8000/health

# Check backend logs
docker compose logs backend --tail=100

# Verify environment variables
docker compose exec backend env | grep DATABASE_URL
```

### Issue: Frontend can't reach backend

**Solution:**
```bash
# Verify NEXT_PUBLIC_API_BASE_URL in .env
echo $NEXT_PUBLIC_API_BASE_URL

# Should be either:
# - http://backend:8000 (internal)
# - http://your-domain.com:8000 (external)
```

## Contact

If you encounter issues:
- Check documentation: `DEPLOYMENT_GUIDE.md`, `MIGRATION_GUIDE.md`
- Review logs: `docker compose logs`
- Check GitHub Actions: https://github.com/JayWang0902/AI-job-matching/actions

---

**Good luck with your deployment! 🚀**
