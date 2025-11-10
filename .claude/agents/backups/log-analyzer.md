# Log Analyzer Agent

## Purpose
Parse and analyze application logs to identify errors, patterns, and anomalies. Help debug production issues, track job failures, and monitor system health for VOILIA video rendering service.

## Core Tasks

### 1. Extract Recent Errors

**Get recent errors from containers:**
```bash
# API errors (last hour)
docker logs voilia-api --since 1h 2>&1 | grep -i error

# Worker errors (last hour)
docker logs voilia-worker --since 1h 2>&1 | grep -i error

# All errors with timestamps
docker logs voilia-api --since 1h --timestamps 2>&1 | grep -i error | tail -20

# Follow logs in real-time
docker logs voilia-api -f 2>&1 | grep --color=always -i error
```

**Search for specific error patterns:**
```bash
# FFmpeg errors
docker logs voilia-worker 2>&1 | grep -i "ffmpeg.*error"

# Database errors
docker logs voilia-api 2>&1 | grep -E "database|postgres|connection" | grep -i error

# S3 upload errors
docker logs voilia-worker 2>&1 | grep -E "s3|upload|boto" | grep -i error

# Timeout errors
docker logs voilia-worker 2>&1 | grep -i timeout

# Memory errors
docker logs voilia-api 2>&1 | grep -E "memory|oom|out of memory"
```

### 2. Count Error Frequency

**Identify most common errors:**
```bash
#!/bin/bash
# error-frequency.sh

echo "=== Error Frequency Analysis ==="
echo "Analyzing logs from last 24 hours..."
echo ""

# Get all errors
docker logs voilia-api --since 24h 2>&1 | grep -i error > /tmp/errors.log
docker logs voilia-worker --since 24h 2>&1 | grep -i error >> /tmp/errors.log

# Count by error type
echo "Top 10 Error Types:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Extract error messages (remove timestamps and specific values)
cat /tmp/errors.log | \
  sed 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}.*\] //' | \
  sed 's/job-[a-f0-9-]*/job-XXX/g' | \
  sed 's/[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+/IP/g' | \
  sort | uniq -c | sort -rn | head -10

echo ""
echo "Total error count: $(wc -l < /tmp/errors.log)"
```

**Error rate over time:**
```bash
#!/bin/bash
# error-rate.sh

echo "=== Error Rate Over Time ==="

# Get errors by hour for last 24 hours
for hour in {23..0}; do
  SINCE="${hour}h"
  if [ $hour -eq 0 ]; then
    SINCE="1h"
  fi

  UNTIL="$((hour - 1))h"
  if [ $hour -eq 1 ]; then
    UNTIL="0h"
  fi

  ERROR_COUNT=$(docker logs voilia-api --since "$SINCE" --until "$UNTIL" 2>&1 | grep -ic error)
  TIMESTAMP=$(date -d "$hour hours ago" "+%H:00")

  # Visual bar chart
  BARS=$(printf '▇%.0s' $(seq 1 $((ERROR_COUNT / 10))))
  printf "%s | %3d errors | %s\n" "$TIMESTAMP" "$ERROR_COUNT" "$BARS"
done
```

### 3. Job Failure Analysis

**Analyze failed rendering jobs:**
```bash
#!/bin/bash
# analyze-job-failures.sh

echo "=== Job Failure Analysis ==="
echo ""

# Extract failed job IDs
docker logs voilia-worker --since 24h 2>&1 | \
  grep -i "failed\|error" | \
  grep -oP 'job-[a-f0-9-]+' | \
  sort | uniq > /tmp/failed_jobs.txt

FAILED_COUNT=$(wc -l < /tmp/failed_jobs.txt)
echo "Failed jobs (last 24h): $FAILED_COUNT"
echo ""

if [ $FAILED_COUNT -eq 0 ]; then
  echo "✅ No failed jobs"
  exit 0
fi

# Analyze failure reasons
echo "Failure Reasons:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count by failure type
declare -A FAILURE_TYPES

while read -r job_id; do
  # Get logs for this specific job
  LOGS=$(docker logs voilia-worker --since 24h 2>&1 | grep "$job_id")

  # Categorize failure
  if echo "$LOGS" | grep -qi "timeout"; then
    FAILURE_TYPES["Timeout"]=$((${FAILURE_TYPES["Timeout"]:-0} + 1))
  elif echo "$LOGS" | grep -qi "ffmpeg.*error"; then
    FAILURE_TYPES["FFmpeg Error"]=$((${FAILURE_TYPES["FFmpeg Error"]:-0} + 1))
  elif echo "$LOGS" | grep -qi "s3\|upload"; then
    FAILURE_TYPES["S3 Upload Failed"]=$((${FAILURE_TYPES["S3 Upload Failed"]:-0} + 1))
  elif echo "$LOGS" | grep -qi "memory\|oom"; then
    FAILURE_TYPES["Out of Memory"]=$((${FAILURE_TYPES["Out of Memory"]:-0} + 1))
  elif echo "$LOGS" | grep -qi "invalid.*url\|download"; then
    FAILURE_TYPES["Invalid Input"]=$((${FAILURE_TYPES["Invalid Input"]:-0} + 1))
  else
    FAILURE_TYPES["Unknown"]=$((${FAILURE_TYPES["Unknown"]:-0} + 1))
  fi
done < /tmp/failed_jobs.txt

# Print results
for type in "${!FAILURE_TYPES[@]}"; do
  count=${FAILURE_TYPES[$type]}
  percentage=$((count * 100 / FAILED_COUNT))
  printf "%-20s: %3d (%2d%%)\n" "$type" "$count" "$percentage"
done

echo ""
echo "Sample Failed Jobs:"
head -5 /tmp/failed_jobs.txt
```

