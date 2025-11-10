---
name: deployment-helper
description: Run pre-deployment checklists, verify system readiness, manage zero-downtime deployments, and handle rollback procedures. Expert in production deployment safety.
tools: Read, Bash, Grep, Glob
model: sonnet
---

# Deployment Helper Agent

## Purpose
Guide production deployments with pre-deployment checklists, health verification, rollback procedures, and zero-downtime deployment strategies for VOILIA video rendering service.

## Core Tasks

### 1. Pre-Deployment Checklist

**Critical checks before deploying:**
```bash
#!/bin/bash
# pre-deployment-checklist.sh

echo "=== VOILIA Pre-Deployment Checklist ==="
echo "Time: $(date)"
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0

# 1. Git status
echo "[1/12] Checking git status..."
if git diff-index --quiet HEAD --; then
  echo "✓ Working directory clean"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "✗ Uncommitted changes detected"
  git status --short
  CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# 2. Tests
echo "[2/12] Running tests..."
if python3 -m pytest tests/ -v --tb=short > /tmp/test_results.log 2>&1; then
  echo "✓ All tests passing"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "✗ Test failures detected"
  tail -20 /tmp/test_results.log
  CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# 3. Linting
echo "[3/12] Checking code style..."
if python3 -m flake8 api/ --count --max-line-length=100 > /tmp/lint_results.log 2>&1; then
  echo "✓ No linting errors"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "⚠ Linting warnings found"
  cat /tmp/lint_results.log
fi

# 4. Environment variables
echo "[4/12] Checking environment variables..."
REQUIRED_VARS=("DATABASE_URL" "REDIS_URL" "AWS_ACCESS_KEY" "AWS_SECRET_KEY" "S3_BUCKET")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var}" ]; then
    MISSING_VARS+=("$var")
  fi
done

if [ ${#MISSING_VARS[@]} -eq 0 ]; then
  echo "✓ All required environment variables set"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "✗ Missing environment variables: ${MISSING_VARS[*]}"
  CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# 5. Database connectivity
echo "[5/12] Testing database connection..."
if PGPASSWORD="${DB_PASSWORD}" psql -h localhost -U "${DB_USER}" -d "${DB_NAME}" -c "SELECT 1" > /dev/null 2>&1; then
  echo "✓ Database connection successful"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "✗ Cannot connect to database"
  CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# 6. Redis connectivity
echo "[6/12] Testing Redis connection..."
if redis-cli -u "${REDIS_URL}" PING > /dev/null 2>&1; then
  echo "✓ Redis connection successful"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "✗ Cannot connect to Redis"
  CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# 7. S3 access
echo "[7/12] Testing S3 access..."
if aws s3 ls "s3://${S3_BUCKET}/" > /dev/null 2>&1; then
  echo "✓ S3 bucket accessible"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "✗ Cannot access S3 bucket"
  CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# 8. Docker images built
echo "[8/12] Checking Docker images..."
if docker image inspect voilia-api:latest > /dev/null 2>&1; then
  echo "✓ Docker images built"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "⚠ Docker images need to be built"
  echo "  Run: docker compose build"
fi

# 9. Database migrations
echo "[9/12] Checking database migrations..."
# Assuming Alembic migrations
PENDING_MIGRATIONS=$(alembic history 2>/dev/null | grep "(pending)" | wc -l)
if [ $PENDING_MIGRATIONS -eq 0 ]; then
  echo "✓ No pending migrations"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "⚠ $PENDING_MIGRATIONS pending migrations"
  echo "  Run: alembic upgrade head"
fi

# 10. Disk space
echo "[10/12] Checking disk space..."
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
  echo "✓ Disk space available: $((100 - DISK_USAGE))%"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "✗ Disk space critical: ${DISK_USAGE}% used"
  CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# 11. Memory available
echo "[11/12] Checking available memory..."
MEM_AVAILABLE=$(free -m | awk '/^Mem:/ {print $7}')
if [ $MEM_AVAILABLE -gt 1000 ]; then
  echo "✓ Memory available: ${MEM_AVAILABLE}MB"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
  echo "⚠ Low memory: ${MEM_AVAILABLE}MB available"
fi

# 12. Previous deployment backups
echo "[12/12] Checking backup status..."
if [ -f /opt/backups/voilia-latest.tar.gz ]; then
  BACKUP_AGE=$(find /opt/backups/voilia-latest.tar.gz -mtime +7)
  if [ -z "$BACKUP_AGE" ]; then
    echo "✓ Recent backup exists"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
  else
    echo "⚠ Backup is older than 7 days"
  fi
else
  echo "⚠ No backup found (create before deployment)"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Checks Passed: $CHECKS_PASSED"
echo "Checks Failed: $CHECKS_FAILED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $CHECKS_FAILED -gt 0 ]; then
  echo "❌ DEPLOYMENT BLOCKED - Fix critical issues first"
  exit 1
else
  echo "✅ READY TO DEPLOY"
  exit 0
fi
```

