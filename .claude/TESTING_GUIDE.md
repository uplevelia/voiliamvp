# VOILIA Testing Guide

## Quick Session Verification Tests

When starting a new ccvoilia session, use these lightweight tests:

### ✅ Test 1: Context Loading (Fast)
```
What is the video processing pipeline?
```
**Expected:** 5-step pipeline (composition → overlay → mixing → concatenation → validation)

### ✅ Test 2: FFmpeg Presets (Fast)
```
What FFmpeg preset for TikTok?
```
**Expected:** 1080x1920, 30fps, CRF 23

### ✅ Test 3: MCP Connectivity (Lightweight)
```
Execute this SQL query on VOILIA: SELECT COUNT(*) FROM video_render_jobs LIMIT 1;
```
**Expected:** Returns count successfully

**⚠️ AVOID:** `List tables in VOILIA Supabase`
- Reason: Retrieves 93 table schemas (~245KB response)
- Use lightweight SQL queries instead

### ✅ Test 4: Project Knowledge (Fast)
```
Where is production code located?
```
**Expected:** `/opt/video-renderer/`

---

## MCP Best Practices

### Lightweight Operations ✅
```
- Execute small SQL queries (COUNT, SELECT with LIMIT)
- Query specific tables
- Check single records
```

### Heavy Operations ⚠️ (Avoid in tests)
```
- list_tables (93 schemas)
- SELECT * without LIMIT
- Large table scans
```

### Examples

**Good:**
```sql
SELECT COUNT(*) FROM video_render_jobs LIMIT 1;
SELECT * FROM video_render_jobs WHERE id = 'specific-id';
SELECT status, COUNT(*) FROM video_render_jobs GROUP BY status;
```

**Avoid in tests:**
```
List all tables
SELECT * FROM video_render_jobs (no LIMIT)
```

---

## Cache Performance Testing

### First Session (Cold Start)
```bash
ccvoilia
"What is the video processing pipeline?"
# Note response time
```

### Second Session (Cache Hit)
```bash
exit  # or Ctrl+D
ccvoilia
"What FFmpeg preset for YouTube?"
# Should be ~50% faster
```

**Expected:** Second session 3-5s vs first session 8-10s

---

## Session Startup Checklist

When launching ccvoilia:
- ✅ Directory: `~/uplevelia/projects/voilia`
- ✅ Model: Sonnet 4.5
- ✅ Context: VOILIA CLAUDE.md loaded
- ✅ MCP: voilia server accessible

Quick verification:
```
pwd && echo "Model: $(claude --version | grep -o 'Sonnet\|Haiku\|Opus')"
```

---

## Troubleshooting

### Context not loading?
```bash
cat .claude/CLAUDE.md  # Verify file exists
```

### MCP not connecting?
```bash
cat ~/.claude/mcp.json | grep voilia -A 5  # Check config
```

### Wrong directory?
```bash
type ccvoilia  # Verify function definition
```

---

**Last updated:** January 8, 2026