### 4. Performance Metrics from Logs

**Extract timing information:**
```bash
#!/bin/bash
# extract-timings.sh

echo "=== Performance Metrics from Logs ==="
echo ""

# API response times (if logged)
echo "[1/3] API Response Times:"
docker logs voilia-api --since 1h 2>&1 | \
  grep -oP 'response_time=[0-9.]+' | \
  sed 's/response_time=//' | \
  awk '{sum+=$1; count++} END {
    if (count > 0) {
      printf "Average: %.2fms\n", sum/count
      printf "Total requests: %d\n", count
    } else {
      print "No timing data found"
    }
  }'

echo ""

# Video encoding times
echo "[2/3] Video Encoding Times:"
docker logs voilia-worker --since 1h 2>&1 | \
  grep -oP 'encoding_time=[0-9.]+' | \
  sed 's/encoding_time=//' | \
  awk '{sum+=$1; count++} END {
    if (count > 0) {
      printf "Average: %.2fs\n", sum/count
      printf "Total encodes: %d\n", count
    } else {
      print "No encoding data found"
    }
  }'

echo ""

# Job queue wait times
echo "[3/3] Queue Wait Times:"
docker logs voilia-worker --since 1h 2>&1 | \
  grep -oP 'queue_wait=[0-9.]+' | \
  sed 's/queue_wait=//' | \
  awk '{sum+=$1; count++} END {
    if (count > 0) {
      printf "Average: %.2fs\n", sum/count
      printf "Total jobs: %d\n", count
    } else {
      print "No queue data found"
    }
  }'
```

### 5. Detect Anomalies

**Identify unusual patterns:**
```bash
#!/bin/bash
# detect-anomalies.sh

echo "=== Log Anomaly Detection ==="
echo ""

# 1. Sudden increase in errors
echo "[1/4] Checking for error spikes..."
RECENT_ERRORS=$(docker logs voilia-api --since 10m 2>&1 | grep -ic error)
BASELINE_ERRORS=$(docker logs voilia-api --since 2h --until 1h 2>&1 | wc -l | awk '{print int($1/12)}') # Per 10min average

if [ $RECENT_ERRORS -gt $((BASELINE_ERRORS * 3)) ]; then
  echo "⚠️  ERROR SPIKE DETECTED"
  echo "   Recent (10min): $RECENT_ERRORS errors"
  echo "   Baseline: ~$BASELINE_ERRORS errors per 10min"
else
  echo "✓ Error rate normal"
fi

echo ""

# 2. Repeated failures for same job
echo "[2/4] Checking for retry loops..."
docker logs voilia-worker --since 1h 2>&1 | \
  grep -oP 'job-[a-f0-9-]+' | \
  sort | uniq -c | sort -rn | head -5 | \
  while read count job_id; do
    if [ $count -gt 5 ]; then
      echo "⚠️  Job $job_id retried $count times"
    fi
  done

echo ""

# 3. Database connection issues
echo "[3/4] Checking database connection..."
DB_ERRORS=$(docker logs voilia-api --since 30m 2>&1 | grep -ic "database.*error\|connection.*failed")
if [ $DB_ERRORS -gt 10 ]; then
  echo "⚠️  Frequent database errors: $DB_ERRORS in last 30min"
else
  echo "✓ Database connections stable"
fi

echo ""

# 4. Memory warnings
echo "[4/4] Checking memory warnings..."
MEM_WARNINGS=$(docker logs voilia-api --since 1h 2>&1 | grep -ic "memory\|oom")
if [ $MEM_WARNINGS -gt 0 ]; then
  echo "⚠️  Memory warnings detected: $MEM_WARNINGS"
else
  echo "✓ No memory issues"
fi
```

### 6. Parse Structured Logs

