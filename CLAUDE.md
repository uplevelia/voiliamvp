# VOILIA - Video Renderer

## What It Does
CPU-based video rendering service using FFmpeg. Transforms video assets with various effects, overlays, and encoding presets.

## Tech Stack
- **Video Processing**: FFmpeg 6.1+ (CPU encoding only - no GPU)
- **Backend**: FastAPI + Celery + RabbitMQ for async job processing
- **Frontend**: Next.js 14 + React
- **Storage**: S3-compatible (MinIO or AWS S3)
- **Database**: PostgreSQL (job metadata), Redis (queue + cache)
- **Infrastructure**: Docker Compose

## Key Commands

### Development
```bash
# Backend API
cd api && uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm run dev

# Worker (Celery)
cd api && celery -A worker worker --loglevel=info

# Tests
pytest tests/ -v

# Docker (full stack)
docker compose up -d
docker compose logs -f voilia-api
```

### Video Processing
```bash
# Test FFmpeg encoding
ffmpeg -i input.mp4 -c:v libx264 -preset medium -crf 23 output.mp4

# Probe video info
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

## Project Structure
```
voilia/
├── api/                    # FastAPI backend
│   ├── main.py            # API entry point
│   ├── worker.py          # Celery worker
│   ├── routes/            # API endpoints
│   └── services/          # Business logic
├── renderer/              # FFmpeg wrapper & rendering logic
│   ├── ffmpeg_wrapper.py  # FFmpeg command builder
│   ├── presets/           # Encoding presets
│   └── effects/           # Video effects modules
├── frontend/              # Next.js application
│   ├── app/              # App router pages
│   ├── components/       # React components
│   └── lib/              # Utilities
├── tests/                 # Test suites
│   ├── unit/
│   └── integration/
├── config/                # Configuration files
│   └── encoder-presets/   # FFmpeg encoding presets
├── docker-compose.yml     # Local dev environment
├── Dockerfile.api         # API container
└── Dockerfile.worker      # Worker container
```

## Important Constraints
- **CPU-only encoding**: No GPU acceleration (use presets: `medium`, `fast`)
- **Temp files**: Always write to `/tmp/voilia-renders/[job_id]/`
- **Cleanup**: Delete temp files after upload or on failure
- **Resource monitoring**: Log CPU/memory usage for long renders
- **Timeouts**: Set reasonable timeouts (max 10 min per job)

## Encoding Presets
Located in `config/encoder-presets/`:
- `web-optimized.json` - Small file size, good quality (CRF 23)
- `high-quality.json` - Larger files, better quality (CRF 18)
- `fast-preview.json` - Quick previews (CRF 28, preset veryfast)

## Development Tips
- Use `ffprobe` to inspect video metadata before processing
- Test encoding presets on small video clips first
- Monitor `/tmp` disk usage during development
- Check Celery logs for job failures: `docker compose logs voilia-worker`

## Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/voilia

# Redis
REDIS_URL=redis://localhost:6379/0

# Storage
S3_ENDPOINT=http://localhost:9000
S3_BUCKET=voilia-renders
S3_ACCESS_KEY=...
S3_SECRET_KEY=...

# API
API_SECRET_KEY=...
ENVIRONMENT=development
```

See `.env.example` for full list.
