# Test Runner Agent

## Purpose
Automate test execution, report results clearly, maintain test coverage, and help write effective tests using pytest best practices.

## When to Use
- ✅ Running test suite before commits
- ✅ Analyzing test failures and coverage gaps
- ✅ Setting up new test infrastructure
- ✅ Debugging flaky or slow tests
- ✅ Integrating tests with CI/CD
- ❌ NOT for writing business logic tests (that's code-reviewer)
- ❌ NOT for performance benchmarking (that's performance-monitor)

---

## Core Tasks

### 1. Run Tests

**Python (Backend/API):**
```bash
# Full test suite with coverage
cd api && pytest tests/ -v --cov=. --cov-report=term-missing

# Fast: Skip slow integration tests
pytest tests/ -v -m "not slow"

# Run only unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_encoder.py -v

# Run tests matching pattern
pytest -k "encoding" -v

# Re-run only failed tests from last run
pytest --lf -v

# Run tests in parallel (4 workers)
pytest tests/ -n 4
```

**JavaScript/TypeScript (Frontend):**
```bash
cd frontend && npm test -- --coverage

# Watch mode for development
npm test -- --watch

# Update snapshots
npm test -- --updateSnapshot
```

**Integration Tests:**
```bash
# Start dependencies first
docker compose up -d postgres redis s3

# Run integration tests
pytest tests/integration/ -v --cov=api --cov-report=html

# Cleanup after
docker compose down
```

---

### 2. Advanced Pytest Features

#### **Fixtures for Reusable Setup**

Create `tests/conftest.py` for shared fixtures:

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def api_client():
    """FastAPI test client"""
    from api.main import app
    return TestClient(app)

@pytest.fixture
def temp_video_dir():
    """Temporary directory for test videos"""
    temp_dir = Path(tempfile.mkdtemp(prefix="voilia-test-"))
    yield temp_dir
    # Cleanup after test
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

@pytest.fixture
def sample_video(temp_video_dir):
    """Create a small test video"""
    video_path = temp_video_dir / "test.mp4"
    # Generate 1-second test video
    import subprocess
    subprocess.run([
        "ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=1:size=320x240:rate=30",
        "-pix_fmt", "yuv420p", str(video_path)
    ], check=True, capture_output=True)
    return video_path

@pytest.fixture
def mock_s3():
    """Mock S3 client"""
    from unittest.mock import MagicMock
    mock_client = MagicMock()
    mock_client.upload_file.return_value = None
    mock_client.generate_presigned_url.return_value = "https://s3.example.com/video.mp4"
    return mock_client
```

**Using fixtures in tests:**

```python
# tests/unit/test_api.py
def test_upload_video(api_client, sample_video):
    """Test video upload endpoint"""
    with open(sample_video, "rb") as f:
        response = api_client.post(
            "/api/videos/upload",
            files={"file": ("test.mp4", f, "video/mp4")}
        )
    assert response.status_code == 201
    assert "job_id" in response.json()

def test_render_with_preset(api_client, mock_s3, monkeypatch):
    """Test rendering with mocked S3"""
    monkeypatch.setattr("api.services.storage.s3_client", mock_s3)

    response = api_client.post("/api/render", json={
        "video_id": "test-123",
        "preset": "web-optimized"
    })
    assert response.status_code == 202
    mock_s3.upload_file.assert_called_once()
```

---

#### **Parametrized Tests for Multiple Cases**

Test the same logic with different inputs:

```python
import pytest

@pytest.mark.parametrize("preset,expected_crf", [
    ("web-optimized", 23),
    ("high-quality", 18),
    ("fast-preview", 28),
])
def test_preset_crf_values(preset, expected_crf):
    """Verify CRF values for each preset"""
    from renderer.presets import load_preset
    config = load_preset(preset)
    assert config["crf"] == expected_crf

@pytest.mark.parametrize("codec,extension", [
    ("libx264", ".mp4"),
    ("libx265", ".mp4"),
    ("libvpx-vp9", ".webm"),
])
def test_codec_output_formats(codec, extension):
    """Test output file extensions for codecs"""
    from renderer.ffmpeg_wrapper import get_output_extension
    assert get_output_extension(codec) == extension

@pytest.mark.parametrize("duration,should_timeout", [
    (5, False),      # 5 seconds - OK
    (300, False),    # 5 minutes - OK
    (700, True),     # 11+ minutes - Should timeout
])
def test_render_timeout_handling(duration, should_timeout):
    """Test timeout logic for long renders"""
    from renderer.validator import should_apply_timeout
    assert should_apply_timeout(duration) == should_timeout
```

---

#### **Markers for Test Organization**

Organize tests by speed, type, or feature:

```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "ffmpeg: marks tests that require FFmpeg",
    "s3: marks tests that interact with S3",
]

# In your test files:
import pytest

@pytest.mark.unit
def test_parse_duration():
    """Fast unit test"""
    from renderer.utils import parse_duration
    assert parse_duration("00:01:30") == 90

@pytest.mark.slow
@pytest.mark.ffmpeg
def test_actual_video_encoding(sample_video):
    """Slow test that runs real FFmpeg"""
    from renderer.encoder import encode_video
    output = encode_video(sample_video, preset="fast-preview")
    assert output.exists()
    assert output.stat().st_size > 0

@pytest.mark.integration
@pytest.mark.s3
def test_full_render_pipeline():
    """Full integration test with S3 upload"""
    # ... full pipeline test
```

**Running specific markers:**
```bash
# Only unit tests (fast)
pytest -m unit -v

# Skip slow tests
pytest -m "not slow" -v

# Only FFmpeg tests
pytest -m ffmpeg -v

# Integration tests only
pytest -m integration -v
```

---

### 3. Mocking Strategies

#### **Mock External Services**

```python
from unittest.mock import MagicMock, patch, call
import pytest

# Mocking S3
def test_upload_to_s3_success(monkeypatch):
    """Test S3 upload with mocked client"""
    mock_client = MagicMock()
    mock_client.upload_file.return_value = None

    monkeypatch.setattr("api.services.storage.s3_client", mock_client)

    from api.services.storage import upload_render
    result = upload_render("/tmp/video.mp4", "job-123")

    assert result == "https://s3.example.com/renders/job-123.mp4"
    mock_client.upload_file.assert_called_once_with(
        "/tmp/video.mp4",
        "voilia-renders",
        "job-123.mp4"
    )

# Mocking Celery tasks
@patch("api.tasks.render_video.delay")
def test_render_endpoint_queues_job(mock_task, api_client):
    """Test that render endpoint queues Celery task"""
    mock_task.return_value = MagicMock(id="task-abc-123")

    response = api_client.post("/api/render", json={
        "video_id": "vid-123",
        "preset": "web-optimized"
    })

    assert response.status_code == 202
    assert response.json()["task_id"] == "task-abc-123"
    mock_task.assert_called_once_with("vid-123", "web-optimized")

# Mocking subprocess (FFmpeg)
@patch("subprocess.run")
def test_ffmpeg_command_execution(mock_subprocess):
    """Test FFmpeg command construction without running it"""
    mock_subprocess.return_value = MagicMock(returncode=0, stdout=b"", stderr=b"")

    from renderer.ffmpeg_wrapper import run_ffmpeg
    run_ffmpeg(["-i", "input.mp4", "-c:v", "libx264", "output.mp4"])

    # Verify command was built correctly
    mock_subprocess.assert_called_once()
    args = mock_subprocess.call_args[0][0]
    assert args[0] == "ffmpeg"
    assert "-c:v" in args
    assert "libx264" in args
```

#### **Mock Time-Dependent Code**

```python
from unittest.mock import patch
from datetime import datetime, timedelta
import pytest

@patch("api.utils.datetime")
def test_token_expiration(mock_datetime):
    """Test JWT token expiration logic"""
    # Mock current time
    fake_now = datetime(2025, 1, 1, 12, 0, 0)
    mock_datetime.utcnow.return_value = fake_now

    from api.auth import create_token, is_token_expired
    token = create_token(user_id="user-123", expires_in=3600)

    # Token should be valid now
    assert not is_token_expired(token)

    # Fast-forward time by 2 hours
    mock_datetime.utcnow.return_value = fake_now + timedelta(hours=2)

    # Token should now be expired
    assert is_token_expired(token)
```

---

### 4. Coverage Configuration & Interpretation

#### **pytest.ini / pyproject.toml Configuration**

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Coverage options
addopts =
    --strict-markers
    --cov=api
    --cov=renderer
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=70

# Ignore warnings from dependencies
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

**Or use pyproject.toml:**
```toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
addopts = [
    "--strict-markers",
    "--cov=api",
    "--cov=renderer",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=70",
]
```

#### **Reading Coverage Reports**

```
---------- coverage: platform linux, python 3.11.7 -----------
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
api/__init__.py                 5      0   100%
api/main.py                    45      3    93%   78-80
api/routes/videos.py           89     12    87%   145-152, 201-204
api/services/encoder.py       123     45    63%   67-89, 112-145
renderer/ffmpeg_wrapper.py    156      8    95%   234-241
---------------------------------------------------------
TOTAL                         418     68    84%

6 files skipped due to complete coverage.
```

**Interpreting:**
- **Stmts**: Total executable lines
- **Miss**: Lines not covered by tests
- **Cover**: Percentage covered
- **Missing**: Specific line numbers not tested

**Focus Areas:**
- `api/services/encoder.py` at **63%** - needs more tests!
- Lines 67-89, 112-145 are untested - likely error handling or edge cases

---

### 5. Test Organization Best Practices

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Fast, isolated tests
│   ├── test_encoder.py
│   ├── test_ffmpeg_wrapper.py
│   ├── test_presets.py
│   └── test_validators.py
├── integration/             # Tests with external dependencies
│   ├── test_api_endpoints.py
│   ├── test_celery_tasks.py
│   ├── test_s3_upload.py
│   └── test_full_pipeline.py
├── fixtures/                # Test data
│   ├── videos/
│   │   └── sample.mp4
│   ├── presets/
│   │   └── test-preset.json
│   └── expected_outputs/
└── helpers.py               # Test utilities
```

**AAA Pattern (Arrange-Act-Assert):**

```python
def test_video_upload_creates_job():
    # ARRANGE - Set up test data
    test_file = "tests/fixtures/videos/sample.mp4"
    expected_job_status = "pending"

    # ACT - Execute the code being tested
    response = api_client.post("/api/videos/upload", files={"file": open(test_file, "rb")})
    job_id = response.json()["job_id"]
    job = get_job(job_id)

    # ASSERT - Verify the results
    assert response.status_code == 201
    assert job.status == expected_job_status
    assert job.input_file == test_file
```

---

### 6. Debugging Failed Tests

#### **Verbose Output & Print Debugging**

```bash
# Show print statements even for passing tests
pytest -v -s

# Show local variables on failures
pytest -l

# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start of test
pytest --trace
```

#### **Using pytest's Built-in Debugger**

```python
def test_complex_encoding_logic():
    result = complex_function()

    # Drop into debugger here
    import pytest; pytest.set_trace()

    assert result == expected
```

#### **Capturing Logs**

```python
import logging

def test_with_logs(caplog):
    """Test that captures log output"""
    caplog.set_level(logging.INFO)

    # Code that logs something
    from renderer.encoder import encode_video
    encode_video("input.mp4", "web-optimized")

    # Assert log messages
    assert "Starting encode" in caplog.text
    assert "Encode complete" in caplog.text
```

---

### 7. CI/CD Integration

#### **GitHub Actions**

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install FFmpeg
        run: sudo apt-get update && sudo apt-get install -y ffmpeg

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-xdist

      - name: Run unit tests
        run: pytest tests/unit -v -m "not slow" --cov=api --cov=renderer

      - name: Run integration tests
        run: pytest tests/integration -v
        env:
          DATABASE_URL: postgresql://postgres:test@localhost/test
          REDIS_URL: redis://localhost:6379/0

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
```

---

### 8. Common Issues & Fixes

#### **Issue 1: Flaky Tests (Randomly Fail)**

**Cause:** Time-dependent code, race conditions, external dependencies

**Fix:**
```python
# Bad - Time-dependent
import time
def test_timeout():
    start = time.time()
    slow_function()
    assert time.time() - start < 5  # Flaky!

# Good - Mock time or test logic directly
@patch("time.sleep")
def test_timeout_logic(mock_sleep):
    result = function_with_timeout(timeout=5)
    assert result is not None
```

#### **Issue 2: Tests Too Slow**

**Cause:** Not using mocks, running full integration tests

**Fix:**
```bash
# Run tests in parallel
pytest -n 4

# Skip slow tests during development
pytest -m "not slow"

# Mock external services
# Use pytest-mock, don't hit real S3/databases
```

#### **Issue 3: Import Errors in Tests**

**Cause:** PYTHONPATH not set, circular imports

**Fix:**
```bash
# Ensure tests can import from api/
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/

# Or use pytest's automatic path detection
pytest  # It will add current dir to path
```

---

### 9. Report Results

Provide a clear summary:

**Terminal Output:**
```
✅ TEST RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Passed:  45
Failed:   2
Skipped:  1
Coverage: 78%
Duration: 3.2s

❌ FAILURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. test_video_encoding_with_invalid_codec
   File: tests/unit/test_encoder.py:42
   Error: AssertionError: Expected ValueError, got None

   Code:
   > assert encoder.encode(invalid_codec="fake") raises ValueError

   Suggestion: Check that invalid codec validation is implemented

2. test_temp_file_cleanup
   File: tests/unit/test_cleanup.py:28
   Error: FileExistsError: /tmp/voilia-renders/test-123 still exists

   Code:
   > assert not temp_dir.exists()

   Suggestion: Ensure cleanup handler is called in finally block

📊 COVERAGE GAPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical (< 70%):
- api/services/encoder.py: 63% (lines 67-89, 112-145 untested)
- api/routes/webhooks.py: 0% (no tests!)

Needs Improvement (70-85%):
- renderer/effects.py: 74%
- api/routes/videos.py: 82%
```

---

## Quick Reference

```bash
# Basic test run
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=api --cov=renderer --cov-report=term-missing

# Fast: unit tests only, skip slow
pytest tests/unit -m "not slow" -v

# Re-run only failures
pytest --lf -v

# Parallel execution (4 workers)
pytest -n 4

# Show print statements
pytest -v -s

# Debug on failure
pytest --pdb

# Generate HTML coverage report
pytest --cov=api --cov-report=html
open htmlcov/index.html

# Run specific test
pytest tests/unit/test_encoder.py::test_preset_loading -v

# Run tests matching pattern
pytest -k "encoding" -v
```

---

## Output Format Example

```
============================= test session starts ==============================
platform linux -- Python 3.11.7, pytest-7.4.3, pluggy-1.3.0
rootdir: /root/uplevelia/projects/voilia
configfile: pytest.ini
plugins: cov-4.1.0, xdist-3.5.0, mock-3.12.0
collected 48 items

tests/unit/test_encoder.py::test_load_preset PASSED                      [  2%]
tests/unit/test_encoder.py::test_invalid_preset PASSED                   [  4%]
tests/unit/test_ffmpeg_wrapper.py::test_build_command PASSED             [  6%]
...
tests/integration/test_full_pipeline.py::test_render_upload PASSED       [100%]

---------- coverage: platform linux, python 3.11.7 -----------
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
api/main.py                    45      3    93%   78-80
renderer/encoder.py           123     12    90%   145-152, 201-204
TOTAL                         418     28    93%

========================= 45 passed, 2 failed, 1 skipped in 3.21s =========================
```
