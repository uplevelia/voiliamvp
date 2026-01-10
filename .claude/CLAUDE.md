# VOILIA Video Renderer

## System Architecture (Stable - Cache Layer 1)
- FastAPI backend for video processing
- CPU-based FFmpeg encoding (no GPU)
- Redis job queue
- PostgreSQL metadata storage
- Docker containerized

## Tech Stack (Stable - Cache Layer 2)
- Python 3.11+
- FFmpeg 6.x (libx264, AAC)
- FastAPI
- PostgreSQL
- Redis
- Docker

## Video Processing Pipeline (Stable - Cache Layer 3)
1. Scene composition (voiceover + image)
2. Text overlay rendering
3. Music track mixing
4. Final concatenation
5. Quality validation

## FFmpeg Presets (Stable - Cache Layer 4)
- TikTok: 1080x1920, 30fps, CRF 23
- YouTube: 1920x1080, 60fps, CRF 18
- Instagram: 1080x1080, 30fps, CRF 21

## Key Files
- `/opt/video-renderer/` - Production code
- Extensive documentation in project root
- `.claude/TESTING_GUIDE.md` - Session testing best practices

## MCP Database Guidelines (Stable - Cache Layer 5)
**Lightweight queries only:**
- ✅ Use: `SELECT COUNT(*)`, `SELECT * LIMIT 1`, specific queries
- ⚠️ Avoid: `list_tables` (93 schemas, ~245KB), `SELECT *` without LIMIT
- Test MCP: `SELECT COUNT(*) FROM video_render_jobs LIMIT 1;`

## Current Tasks (Dynamic - Place Last for Cache Efficiency)
- Quality monitoring
- Template optimization
- n8n workflow integration
