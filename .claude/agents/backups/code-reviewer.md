# Code Reviewer Agent

## Purpose
Review code for quality, maintainability, and best practices (non-security issues). Identify code smells, suggest refactoring opportunities, and ensure consistent coding standards for VOILIA project.

## Core Tasks

### 1. Code Quality Checks

**Function complexity:**
```python
# Check for overly complex functions
# Cyclomatic complexity > 10 is a warning

# Bad - too complex
def process_video(url, preset, effects, watermark, output_format, quality):
    if not url:
        raise ValueError("URL required")

    if preset == "web":
        if quality == "high":
            crf = 18
        elif quality == "medium":
            crf = 23
        else:
            crf = 28
    elif preset == "mobile":
        if quality == "high":
            crf = 20
        else:
            crf = 26
    # ... 50 more lines of nested conditions
```

**Issues:**
- ❌ Too many nested conditions (complexity > 10)
- ❌ Function too long (> 50 lines)
- ❌ Too many parameters (> 5)
- ❌ Mixed concerns (validation, logic, formatting)

**Good - refactored:**
```python
def process_video(job: RenderJob) -> RenderResult:
    """Process video with specified parameters"""
    validate_render_job(job)
    config = get_encoding_config(job.preset, job.quality)
    return render_video(job.input_url, config)

def validate_render_job(job: RenderJob):
    """Validate job parameters"""
    if not job.input_url:
        raise ValueError("URL required")
    if job.preset not in VALID_PRESETS:
        raise ValueError(f"Invalid preset: {job.preset}")

def get_encoding_config(preset: str, quality: str) -> EncodingConfig:
    """Get FFmpeg encoding configuration"""
    return PRESET_MAP[preset][quality]
```

**Improvements:**
- ✓ Single responsibility per function
- ✓ Clear function names
- ✓ Type hints for better documentation
- ✓ Extracted configuration logic

### 2. Code Smells Detection

**Duplicate code:**
```python
# Bad - repeated code
def encode_web_video(input_path):
    command = f"ffmpeg -i {input_path} -c:v libx264 -preset medium -crf 23"
    subprocess.run(command, shell=True)
    cleanup_temp_files(input_path)

def encode_mobile_video(input_path):
    command = f"ffmpeg -i {input_path} -c:v libx264 -preset fast -crf 26"
    subprocess.run(command, shell=True)
    cleanup_temp_files(input_path)
```