**For JSON-formatted logs:**
```bash
# Extract specific fields from JSON logs
docker logs voilia-api --since 1h 2>&1 | \
  grep '^{' | \
  jq -r '.timestamp + " | " + .level + " | " + .message'

# Count by log level
docker logs voilia-api --since 1h 2>&1 | \
  grep '^{' | \
  jq -r '.level' | \
  sort | uniq -c

# Extract errors with context
docker logs voilia-api --since 1h 2>&1 | \
  grep '^{' | \
  jq 'select(.level == "ERROR") | {time: .timestamp, msg: .message, job: .job_id}'

# Aggregate metrics
docker logs voilia-api --since 1h 2>&1 | \
  grep '^{' | \
  jq -r 'select(.response_time != null) | .response_time' | \
  awk '{sum+=$1; count++; if($1>max) max=$1} END {
    printf "Min: %.0fms\n", 0
    printf "Avg: %.0fms\n", sum/count
    printf "Max: %.0fms\n", max
  }'
```

### 7. Incident Timeline

**Create timeline of events:**
```bash
#!/bin/bash
# create-incident-timeline.sh

INCIDENT_START=$1  # e.g., "2025-11-10 14:30"
INCIDENT_END=$2    # e.g., "2025-11-10 15:00"

echo "=== Incident Timeline ==="
echo "From: $INCIDENT_START"
echo "To: $INCIDENT_END"
echo ""

# Get logs from all services during incident
docker logs voilia-api --since "$INCIDENT_START" --until "$INCIDENT_END" --timestamps 2>&1 > /tmp/api_logs.txt
docker logs voilia-worker --since "$INCIDENT_START" --until "$INCIDENT_END" --timestamps 2>&1 > /tmp/worker_logs.txt

# Merge and sort by timestamp
cat /tmp/api_logs.txt /tmp/worker_logs.txt | \
  sort | \
  grep -i "error\|warning\|critical" | \
  awk '{
    # Extract timestamp and message
    timestamp = $1 " " $2
    $1=""; $2=""
    message = $0
    print timestamp " | " message
  }' | head -50

echo ""
echo "Timeline saved. Review for incident root cause."
```

### 8. Log Search Utilities

**Search across all containers:**
```bash
#!/bin/bash
# search-logs.sh

SEARCH_TERM=$1
TIME_RANGE=${2:-1h}

echo "=== Searching logs for: $SEARCH_TERM ==="
echo "Time range: Last $TIME_RANGE"
echo ""

# Search all VOILIA containers
for container in $(docker ps --filter name=voilia --format "{{.Names}}"); do
  echo "━━━ $container ━━━"
  MATCHES=$(docker logs "$container" --since "$TIME_RANGE" 2>&1 | grep -i "$SEARCH_TERM")

  if [ -n "$MATCHES" ]; then
    echo "$MATCHES" | tail -5
    COUNT=$(echo "$MATCHES" | wc -l)
    echo "($COUNT matches)"
  else
    echo "(no matches)"
  fi
  echo ""
done
```

**Context-aware log viewing:**
```bash
#!/bin/bash
# log-context.sh

# Find error and show 5 lines before and after
docker logs voilia-api 2>&1 | grep -B 5 -A 5 "ERROR"

# Show full stack trace for exceptions
docker logs voilia-worker 2>&1 | awk '
  /Traceback/ {printing=1}
  printing {print}
  /^[^ ]/ && printing {printing=0}
'
```

### 9. Real-Time Log Monitoring

**Live monitoring dashboard:**
```bash
#!/bin/bash
# live-monitor.sh

echo "=== Live Log Monitor ==="
echo "Press Ctrl+C to exit"
echo ""

# Monitor multiple containers in parallel
docker logs voilia-api -f --tail 0 2>&1 | sed 's/^/[API] /' &
API_PID=$!

docker logs voilia-worker -f --tail 0 2>&1 | sed 's/^/[WORKER] /' &
WORKER_PID=$!

# Highlight errors in red
while read line; do
  if echo "$line" | grep -qi error; then
    echo -e "\033[0;31m$line\033[0m"  # Red
  elif echo "$line" | grep -qi warning; then
    echo -e "\033[0;33m$line\033[0m"  # Yellow
  else
    echo "$line"
  fi
done

# Cleanup on exit
trap "kill $API_PID $WORKER_PID 2>/dev/null" EXIT
```

**Alert on critical errors:**
```bash
#!/bin/bash
# alert-on-errors.sh

echo "=== Monitoring for critical errors ==="

docker logs voilia-api -f --tail 0 2>&1 | \
  while read line; do
    if echo "$line" | grep -qi "critical\|fatal"; then
      echo "🚨 CRITICAL ERROR DETECTED 🚨"
      echo "$line"

      # Send notification (example)
      # curl -X POST https://hooks.slack.com/... -d "{\"text\": \"$line\"}"
    fi
  done
```

