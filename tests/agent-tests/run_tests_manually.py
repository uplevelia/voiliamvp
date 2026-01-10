"""
Manual test execution to demonstrate test-runner agent
"""
import time
import traceback

class TestResult:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.skipped = []
        self.start_time = time.time()

    def add_pass(self, test_name):
        self.passed.append(test_name)

    def add_fail(self, test_name, error_msg, line_no):
        self.failed.append((test_name, error_msg, line_no))

    def add_skip(self, test_name, reason):
        self.skipped.append((test_name, reason))

    def duration(self):
        return round(time.time() - self.start_time, 2)

result = TestResult()

# Test 1
def test_video_url_validation():
    valid_url = "https://example.com/video.mp4"
    assert valid_url.startswith("https://")
    assert valid_url.endswith(".mp4")

try:
    test_video_url_validation()
    result.add_pass("test_video_url_validation")
except AssertionError as e:
    result.add_fail("test_video_url_validation", str(e), 11)

# Test 2
def test_preset_selection():
    valid_presets = ["web-optimized", "high-quality", "fast-preview"]
    selected_preset = "web-optimized"
    assert selected_preset in valid_presets

try:
    test_preset_selection()
    result.add_pass("test_preset_selection")
except AssertionError as e:
    result.add_fail("test_preset_selection", str(e), 18)

# Test 3
def test_job_id_generation():
    import uuid
    job_id = str(uuid.uuid4())
    assert len(job_id) == 36
    assert job_id.count("-") == 4

try:
    test_job_id_generation()
    result.add_pass("test_job_id_generation")
except AssertionError as e:
    result.add_fail("test_job_id_generation", str(e), 26)

# Test 4
def test_progress_calculation():
    current_frame = 500
    total_frames = 1000
    progress = int((current_frame / total_frames) * 100)
    assert progress == 50
    assert 0 <= progress <= 100

try:
    test_progress_calculation()
    result.add_pass("test_progress_calculation")
except AssertionError as e:
    result.add_fail("test_progress_calculation", str(e), 35)

# Test 5
def test_file_extension_check():
    valid_extensions = [".mp4", ".mov", ".avi", ".mkv"]
    test_file = "video.mp4"
    ext = "." + test_file.split(".")[-1]
    assert ext in valid_extensions

try:
    test_file_extension_check()
    result.add_pass("test_file_extension_check")
except AssertionError as e:
    result.add_fail("test_file_extension_check", str(e), 44)

# Test 6 - Intentional failure
def test_encoding_timeout():
    max_timeout = 600
    actual_time = 700
    assert actual_time <= max_timeout, f"Encoding took {actual_time}s, max is {max_timeout}s"

try:
    test_encoding_timeout()
    result.add_pass("test_encoding_timeout")
except AssertionError as e:
    result.add_fail("test_encoding_timeout", str(e), 56)

# Test 7 - Intentional failure
def test_temp_file_cleanup():
    temp_files_remaining = 5
    assert temp_files_remaining == 0, f"Found {temp_files_remaining} temp files not cleaned up"

try:
    test_temp_file_cleanup()
    result.add_pass("test_temp_file_cleanup")
except AssertionError as e:
    result.add_fail("test_temp_file_cleanup", str(e), 63)

# Test 8 - Skipped
result.add_skip("test_batch_rendering", "Feature not implemented yet")

# Print results
print("\n" + "="*60)
print("✅ TEST RESULTS")
print("="*60)
print(f"Passed:  {len(result.passed)}")
print(f"Failed:  {len(result.failed)}")
print(f"Skipped: {len(result.skipped)}")
print(f"Duration: {result.duration()}s")
print()

if result.failed:
    print("="*60)
    print("❌ FAILURES")
    print("="*60)
    for i, (test_name, error, line_no) in enumerate(result.failed, 1):
        print(f"\n{i}. {test_name}")
        print(f"   File: test_sample.py:{line_no}")
        print(f"   Error: {error}")

        # Suggestions
        if "timeout" in test_name:
            print(f"   Suggestion: Increase timeout or optimize encoding speed")
        elif "cleanup" in test_name:
            print(f"   Suggestion: Add try/finally block to ensure cleanup")
    print()

if result.skipped:
    print("="*60)
    print("⏭️  SKIPPED")
    print("="*60)
    for test_name, reason in result.skipped:
        print(f"- {test_name}: {reason}")
    print()

# Summary
total = len(result.passed) + len(result.failed) + len(result.skipped)
pass_rate = round((len(result.passed) / total) * 100) if total > 0 else 0
print("="*60)
print(f"📊 SUMMARY: {len(result.passed)}/{total} passed ({pass_rate}%)")
print("="*60)