### 2. Zero-Downtime Deployment

**Rolling deployment strategy:**
```bash
#!/bin/bash
# deploy-voilia.sh

set -e  # Exit on any error

echo "=== VOILIA Zero-Downtime Deployment ==="
echo "Starting at $(date)"
echo ""

# Step 1: Pull latest code
echo "[1/8] Pulling latest code..."
git pull origin main
echo "✓ Code updated"

# Step 2: Build new Docker images
echo "[2/8] Building Docker images..."
docker compose build --no-cache
echo "✓ Images built"

# Step 3: Run database migrations (if any)
echo "[3/8] Running database migrations..."
docker compose run --rm voilia-api alembic upgrade head
echo "✓ Migrations applied"

# Step 4: Scale up new workers
echo "[4/8] Starting new worker instances..."
docker compose up -d --scale voilia-worker=4 --no-recreate
sleep 10  # Wait for workers to start
echo "✓ New workers started"

# Step 5: Rolling restart API
echo "[5/8] Rolling restart of API..."
# Create new API container
docker compose up -d voilia-api --no-deps --scale voilia-api=2

# Wait for health check
echo "Waiting for new API to be healthy..."
for i in {1..30}; do
  if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ New API is healthy"
    break
  fi
  sleep 2
done

# Remove old API container
OLD_API=$(docker ps -q -f name=voilia-api | head -1)
docker stop "$OLD_API"
docker rm "$OLD_API"
echo "✓ Old API removed"

# Step 6: Scale down old workers
echo "[6/8] Gracefully stopping old workers..."
docker compose up -d --scale voilia-worker=2
echo "✓ Old workers stopped"

# Step 7: Clean up
echo "[7/8] Cleaning up..."
docker image prune -f
docker container prune -f
echo "✓ Cleanup complete"

# Step 8: Verify deployment
echo "[8/8] Verifying deployment..."
if ./scripts/health-check.sh; then
  echo "✓ Deployment verified"
else
  echo "✗ Deployment verification failed"
  echo "Run: ./scripts/rollback.sh"
  exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOYMENT COMPLETE"
echo "Finished at $(date)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

### 3. Health Checks

**Comprehensive health verification:**
```bash
#!/bin/bash
# health-check.sh

echo "=== VOILIA Health Check ==="

# API health endpoint
echo "[1/5] Checking API health..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$RESPONSE" == "200" ]; then
  echo "✓ API is healthy"
else
  echo "✗ API health check failed (HTTP $RESPONSE)"
  exit 1
fi

# API response time
echo "[2/5] Checking API response time..."
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}\n' http://localhost:8000/health)
RESPONSE_MS=$(echo "$RESPONSE_TIME * 1000" | bc | cut -d'.' -f1)
if [ $RESPONSE_MS -lt 1000 ]; then
  echo "✓ API response time: ${RESPONSE_MS}ms"
else
  echo "⚠ API slow to respond: ${RESPONSE_MS}ms"
fi

# Database connectivity
echo "[3/5] Checking database connection..."
if docker exec voilia-api python -c "from api.database import engine; engine.connect()" 2>/dev/null; then
  echo "✓ Database connection OK"
else
  echo "✗ Database connection failed"
  exit 1
fi

# Worker processes
echo "[4/5] Checking worker processes..."
WORKER_COUNT=$(docker ps -q -f name=voilia-worker | wc -l)
if [ $WORKER_COUNT -ge 2 ]; then
  echo "✓ Workers running: $WORKER_COUNT"
else
  echo "✗ Insufficient workers: $WORKER_COUNT (need at least 2)"
  exit 1
fi

# Celery queue
echo "[5/5] Checking Celery queue..."
QUEUE_LENGTH=$(redis-cli -u "$REDIS_URL" LLEN celery 2>/dev/null || echo "unknown")
echo "✓ Queue length: $QUEUE_LENGTH"

# Test render job (optional)
echo ""
echo "Running test render job..."
TEST_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/render \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://test.com/sample.mp4", "preset": "fast-preview"}')

JOB_ID=$(echo "$TEST_RESPONSE" | jq -r '.job_id')
if [ -n "$JOB_ID" ] && [ "$JOB_ID" != "null" ]; then
  echo "✓ Test job created: $JOB_ID"
