# VOILIA - Full Stack Video Platform MVP

## Overview
Complete video rendering and management platform with FastAPI backend, Next.js frontend, and FFmpeg-based video processing engine.

## Project Locations (Stable - Cache Layer 1)
- **Production**: `/opt/video-renderer/` - Live FastAPI backend + rendering scripts
- **Development**: `/root/uplevelia/projects/voilia/` - Full stack codebase, docs, tests
- **GitHub**: `https://github.com/uplevelia/voiliamvp.git`

## Full Stack Architecture (Stable - Cache Layer 2)
- **Backend**: FastAPI + Celery workers
- **Frontend**: Next.js 14 + React + TypeScript
- **Video Engine**: FFmpeg 6.x (CPU encoding, no GPU)
- **Queue**: Redis + Celery for async jobs
- **Database**: PostgreSQL (Supabase project: mmrgefuweihgalyohnfz)
- **Storage**: S3-compatible (MinIO or AWS S3)
- **Infrastructure**: Docker Compose

## Tech Stack (Stable - Cache Layer 3)
- **Backend**: Python 3.11+, FastAPI, Celery, FFmpeg
- **Frontend**: Node.js 18+, Next.js 14, React 18, TypeScript
- **Database**: PostgreSQL 15+, Redis 7+
- **DevOps**: Docker, Docker Compose, Git

## Video Processing Pipeline (Stable - Cache Layer 4)
1. Scene composition (voiceover + image)
2. Text overlay rendering (subtitles, watermarks)
3. Music track mixing
4. Effects (Ken Burns, transitions, LUTs)
5. Final concatenation & encoding
6. Quality validation & upload

## FFmpeg Presets
- TikTok: 1080x1920, 30fps, CRF 23
- YouTube: 1920x1080, 60fps, CRF 18
- Instagram: 1080x1080, 30fps, CRF 21

## Key Directories
- `/opt/video-renderer/` - Production deployment
  - `api.py` - FastAPI backend
  - `render_video_v2.5.sh` - Main rendering engine
  - `ffmpeg_patterns.py` - FFmpeg utilities
- `/root/uplevelia/projects/voilia/` - Full repo
  - `tests/` - Test suites
  - `*.md` - Documentation

## MCP Database Guidelines (Stable - Cache Layer 5)
**Lightweight queries only:**
- ✅ Use: `SELECT COUNT(*)`, `SELECT * LIMIT 1`, specific queries
- ⚠️ Avoid: `list_tables` (93 schemas, ~245KB), `SELECT *` without LIMIT
- Test MCP: `SELECT COUNT(*) FROM video_render_jobs LIMIT 1;`

## Genius Orchestrator MCP - R&D Room

**VOILIA R&D Room ID**: `645b74b5-bde2-4fa9-84f2-599daeee27c8`

### Room Message Tools (via execute_tool)
| Tool | Purpose |
|------|---------|
| `post_room_message` | Post updates, status, discussions |
| `get_room_messages` | Fetch recent messages (auto-truncated) |
| `post_room_task` | Create tasks with P0-P3 priority |
| `complete_room_task` | Mark tasks as done |

### Quick Usage
```
# Search for room tools
mcp__genius-orchestrator__search_genius_tools("room message")

# Post a status update
mcp__genius-orchestrator__execute_tool("post_room_message", {
  "room_id": "645b74b5-bde2-4fa9-84f2-599daeee27c8",
  "content": "Video rendering pipeline optimized",
  "sender": "voilia-agent",
  "message_type": "status"
})

# Get recent messages
mcp__genius-orchestrator__execute_tool("get_room_messages", {
  "room_id": "645b74b5-bde2-4fa9-84f2-599daeee27c8",
  "limit": 5
})

# Create a task
mcp__genius-orchestrator__execute_tool("post_room_task", {
  "room_id": "645b74b5-bde2-4fa9-84f2-599daeee27c8",
  "title": "Optimize FFmpeg encoding",
  "description": "Reduce encoding time by 20%",
  "priority": "P1",
  "assignee": "backend"
})
```

### Context Safety Rules
- Always use LIMIT on message queries (max 10)
- Messages auto-truncate to 150 chars in responses
- Exit after posting to avoid context bloat

## Operational Guidelines

**VPS Operations Reference**: `/root/llmowner-backend/.claude/VPS_OPERATIONS_RUNBOOK.md`

### VOILIA-Specific Services
| Port | Service | Management |
|------|---------|------------|
| 5000 | voilia-api | systemd/Docker |
| 5001 | voilia-renderer | systemd: `voilia-renderer.service` |
| 5050 | video-renderer (Docker) | Container: `root-video-renderer-1` |
| 3080 | mvp-voilia | Docker container |

### Docker Containers (VOILIA Stack)
```bash
# Check container status
docker ps | grep -E "(voilia|video)"

# View renderer logs
docker logs root-video-renderer-1 -f --tail 100

# Systemd renderer
journalctl -u voilia-renderer -f
```

### Key Rules
- Port conflicts: RECONFIGURE new service, don't kill existing
- Video processing: Monitor CPU/memory during long renders
- Temp files: Always clean up `/tmp/voilia-renders/` after jobs
- Resource limits: Be mindful of concurrent render jobs

### Related Docs
- [VPS Operations Runbook](/root/llmowner-backend/.claude/VPS_OPERATIONS_RUNBOOK.md)
- [Cross-Project Coordination](/root/llmowner-backend/.claude/CROSS_PROJECT_COORDINATION.md)

## Error Learning (Project-Specific)

> Full protocol in global `~/.claude/CLAUDE.md`. This section sets **project context** so learnings are properly scoped.

**ALWAYS pass `project_id` when recording errors or getting tips:**
```
mcp__snap-memory__get_snap_tips({"task_description": "...", "category": "api", "project_id": "voilia"})
mcp__snap-memory__record_error({"error_pattern": "...", "category": "api", "project_id": "voilia"})
mcp__snap-memory__record_solution({"error_pattern": "...", "solution": "...", "success": true, "category": "api", "project_id": "voilia"})
```
This ensures: Voilia agents see global + voilia learnings, NOT llmowner/stayproperties internals.

## Claude Code v2.1.79

**Context & Performance:**
- **1M context window** for Opus 4.6 — full render logs and FFmpeg output fit in context (v2.1.75)
- **Opus 4.6 max output: 64k tokens** — longer code generation for render scripts (v2.1.77)
- **`/context`** — check context bloat from large render outputs (v2.1.74)
- **`/effort low|medium|high`** — adjust model effort mid-session (v2.1.76)

**Workflow:**
- **`/plan <description>`** — e.g., `/plan optimize Ken Burns pipeline` starts plan mode immediately (v2.1.72)
- **`/loop 5m /check`** — monitor render jobs on interval (v2.1.71)
- **`/copy N`** — copy Nth-latest response (v2.1.77)
- **`lsof`, `ss`, `pgrep`** auto-approved — no permission prompts for diagnostics (v2.1.72)

**Agent & Hooks:**
- **`SendMessage({to: agentId})`** to continue agents (v2.1.77)
- **`SessionEnd` hooks** fire correctly on `/resume` session switches (v2.1.79)
- **Agent `effort`, `maxTurns`, `disallowedTools` frontmatter** in agent definitions (v2.1.78)

## Current Tasks (Dynamic - Place Last for Cache Efficiency)
- Quality monitoring
- Template optimization
- n8n workflow integration