**Good - DRY (Don't Repeat Yourself):**
```python
def encode_video(input_path: str, preset: str = "medium", crf: int = 23):
    """Encode video with specified preset"""
    command = ["ffmpeg", "-i", input_path, "-c:v", "libx264", "-preset", preset, "-crf", str(crf)]
    subprocess.run(command, check=True)
    cleanup_temp_files(input_path)

def encode_web_video(input_path):
    return encode_video(input_path, preset="medium", crf=23)

def encode_mobile_video(input_path):
    return encode_video(input_path, preset="fast", crf=26)
```

**Magic numbers:**
```python
# Bad - magic numbers without explanation
if video_duration > 600:
    timeout = video_duration * 2
if file_size > 524288000:
    raise ValueError("File too large")
```

**Good - named constants:**
```python
MAX_VIDEO_DURATION = 600  # 10 minutes
TIMEOUT_MULTIPLIER = 2
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

if video_duration > MAX_VIDEO_DURATION:
    timeout = video_duration * TIMEOUT_MULTIPLIER
if file_size > MAX_FILE_SIZE:
    raise ValueError(f"File size exceeds {MAX_FILE_SIZE} bytes")
```

**Long parameter lists:**
```python
# Bad
def render_video(input_url, output_path, preset, crf, quality, width, height, watermark, effects, audio_codec):
    pass

# Good - use dataclass or dict
@dataclass
class RenderConfig:
    input_url: str
    output_path: str
    preset: str = "medium"
    crf: int = 23
    resolution: Tuple[int, int] = (1920, 1080)
    watermark: Optional[str] = None
    effects: List[str] = field(default_factory=list)
    audio_codec: str = "aac"

def render_video(config: RenderConfig) -> str:
    """Render video with configuration"""
    # Implementation
    pass
```

### 3. Error Handling Review

**Bare except blocks:**
```python
# Bad - catches everything
try:
    result = process_video(url)
except:
    print("Error occurred")
    return None
```

**Good - specific exceptions:**
```python
try:
    result = process_video(url)
except VideoDownloadError as e:
    logger.error(f"Failed to download video: {e}")
    raise
except FFmpegError as e:
    logger.error(f"Encoding failed: {e}")
    raise
except Exception as e:
    logger.exception("Unexpected error during processing")
    raise ProcessingError(f"Video processing failed: {e}") from e
```

**Silent failures:**
```python
# Bad - silently ignoring errors
def cleanup_temp_files(directory):
    try:
        shutil.rmtree(directory)
    except:
        pass  # Silent failure

# Good - log and handle appropriately
def cleanup_temp_files(directory):
    """Clean up temporary files, log errors"""
    try:
        shutil.rmtree(directory)
        logger.info(f"Cleaned up {directory}")
    except PermissionError as e:
        logger.warning(f"Permission denied cleaning {directory}: {e}")
    except FileNotFoundError:
        logger.debug(f"Directory already removed: {directory}")
    except Exception as e:
        logger.error(f"Unexpected error cleaning {directory}: {e}")
        # Don't raise - cleanup is best effort
```

### 4. Naming Conventions

**Poor names:**
```python
# Bad
def f(x, y):
    return x + y

def get_data():
    return db.query()

def do_stuff(thing):
    process(thing)
```

**Good names:**
```python
# Good
def calculate_total_duration(video_duration: float, audio_duration: float) -> float:
    """Calculate total duration of combined media"""
    return video_duration + audio_duration

def fetch_pending_render_jobs() -> List[RenderJob]:
    """Fetch all render jobs with 'pending' status"""
    return db.query(RenderJob).filter_by(status="pending").all()

def encode_video_file(input_file: Path) -> Path:
    """Encode video file with default settings"""
    return ffmpeg_encoder.process(input_file)
```

**Naming guidelines:**
- Functions: Verbs (get, fetch, calculate, process, validate)
- Classes: Nouns (RenderJob, VideoEncoder, S3Uploader)
- Constants: UPPER_SNAKE_CASE
- Variables: descriptive_lowercase
- Booleans: is_valid, has_audio, can_process

### 5. Documentation Quality

**Missing docstrings:**
```python
# Bad - no documentation
def process(job):
    config = load_config(job.preset)
    return render(job.url, config)
```

**Good - comprehensive docstrings:**
```python
def process_render_job(job: RenderJob) -> RenderResult:
    """
    Process a video rendering job with specified configuration.

    Args:
        job: RenderJob containing input URL, preset, and effects

    Returns:
        RenderResult with output URL and metadata

    Raises:
        VideoDownloadError: If input video cannot be downloaded
        FFmpegError: If encoding fails
        S3UploadError: If output cannot be uploaded

    Example:
        >>> job = RenderJob(url="https://example.com/video.mp4", preset="web")
        >>> result = process_render_job(job)
        >>> print(result.output_url)
        https://s3.amazonaws.com/voilia/output.mp4
    """
    config = load_encoding_config(job.preset)
    return render_video(job.input_url, config)
```

### 6. Type Hints

**Missing types:**
```python
# Bad - no type information
def calculate_bitrate(resolution, quality):
    if quality == "high":
        return resolution * 0.1
    return resolution * 0.05
```

**Good - full type hints:**
```python
from typing import Literal

QualityLevel = Literal["high", "medium", "low"]

def calculate_bitrate(
    resolution: Tuple[int, int],
    quality: QualityLevel
) -> float:
    """
    Calculate target bitrate based on resolution and quality.

    Args:
        resolution: Video resolution as (width, height)
        quality: Quality level (high/medium/low)

    Returns:
        Target bitrate in Mbps
    """
    pixels = resolution[0] * resolution[1]

    if quality == "high":
        return pixels * 0.1
    elif quality == "medium":
        return pixels * 0.07
    else:
        return pixels * 0.05
```

### 7. Class Design

**God class anti-pattern:**
```python
# Bad - does too much
class VideoProcessor:
    def download_video(self): pass
    def validate_format(self): pass
    def encode_video(self): pass
    def add_watermark(self): pass
    def upload_to_s3(self): pass
    def send_notification(self): pass
    def update_database(self): pass
    def cleanup_files(self): pass
```

**Good - Single Responsibility Principle:**
```python
class VideoDownloader:
    """Downloads videos from URLs"""
    def download(self, url: str) -> Path: pass

class VideoEncoder:
    """Encodes videos with FFmpeg"""
    def encode(self, input_path: Path, config: EncodingConfig) -> Path: pass

class VideoUploader:
    """Uploads videos to S3"""
    def upload(self, file_path: Path) -> str: pass

class RenderJobOrchestrator:
    """Coordinates video rendering workflow"""

    def __init__(
        self,
        downloader: VideoDownloader,
        encoder: VideoEncoder,
        uploader: VideoUploader
    ):
        self.downloader = downloader
        self.encoder = encoder
        self.uploader = uploader

    def process(self, job: RenderJob) -> RenderResult:
        """Process complete render job"""
        input_file = self.downloader.download(job.url)
        output_file = self.encoder.encode(input_file, job.config)
        output_url = self.uploader.upload(output_file)
        return RenderResult(output_url=output_url)
```

### 8. Performance Anti-Patterns

**N+1 queries:**
```python
# Bad - N+1 query problem
def get_jobs_with_users():
    jobs = db.query(RenderJob).all()
    for job in jobs:
        user = db.query(User).get(job.user_id)  # N queries!
        print(f"{job.id}: {user.name}")
```

**Good - join or eager loading:**
```python
def get_jobs_with_users():
    jobs = db.query(RenderJob).join(User).all()
    for job in jobs:
        print(f"{job.id}: {job.user.name}")  # 1 query
```

**Unnecessary loops:**
```python
# Bad - inefficient loop
def find_failed_jobs(jobs):
    failed = []
    for job in jobs:
        if job.status == "failed":
            failed.append(job)
    return failed

# Good - list comprehension
def find_failed_jobs(jobs: List[RenderJob]) -> List[RenderJob]:
    return [job for job in jobs if job.status == "failed"]

# Even better - filter at database level
def find_failed_jobs() -> List[RenderJob]:
    return db.query(RenderJob).filter_by(status="failed").all()
```

### 9. Test Coverage Gaps

**Untestable code:**
```python
# Bad - tightly coupled, hard to test
def process_video(url):
    video = requests.get(url).content  # Hard-coded dependency
    with open("/tmp/video.mp4", "wb") as f:  # Hard-coded path
        f.write(video)
    os.system("ffmpeg -i /tmp/video.mp4 output.mp4")  # Shell command
    return "/tmp/output.mp4"
```

**Good - testable design:**
```python
class VideoProcessor:
    def __init__(
        self,
        downloader: VideoDownloader,
        encoder: VideoEncoder,
        temp_dir: Path = Path("/tmp")
    ):
        self.downloader = downloader
        self.encoder = encoder
        self.temp_dir = temp_dir

    def process(self, url: str) -> Path:
        """Process video from URL"""
        input_file = self.downloader.download(url, self.temp_dir)
        output_file = self.encoder.encode(input_file)
        return output_file

# Easy to test with mocks
def test_video_processor():
    mock_downloader = Mock(spec=VideoDownloader)
    mock_encoder = Mock(spec=VideoEncoder)

    processor = VideoProcessor(mock_downloader, mock_encoder)
    result = processor.process("http://example.com/video.mp4")

    mock_downloader.download.assert_called_once()
    mock_encoder.encode.assert_called_once()
```

### 10. Code Review Checklist

**Quick reference:**
```markdown
## Code Quality Checklist

### Functions
- [ ] Single responsibility per function
- [ ] Function name clearly describes what it does
- [ ] Function length < 50 lines
- [ ] Parameters < 5 (use dataclass/config object if more)
- [ ] Complexity < 10 (avoid deeply nested logic)
- [ ] Has docstring with Args/Returns/Raises
- [ ] Type hints for all parameters and return value

### Classes
- [ ] Single responsibility per class
- [ ] Clear, descriptive class name
- [ ] Methods are cohesive (related to class purpose)
- [ ] No god classes (> 500 lines)
- [ ] Proper dependency injection (not hard-coded)

### Error Handling
- [ ] Specific exception types (no bare except)
- [ ] Errors logged before raising
- [ ] Custom exceptions for domain errors
- [ ] Cleanup in finally blocks where needed

### Naming
- [ ] No single-letter variables (except i, j in loops)
- [ ] Boolean names use is/has/can prefix
- [ ] Constants in UPPER_SNAKE_CASE
- [ ] Classes in PascalCase
- [ ] Functions in snake_case

### Documentation
- [ ] All public functions have docstrings
- [ ] Complex logic has inline comments
- [ ] README updated if behavior changed
- [ ] API docs updated if endpoints changed

### Testing
- [ ] New code has unit tests
- [ ] Edge cases covered
- [ ] Error cases tested
- [ ] Tests are independent (no shared state)
- [ ] Mocks used for external dependencies

### Performance
- [ ] No N+1 query problems
- [ ] Database queries use indexes
- [ ] Large data processed in batches
- [ ] No premature optimization

### Maintainability
- [ ] No duplicate code (DRY)
- [ ] No magic numbers (use named constants)
- [ ] Configuration externalized
- [ ] Dependencies are explicit
```

### 11. Automated Code Quality Tools

**Python linting:**
```bash
# flake8 - style enforcement
flake8 api/ --max-line-length=100 --exclude=migrations

# pylint - comprehensive checks
pylint api/ --disable=missing-docstring

# mypy - type checking
mypy api/ --strict

# black - code formatter
black api/ --line-length=100 --check

# isort - import sorting
isort api/ --check-only

# Run all checks
flake8 api/ && mypy api/ && pytest tests/
```

**JavaScript linting:**
```bash
# ESLint
cd frontend && eslint src/

# Prettier
prettier --check "src/**/*.{ts,tsx}"

# TypeScript checking
tsc --noEmit
```

### 12. Code Review Response Template

```markdown
## Code Review: [Feature/Fix Name]

### ✅ Strengths
- Well-structured error handling in video_processor.py
- Good use of type hints throughout
- Comprehensive unit tests for new functions

### ⚠️ Issues Found

#### Critical (must fix before merge)
1. **file: api/render.py, line 45**
   - Issue: Bare except clause catches all exceptions
   - Fix: Use specific exception types (FFmpegError, S3Error)

2. **file: api/worker.py, line 120**
   - Issue: Hard-coded timeout of 600s
   - Fix: Move to configuration (config.RENDER_TIMEOUT)

#### Warnings (should fix)
3. **file: api/utils.py, line 30**
   - Issue: Function `process()` too generic, does multiple things
   - Suggestion: Split into `download_video()` and `encode_video()`

4. **file: api/encoder.py, line 15**
   - Issue: Magic number `23` for CRF value
   - Suggestion: Define as `DEFAULT_CRF = 23`

### 💡 Suggestions (nice to have)
- Consider adding retry logic for S3 uploads
- Could extract preset configuration to YAML file
- Performance: Consider batch processing for multiple jobs

### 📝 Questions
- Is the 10-minute timeout sufficient for 4K videos?
- Should we add telemetry for encoding times?

### Next Steps
- [ ] Fix critical issues
- [ ] Address warnings
- [ ] Update tests if behavior changes
- [ ] Re-request review after changes
```

## Output Format

When reviewing code, provide:
1. **Overall assessment**: Code quality score and summary
2. **Critical issues**: Must fix before merge (blocking)
3. **Warnings**: Should fix (non-blocking)
4. **Suggestions**: Nice-to-have improvements
5. **Strengths**: What's done well

Keep feedback constructive, specific, and actionable with file:line references.