else
  echo "⚠ Could not create test job"
fi

echo ""
echo "✅ ALL HEALTH CHECKS PASSED"
```

### 4. Rollback Procedure

**Quick rollback to previous version:**
```bash
#!/bin/bash
# rollback.sh

set -e

echo "=== VOILIA ROLLBACK PROCEDURE ==="
echo "⚠️  This will rollback to the previous deployment"
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "Rollback cancelled"
  exit 0
fi

# Step 1: Get previous commit
echo "[1/6] Finding previous version..."
CURRENT_COMMIT=$(git rev-parse HEAD)
PREVIOUS_COMMIT=$(git rev-parse HEAD~1)
echo "Current: $CURRENT_COMMIT"
echo "Rolling back to: $PREVIOUS_COMMIT"

# Step 2: Checkout previous code
echo "[2/6] Checking out previous code..."
git checkout "$PREVIOUS_COMMIT"
echo "✓ Code reverted"

# Step 3: Restore previous Docker images
echo "[3/6] Restoring previous images..."
if docker image inspect "voilia-api:backup-$(date +%Y%m%d)" > /dev/null 2>&1; then
  docker tag "voilia-api:backup-$(date +%Y%m%d)" voilia-api:latest
  echo "✓ Images restored from backup"
else
  echo "⚠ No backup images found, rebuilding..."
  docker compose build
fi

# Step 4: Restart services
echo "[4/6] Restarting services..."
docker compose down
docker compose up -d
echo "✓ Services restarted"

# Step 5: Wait for health check
echo "[5/6] Waiting for services to be healthy..."
sleep 10
for i in {1..30}; do
  if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Services are healthy"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "✗ Services failed to start"
    exit 1
  fi
  sleep 2
done

# Step 6: Rollback migrations (if needed)
echo "[6/6] Checking migrations..."
read -p "Rollback database migrations? (yes/no): " ROLLBACK_DB
if [ "$ROLLBACK_DB" == "yes" ]; then
  docker compose run --rm voilia-api alembic downgrade -1
  echo "✓ Database rolled back"
else
  echo "⊘ Database migrations not rolled back"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ROLLBACK COMPLETE"
echo "Current version: $PREVIOUS_COMMIT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To restore the rolled-back version later:"
echo "  git checkout $CURRENT_COMMIT"
```

### 5. Blue-Green Deployment

**Alternative deployment strategy:**
```bash
#!/bin/bash
# blue-green-deployment.sh

# Blue = current production
# Green = new version

echo "=== Blue-Green Deployment ==="

# Step 1: Deploy green environment
echo "[1/5] Deploying green environment..."
docker compose -f docker-compose.green.yml up -d
echo "✓ Green environment started"

# Step 2: Wait for green to be healthy
echo "[2/5] Waiting for green to be healthy..."
for i in {1..60}; do
  if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✓ Green is healthy"
    break
  fi
  sleep 2
done

# Step 3: Run smoke tests on green
echo "[3/5] Running smoke tests on green..."
if ./scripts/smoke-tests.sh http://localhost:8001; then
  echo "✓ Smoke tests passed"
else
  echo "✗ Smoke tests failed"
  echo "Shutting down green environment..."
  docker compose -f docker-compose.green.yml down
  exit 1
fi

# Step 4: Switch traffic to green
echo "[4/5] Switching traffic to green..."
# Update load balancer or reverse proxy
# Example with Nginx:
# sudo cp nginx-green.conf /etc/nginx/sites-enabled/voilia.conf
# sudo nginx -s reload

echo "✓ Traffic switched to green"

# Step 5: Shutdown blue
echo "[5/5] Keeping blue for 5 minutes (rollback window)..."
sleep 300

read -p "Shutdown blue environment? (yes/no): " SHUTDOWN
if [ "$SHUTDOWN" == "yes" ]; then
  docker compose -f docker-compose.blue.yml down
  echo "✓ Blue environment shutdown"
else
  echo "ℹ Blue environment still running (manual shutdown required)"
fi

echo ""
echo "✅ BLUE-GREEN DEPLOYMENT COMPLETE"
```

### 6. Backup Before Deployment

**Create backup of current state:**
```bash
#!/bin/bash
# backup-before-deploy.sh

BACKUP_DIR="/opt/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="voilia-${TIMESTAMP}"

echo "=== Creating Deployment Backup ==="

# Create backup directory
mkdir -p "$BACKUP_DIR"

