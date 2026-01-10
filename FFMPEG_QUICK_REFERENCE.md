# VOILIA FFmpeg Quick Reference Card

## Production Command (Use This!)

```bash
ffmpeg -i input.mp4 \
  -c:v libx264 \
  -preset medium \
  -crf 23 \
  -threads 0 \
  -c:a copy \
  -movflags +faststart \
  output.mp4
```

**Expected**: 50 min per 1-hour video | Quality: PSNR ~40 dB | File size: 450 MB per hour

---

## Common Encoding Scenarios

### Web Video (Default)
```bash
ffmpeg -i input.mp4 -c:v libx264 -preset medium -crf 23 -threads 0 -c:a copy -movflags +faststart output.mp4
```
Speed: 1-2x realtime | Quality: Very Good | Use: Web, streaming

### Premium Quality
```bash
ffmpeg -i input.mp4 -c:v libx264 -preset slow -crf 18 -threads 0 -c:a aac -b:a 192k -movflags +faststart output.mp4
```
Speed: 0.5x realtime | Quality: Excellent | Use: Marketing, archival

### Fast Preview
```bash
ffmpeg -i input.mp4 -c:v libx264 -preset veryfast -crf 28 -threads 0 -c:a copy -vf "scale=854:480" output.mp4
```
Speed: 5x realtime | Quality: Fair | Use: Testing, development

### 4K Downscale to 1080p
```bash
ffmpeg -i input_4k.mp4 -c:v libx264 -preset fast -crf 23 -threads 0 -c:a copy -vf "scale=1920:1080" -movflags +faststart output.mp4
```
Speed: 2-3x realtime | Quality: Good | File: 40% reduction

---

## Key Flags Explained

| Flag | Example | Purpose |
|------|---------|---------|
| `-c:v libx264` | Video codec | Always use libx264 for web (CPU-friendly) |
| `-preset` | `medium` | Speed/quality balance (ultrafast, fast, medium, slow, veryslow) |
| `-crf` | `23` | Quality (0-51, lower=better, 18-28 typical) |
| `-threads 0` | Auto | Use all CPU cores automatically |
| `-c:a copy` | Copy audio | Don't re-encode if already AAC/MP3 |
| `-c:a aac -b:a 128k` | Re-encode | Only if needed (128k sufficient for dialogue) |
| `-movflags +faststart` | Web streaming | Enables instant playback |
| `-vf "scale=W:H"` | Resize | Apply scaling filter (do LAST in chain) |

---

## Preset Quick Comparison (1-hour 1080p video)

| Preset | Time | Quality | File Size | When |
|--------|------|---------|-----------|------|
| ultrafast | 6 min | Poor | 900 MB | Not recommended |
| veryfast | 12 min | Fair | 850 MB | Quick test |
| fast | 30 min | Good | 450 MB | Time-sensitive |
| **medium** | **50 min** | **Very Good** | **450 MB** | **Default** |
| slow | 100 min | Excellent | 350 MB | Premium |
| veryslow | 300 min | Best | 320 MB | Don't use |

---

## Common Mistakes to Avoid

1. **DON'T use ultrafast for web**: Poor quality/speed tradeoff
2. **DON'T use veryslow**: 300 minutes per hour = not practical
3. **DON'T scale twice**: One scaling operation at END of filter chain
4. **DON'T re-encode AAC audio**: Use `-c:a copy` instead
5. **DON'T forget `-threads 0`**: Leaves CPU cores unused
6. **DON'T use os.system()**: Use `subprocess` with list args
7. **DON'T hardcode credentials**: Use environment variables

---

## Quick Performance Boosts (In Order)

1. Add `-threads 0` → +30-50% speed
2. Use `-c:a copy` → +5-10 min saved per video
3. Remove double scaling → +30% filter speed
4. Add `-movflags +faststart` → Instant web playback

**Total potential gain**: 2-3x faster encoding!

---

## Troubleshooting

### Encoding Too Slow
- Check preset (should be `fast` or `medium`)
- Add `-threads 0` if missing
- Reduce resolution with `-vf "scale=1280:720"`
- Don't use `slow` or `veryslow` for production

### File Too Large
- Increase CRF to 26-28 (quality still acceptable)
- Reduce resolution
- Don't use `slow`/`veryslow` presets

### Poor Quality
- Decrease CRF to 18-20
- Use `slow` preset instead of `medium`
- Check source video quality with ffprobe

### Command Injection (SECURITY!)
- NEVER: `os.system(f"ffmpeg -i {user_input} ...")`
- ALWAYS: Use `subprocess.run([list, of, args])`

---

## Safe Python Template

```python
import subprocess
from pathlib import Path

def encode_video(input_file: str, output_file: str, preset: str = 'medium'):
    """Safe FFmpeg encoding"""
    
    # Validate inputs
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_file}")
    
    # Build command as LIST (prevents injection)
    cmd = [
        'ffmpeg',
        '-i', str(input_path),
        '-c:v', 'libx264',
        '-preset', preset,
        '-crf', '23',
        '-threads', '0',
        '-c:a', 'copy',
        '-movflags', '+faststart',
        '-y',  # Overwrite
        output_file
    ]
    
    try:
        # Run with timeout
        result = subprocess.run(
            cmd,
            timeout=600,  # 10 minutes max
            capture_output=True,
            check=True
        )
        return {'success': True, 'output': output_file}
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Timeout'}
    except subprocess.CalledProcessError as e:
        return {'success': False, 'error': e.stderr.decode()}
```

---

## Get Video Info (Before Encoding)

```bash
# Full details (JSON)
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4

# Duration only
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4

# Bitrate and resolution
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,bit_rate,width,height \
  -of default=noprint_wrappers=1 input.mp4
```

---

## Resources

- Full audit: `/root/uplevelia/projects/voilia/FFMPEG_AUDIT_DETAILED.md`
- Optimization guide: `/root/uplevelia/projects/voilia/FFMPEG_OPTIMIZATION_GUIDE.md`
- Executive summary: `/root/uplevelia/projects/voilia/FFMPEG_AUDIT_SUMMARY.md`

---

## Key Metrics to Monitor

**During Encoding**:
- CPU usage: Should be 75-100% (using all cores)
- Memory: Should stay < 500 MB
- Speed: Should be 0.5-2x realtime for medium preset

**After Encoding**:
- File exists and is readable
- File size reasonable (450 MB per hour for 1080p)
- PSNR > 40 dB (quality validation)

---

Last Updated: November 12, 2025
Status: Production Ready