### 10. Log Rotation & Cleanup

**Check log file sizes:**
```bash
#!/bin/bash
# check-log-sizes.sh

echo "=== Docker Log Sizes ==="
echo ""

# Get log file sizes for each container
for container in $(docker ps --format "{{.Names}}"); do
  LOG_FILE=$(docker inspect "$container" --format='{{.LogPath}}')
  if [ -f "$LOG_FILE" ]; then
    SIZE=$(du -h "$LOG_FILE" | cut -f1)
    printf "%-30s: %s\n" "$container" "$SIZE"
  fi
done

echo ""

# Total log size
TOTAL=$(docker system df -v | grep "Local Volumes" -A 1 | tail -1 | awk '{print $3}')
echo "Total Docker logs: $TOTAL"

# Warn if logs are large
for container in $(docker ps --format "{{.Names}}"); do
  LOG_FILE=$(docker inspect "$container" --format='{{.LogPath}}')
  SIZE_BYTES=$(stat -c%s "$LOG_FILE" 2>/dev/null || echo "0")
  SIZE_MB=$((SIZE_BYTES / 1024 / 1024))

  if [ $SIZE_MB -gt 100 ]; then
    echo "⚠️  Large log file: $container (${SIZE_MB}MB)"
  fi
done
```

**Cleanup old logs:**
```bash
#!/bin/bash
# cleanup-logs.sh

echo "=== Log Cleanup ==="
echo ""

# Truncate large log files
for container in $(docker ps --format "{{.Names}}"); do
  LOG_FILE=$(docker inspect "$container" --format='{{.LogPath}}')
  SIZE_BYTES=$(stat -c%s "$LOG_FILE" 2>/dev/null || echo "0")
  SIZE_MB=$((SIZE_BYTES / 1024 / 1024))

  if [ $SIZE_MB -gt 500 ]; then
    echo "Truncating $container logs (${SIZE_MB}MB)..."
    truncate -s 100M "$LOG_FILE"
    echo "✓ Truncated to 100MB"
  fi
done

# Remove old archived logs
find /var/log/voilia -name "*.log.gz" -mtime +30 -delete
echo "✓ Removed archived logs older than 30 days"
```

### 11. Comprehensive Log Report

**Generate daily log summary:**
```bash
#!/bin/bash
# daily-log-report.sh

OUTPUT="log-report-$(date +%Y%m%d).md"

cat > "$OUTPUT" <<EOF
# VOILIA Log Report
Generated: $(date)

## Summary

### Error Statistics
- Total errors (24h): $(docker logs voilia-api --since 24h 2>&1 | grep -ic error)
- Total warnings (24h): $(docker logs voilia-api --since 24h 2>&1 | grep -ic warning)

### Job Statistics
- Completed jobs: $(docker logs voilia-worker --since 24h 2>&1 | grep -ic "completed")
- Failed jobs: $(docker logs voilia-worker --since 24h 2>&1 | grep -ic "failed")

### Top Errors
\`\`\`
$(docker logs voilia-api --since 24h 2>&1 | grep -i error | head -10)
\`\`\`

### Performance
- Average API response time: $(docker logs voilia-api --since 24h 2>&1 | grep -oP 'response_time=[0-9.]+' | sed 's/response_time=//' | awk '{sum+=$1; count++} END {printf "%.2fms", sum/count}')

## Recommendations
EOF

# Add recommendations based on analysis
ERROR_COUNT=$(docker logs voilia-api --since 24h 2>&1 | grep -ic error)
if [ $ERROR_COUNT -gt 100 ]; then
  echo "- ⚠️ High error rate detected - investigate root causes" >> "$OUTPUT"
fi

echo "✓ Report saved to $OUTPUT"
```

### 12. Quick Reference

**Common log queries:**
```bash
# Last 100 errors
docker logs voilia-api 2>&1 | grep -i error | tail -100

# Errors in last hour
docker logs voilia-api --since 1h 2>&1 | grep -i error

# Follow logs live
docker logs voilia-api -f

# Search for specific job
docker logs voilia-worker 2>&1 | grep "job-abc123"

# Count errors by hour
for h in {23..0}; do
  echo -n "$(date -d "$h hours ago" +%H:00): "
  docker logs voilia-api --since "${h}h" --until "$((h-1))h" 2>&1 | grep -ic error
done

# Export logs to file
docker logs voilia-api --since 24h 2>&1 > api-logs-$(date +%Y%m%d).txt
```

## Output Format

When analyzing logs, provide:
1. **Error summary**: Total count and top error types
2. **Timeline**: When issues started and frequency
3. **Root cause**: Likely cause based on log patterns
4. **Affected jobs**: Specific job IDs impacted
5. **Recommendations**: Immediate actions and preventive measures

Keep analysis focused on actionable insights for debugging and preventing future issues.