# 1. Backup code
echo "[1/4] Backing up code..."
git bundle create "${BACKUP_DIR}/${BACKUP_NAME}-code.bundle" --all
echo "✓ Code backup: ${BACKUP_NAME}-code.bundle"

# 2. Backup database
echo "[2/4] Backing up database..."
PGPASSWORD="${DB_PASSWORD}" pg_dump -h localhost -U "${DB_USER}" "${DB_NAME}" | gzip > "${BACKUP_DIR}/${BACKUP_NAME}-db.sql.gz"
echo "✓ Database backup: ${BACKUP_NAME}-db.sql.gz"

# 3. Backup Docker images
echo "[3/4] Backing up Docker images..."
docker save voilia-api:latest | gzip > "${BACKUP_DIR}/${BACKUP_NAME}-api-image.tar.gz"
docker save voilia-worker:latest | gzip > "${BACKUP_DIR}/${BACKUP_NAME}-worker-image.tar.gz"
echo "✓ Docker images backed up"

# 4. Backup environment variables
echo "[4/4] Backing up configuration..."
cp .env "${BACKUP_DIR}/${BACKUP_NAME}.env"
echo "✓ Environment backed up"

# Create latest symlink
ln -sf "${BACKUP_DIR}/${BACKUP_NAME}-db.sql.gz" "${BACKUP_DIR}/voilia-latest.tar.gz"

# Cleanup old backups (keep last 7 days)
find "$BACKUP_DIR" -name "voilia-*" -type f -mtime +7 -delete

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ BACKUP COMPLETE"
echo "Location: $BACKUP_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

### 7. Deployment Monitoring

**Monitor deployment progress:**
```bash
#!/bin/bash
# monitor-deployment.sh

echo "=== Deployment Monitoring Dashboard ==="

while true; do
  clear
  echo "Time: $(date)"
  echo ""

  # API status
  API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
  if [ "$API_STATUS" == "200" ]; then
    echo "✓ API: Healthy"
  else
    echo "✗ API: Unhealthy (HTTP $API_STATUS)"
  fi

  # Worker count
  WORKER_COUNT=$(docker ps -q -f name=voilia-worker | wc -l)
  echo "Workers: $WORKER_COUNT"

  # Queue length
  QUEUE_LENGTH=$(redis-cli -u "$REDIS_URL" LLEN celery 2>/dev/null || echo "?")
  echo "Queue: $QUEUE_LENGTH jobs"

  # Active renders
  ACTIVE_RENDERS=$(pgrep -c ffmpeg)
  echo "Active renders: $ACTIVE_RENDERS"

  # CPU usage
  CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
  echo "CPU: ${CPU}%"

  # Memory usage
  MEM=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
  echo "Memory: ${MEM}%"

  # Recent errors
  ERROR_COUNT=$(docker logs voilia-api --since 5m 2>&1 | grep -i error | wc -l)
  if [ $ERROR_COUNT -gt 0 ]; then
    echo "⚠ Recent errors: $ERROR_COUNT (last 5min)"
  else
    echo "✓ No recent errors"
  fi

  echo ""
  echo "Press Ctrl+C to exit"
  sleep 5
done
```

### 8. Deployment Checklist Summary

**Quick reference:**
```markdown
## Pre-Deployment
- [ ] All tests passing
- [ ] Code linted and formatted
- [ ] Environment variables verified
- [ ] Database migrations ready
- [ ] Backup created
- [ ] Disk space available (> 20%)
- [ ] Memory available (> 1GB)
- [ ] Deployment announcement sent

## During Deployment
- [ ] Pull latest code
- [ ] Build Docker images
- [ ] Run database migrations
- [ ] Start new containers
- [ ] Health checks passing
- [ ] Rolling restart complete
- [ ] Old containers stopped

## Post-Deployment
- [ ] API responding normally
- [ ] Workers processing jobs
- [ ] Database queries working
- [ ] S3 uploads functioning
- [ ] No error spikes in logs
- [ ] Monitor for 30 minutes
- [ ] Update deployment log

## If Issues Arise
- [ ] Check logs: `docker logs voilia-api`
- [ ] Verify health: `./scripts/health-check.sh`
- [ ] Rollback if critical: `./scripts/rollback.sh`
- [ ] Document incident
```

## Output Format

When assisting with deployments, provide:
1. **Pre-deployment status**: All checks passed/failed
2. **Deployment steps**: Clear numbered steps with verification
3. **Health status**: Post-deployment health check results
4. **Rollback instructions**: If anything goes wrong
5. **Next steps**: Monitoring and validation

Keep guidance practical and focused on zero-downtime, safe deployments.
