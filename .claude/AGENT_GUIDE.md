# VOILIA Agent Master Guide

**Complete reference for when and how to use each of the 12 specialized agents**

Last Updated: 2025-11-10
Version: 1.0
Project: VOILIA Video Rendering Service

---

## 📚 Table of Contents

1. [Quick Start (5 Minutes)](#quick-start-5-minutes)
2. [Quick Reference](#quick-reference)
3. [One-Page Cheat Sheet](#one-page-cheat-sheet)
4. [Agents by Development Phase](#agents-by-development-phase)
5. [Agents by Problem Type](#agents-by-problem-type)
6. [Individual Agent Guides](#individual-agent-guides)
7. [Common Workflows](#common-workflows)
8. [Decision Trees](#decision-trees)
9. [Real Conversation Examples](#real-conversation-examples)
10. [Common Mistakes](#common-mistakes)
11. [Performance Tips](#performance-tips)
12. [FAQ](#faq)
13. [Troubleshooting](#troubleshooting)

---

## Quick Start (5 Minutes)

**Welcome to VOILIA Agents!** Here's how to start using them right now:

### Your First Agent Interaction

1. **Navigate to your VOILIA directory:**
   ```bash
   cd /root/uplevelia/projects/voilia
   ```

2. **Ask Claude Code to use an agent:**
   ```
   "Use security-reviewer to check api/routes/upload.py for vulnerabilities"
   ```

3. **Review the output** - The agent will analyze the file and report findings

4. **Make fixes** based on the suggestions

That's it! You're now using agents.

### Try These Common Commands

```bash
# Check security before committing
"Run security-reviewer on all changed files"

# Execute your test suite
"Run test-runner to execute all tests"

# Check if system has enough resources
"Use performance-monitor to check current system health"

# Optimize an FFmpeg command
"Use ffmpeg-optimizer to review this command: ffmpeg -i input.mp4 -c:v libx264 output.mp4"

# Check video render output quality
"Use video-qa to validate /tmp/voilia-renders/job-123/output.mp4"
```

### What Makes Agents Useful?

- **Automated expertise**: Each agent is a specialist in its domain
- **Consistent quality**: Same thorough checks every time
- **Time-saving**: Catch issues before they become problems
- **Educational**: Learn best practices from agent recommendations

### Next Steps

- Read the [Cheat Sheet](#one-page-cheat-sheet) for quick command reference
- Check [Common Workflows](#common-workflows) for multi-agent tasks
- Review [FAQ](#faq) for common questions

---

## Quick Reference

| Agent | Primary Use | Invoke When | Key Output |
|-------|-------------|-------------|------------|
| **security-reviewer** | Find vulnerabilities | Before committing code | Security issues + fixes |
| **test-runner** | Execute tests | Development, CI/CD | Pass/fail + coverage |
| **ffmpeg-optimizer** | Video encoding | Creating/optimizing renders | Optimized FFmpeg commands |
| **docker-helper** | Container issues | Deployment, debugging | Container health status |
| **performance-monitor** | System resources | Capacity planning | Resource metrics + recommendations |
| **api-documenter** | API documentation | Adding/changing endpoints | OpenAPI specs + examples |
| **video-qa** | Output validation | After rendering | Quality score 0-100 |
| **deployment-helper** | Safe deployments | Before/during deploys | Deployment checklist + status |
| **dependency-manager** | Package updates | Weekly maintenance | Vulnerability report |
| **log-analyzer** | Debug issues | Production problems | Error patterns + root cause |
| **code-reviewer** | Code quality | Code reviews | Quality score + suggestions |
| **database-migration** | Schema changes | Database updates | Migration safety review |

---

## One-Page Cheat Sheet

**Quick command reference for common problems:**

| Problem | Agent | Command Example |
|---------|-------|-----------------|
| 🔒 Security issue | security-reviewer | `"Run security-reviewer on api/upload.py"` |
| 🧪 Test failure | test-runner | `"Run test-runner to execute all tests"` |
| 🎥 Slow render | ffmpeg-optimizer | `"Optimize this FFmpeg command: ffmpeg -i input.mp4..."` |
| 🐳 Container down | docker-helper | `"Check container health for voilia-api"` |
| 📈 High CPU | performance-monitor | `"Check system resources and identify bottlenecks"` |
| 📝 API change | api-documenter | `"Document the /api/render endpoint"` |
| ❌ Bad video | video-qa | `"QA this render: /tmp/voilia-renders/job-123/output.mp4"` |
| 🚀 Deploying | deployment-helper | `"Run pre-deployment checklist"` |
| 📦 Update pkg | dependency-manager | `"Check for dependency vulnerabilities"` |
| 🔥 Error spike | log-analyzer | `"Find recent errors in Docker logs"` |
| 💩 Code smell | code-reviewer | `"Review this function for complexity"` |
| 🗄️ DB change | database-migration | `"Review this Alembic migration for safety"` |

### 🎯 Most Common Daily Commands

```bash
# Morning / Start of work
"Use performance-monitor to check system health"
"Use log-analyzer to find any overnight errors"

# During development
"Run test-runner to execute all tests"
"Use code-reviewer on the function I just wrote"

# Before committing
"Run security-reviewer on all changed files"
"Run test-runner to verify all tests pass"

# Before deploying
"Use deployment-helper to run pre-deployment checklist"
"Use dependency-manager to check for CVEs"

# Weekly maintenance
"Use dependency-manager to check for package updates"
"Use log-analyzer to analyze error patterns this week"
"Use performance-monitor to check for resource trends"
```

### 🔗 Common Agent Combinations

**Full Security Audit:**
```
1. "Run security-reviewer on all Python files"
2. "Use dependency-manager to check for CVEs"
3. "Use docker-helper to review container security"
```

**Pre-Release Checklist:**
```
1. "Run test-runner to verify all tests pass"
2. "Run security-reviewer on changed files"
3. "Use api-documenter to update docs"
4. "Use deployment-helper for pre-deploy checklist"
```

**Debug Production Issue:**
```
1. "Use log-analyzer to find recent errors"
2. "Use performance-monitor to check system resources"
3. "Use docker-helper to check container health"
```

---

## Agents by Development Phase

### 🛠️ Development Phase

**When writing new features:**

1. **code-reviewer** - Review code quality as you write
   ```
   "Use code-reviewer to check this function for complexity"
   ```

2. **test-runner** - Run tests frequently
   ```
   "Run test-runner to execute unit tests"
   ```

3. **security-reviewer** - Check for security issues early
   ```
   "Use security-reviewer on the new upload endpoint"
   ```

**When working with video encoding:**

4. **ffmpeg-optimizer** - Optimize encoding commands
   ```
   "Use ffmpeg-optimizer to review this encoding command"
   ```

---

### 🔍 Code Review Phase

**Before committing:**

1. **security-reviewer** - Mandatory security check
2. **code-reviewer** - Quality and maintainability review
3. **test-runner** - Ensure all tests pass

**Example workflow:**
```bash
# 1. Security check
"Run security-reviewer on all changed files"

# 2. Quality check
"Use code-reviewer to review api/routes/render.py"

# 3. Test verification
"Run test-runner to verify all tests pass"
```

---

### 🚀 Pre-Deployment Phase

**Before deploying to production:**

1. **deployment-helper** - Run pre-deployment checklist
   ```
   "Use deployment-helper to check if we're ready to deploy"
   ```

2. **database-migration** - Review database changes
   ```
   "Use database-migration to review the schema changes"
   ```

3. **dependency-manager** - Check for vulnerabilities
   ```
   "Run dependency-manager security audit"
   ```

4. **docker-helper** - Verify container configuration
   ```
   "Use docker-helper to review docker-compose.yml"
   ```

---

### 📦 Deployment Phase

**During deployment:**

1. **deployment-helper** - Execute deployment
   ```
   "Use deployment-helper to perform zero-downtime deployment"
   ```

2. **docker-helper** - Monitor containers
   ```
   "Use docker-helper to check container health"
   ```

3. **performance-monitor** - Watch system resources
   ```
   "Run performance-monitor during deployment"
   ```

---

### 🔧 Post-Deployment Phase

**After deployment:**

1. **log-analyzer** - Monitor for errors
   ```
   "Use log-analyzer to check for errors in last 10 minutes"
   ```

2. **video-qa** - Validate video output
   ```
   "Run video-qa on the test render job"
   ```

3. **performance-monitor** - Verify system health
   ```
   "Use performance-monitor to check system status"
   ```

4. **api-documenter** - Update documentation
   ```
   "Use api-documenter to update OpenAPI specs"
   ```

---

### 🔄 Maintenance Phase

**Weekly maintenance:**

1. **dependency-manager** - Check for updates
   ```
   "Run dependency-manager weekly check"
   ```

2. **log-analyzer** - Generate weekly report
   ```
   "Use log-analyzer to create weekly error summary"
   ```

3. **performance-monitor** - Review trends
   ```
   "Use performance-monitor for weekly performance report"
   ```

---

## Agents by Problem Type

### 🐛 "Something is broken"

**Start here:**

1. **log-analyzer** - Find error messages
   ```
   "Use log-analyzer to find errors in last hour"
   ```

2. **performance-monitor** - Check if it's a resource issue
   ```
   "Run performance-monitor to check CPU/memory"
   ```

3. **docker-helper** - Check container status
   ```
   "Use docker-helper to check if containers are healthy"
   ```

**Video-specific issues:**

4. **video-qa** - Validate video output
   ```
   "Run video-qa on the failed render job"
   ```

5. **ffmpeg-optimizer** - Check encoding settings
   ```
   "Use ffmpeg-optimizer to review the encoding command"
   ```

---

### 🐌 "It's too slow"

1. **performance-monitor** - Identify bottleneck
   ```
   "Use performance-monitor to find the bottleneck"
   ```

2. **ffmpeg-optimizer** - Optimize encoding
   ```
   "Use ffmpeg-optimizer to speed up rendering"
   ```

3. **log-analyzer** - Find slow operations
   ```
   "Use log-analyzer to extract timing data"
   ```

4. **code-reviewer** - Check for performance anti-patterns
   ```
   "Use code-reviewer to find N+1 queries"
   ```

---

### 🔒 "Is this secure?"

1. **security-reviewer** - Comprehensive security check
   ```
   "Run security-reviewer on all code"
   ```

2. **dependency-manager** - Check for vulnerabilities
   ```
   "Use dependency-manager to scan for CVEs"
   ```

3. **docker-helper** - Review container security
   ```
   "Use docker-helper to check Docker security"
   ```

---

### 📊 "How do I document this?"

1. **api-documenter** - API endpoints
   ```
   "Use api-documenter to create OpenAPI spec for this endpoint"
   ```

2. **code-reviewer** - Code documentation
   ```
   "Use code-reviewer to check docstring quality"
   ```

---

### 🗄️ "I need to change the database"

1. **database-migration** - Create safe migration
   ```
   "Use database-migration to create migration for adding column"
   ```

2. **database-migration** - Review migration safety
   ```
   "Use database-migration to review this migration for data loss"
   ```

3. **database-migration** - Test rollback
   ```
   "Use database-migration to test downgrade procedure"
   ```

---

## Individual Agent Guides

### 1. security-reviewer

**When to use:**
- ✅ Before every commit (mandatory)
- ✅ During code review
- ✅ When handling user input
- ✅ When working with external APIs
- ✅ Pre-deployment security audit

**When NOT to use:**
- ❌ For code quality issues (use code-reviewer)
- ❌ For performance problems (use performance-monitor)

**Example usage:**
```
"Run security-reviewer on api/routes/upload.py"
"Use security-reviewer to check for SQL injection"
"Security review the authentication middleware"
```

**What it checks:**
- Hardcoded credentials
- Command injection
- SQL injection
- Path traversal
- Input validation
- Authentication/authorization

---

### 2. test-runner

**When to use:**
- ✅ During development (frequently)
- ✅ Before committing
- ✅ In CI/CD pipeline
- ✅ After refactoring
- ✅ When debugging test failures

**When NOT to use:**
- ❌ For code quality (use code-reviewer)
- ❌ For security (use security-reviewer)

**Example usage:**
```
"Run test-runner to execute all tests"
"Use test-runner to check coverage"
"Run test-runner on tests/unit/test_encoder.py"
```

**What it provides:**
- Pass/fail counts
- Coverage percentage
- Failed test details
- Suggestions for fixes

---

### 3. ffmpeg-optimizer

**When to use:**
- ✅ Creating new encoding presets
- ✅ Optimizing slow renders
- ✅ Reducing file sizes
- ✅ Improving video quality
- ✅ Benchmarking encoding options

**When NOT to use:**
- ❌ For non-video tasks
- ❌ After video is already rendered

**Example usage:**
```
"Use ffmpeg-optimizer to review this encoding command"
"Optimize this FFmpeg command for CPU-only rendering"
"Use ffmpeg-optimizer to suggest faster preset"
```

**What it analyzes:**
- Preset efficiency
- CRF values
- Filter chains
- Audio handling
- Thread optimization

---

### 4. docker-helper

**When to use:**
- ✅ Containers won't start
- ✅ Reviewing docker-compose.yml
- ✅ Optimizing Docker images
- ✅ Debugging container issues
- ✅ Cleaning up Docker resources

**When NOT to use:**
- ❌ For application code issues
- ❌ For database problems (unless connection-related)

**Example usage:**
```
"Use docker-helper to debug why API container keeps restarting"
"Review docker-compose.yml with docker-helper"
"Use docker-helper to optimize Dockerfile"
```

**What it handles:**
- Container debugging
- Health checks
- Resource limits
- Security best practices
- Cleanup and maintenance

---

### 5. performance-monitor

**When to use:**
- ✅ System feels slow
- ✅ Planning capacity
- ✅ Before scaling decisions
- ✅ During/after deployment
- ✅ Weekly health checks

**When NOT to use:**
- ❌ For code-level performance (use code-reviewer)
- ❌ For FFmpeg optimization (use ffmpeg-optimizer)

**Example usage:**
```
"Run performance-monitor to check system health"
"Use performance-monitor to analyze current load"
"Performance check before deploying new workers"
```

**What it monitors:**
- CPU usage and load
- Memory consumption
- Disk I/O
- Network usage
- Container resources

---

### 6. api-documenter

**When to use:**
- ✅ Adding new API endpoints
- ✅ Changing endpoint behavior
- ✅ Updating request/response models
- ✅ Before releasing API changes
- ✅ Onboarding new developers

**When NOT to use:**
- ❌ For internal functions (use code-reviewer)
- ❌ For database schema (use database-migration)

**Example usage:**
```
"Use api-documenter to create docs for /api/v1/render"
"Update OpenAPI spec with api-documenter"
"Create client examples with api-documenter"
```

**What it creates:**
- OpenAPI specifications
- Request/response examples
- cURL commands
- Python/JavaScript clients
- API changelogs

---

### 7. video-qa

**When to use:**
- ✅ After video rendering completes
- ✅ Before sending to client
- ✅ Debugging quality issues
- ✅ Validating new presets
- ✅ Testing encoding changes

**When NOT to use:**
- ❌ Before rendering (use ffmpeg-optimizer)
- ❌ For system performance (use performance-monitor)

**Example usage:**
```
"Run video-qa on job-abc123 output"
"Use video-qa to validate this render"
"Check video quality for completed job"
```

**What it validates:**
- Video codec and format
- Resolution and bitrate
- Audio/video sync
- Frame integrity
- File size
- Temp file cleanup
- S3 upload status

---

### 8. deployment-helper

**When to use:**
- ✅ Before every deployment
- ✅ During production releases
- ✅ When rollback is needed
- ✅ Setting up deployment automation
- ✅ Creating deployment runbooks

**When NOT to use:**
- ❌ During development
- ❌ For local testing

**Example usage:**
```
"Use deployment-helper to check deployment readiness"
"Run pre-deployment checklist"
"Use deployment-helper to perform zero-downtime deploy"
```

**What it provides:**
- Pre-deployment checklist
- Deployment procedures
- Health verification
- Rollback instructions
- Monitoring guidance

---

### 9. dependency-manager

**When to use:**
- ✅ Weekly maintenance
- ✅ Security vulnerabilities announced
- ✅ Before major version updates
- ✅ Reviewing new dependencies
- ✅ License compliance checks

**When NOT to use:**
- ❌ For application code issues
- ❌ During active development (unless adding deps)

**Example usage:**
```
"Run dependency-manager weekly check"
"Use dependency-manager to audit security vulnerabilities"
"Check if package updates are safe"
```

**What it manages:**
- Outdated packages
- Security vulnerabilities
- Upgrade safety
- Breaking changes
- License compliance

---

### 10. log-analyzer

**When to use:**
- ✅ Debugging production issues
- ✅ After deployment
- ✅ Investigating errors
- ✅ Creating incident reports
- ✅ Weekly health reviews

**When NOT to use:**
- ❌ For real-time monitoring (use performance-monitor)
- ❌ Before errors occur

**Example usage:**
```
"Use log-analyzer to find errors in last hour"
"Analyze job failures with log-analyzer"
"Create incident timeline with log-analyzer"
```

**What it analyzes:**
- Error frequencies
- Job failure patterns
- Performance metrics
- Anomaly detection
- Incident timelines

---

### 11. code-reviewer

**When to use:**
- ✅ During code review
- ✅ Refactoring code
- ✅ Learning best practices
- ✅ Before merging PRs
- ✅ Improving code quality

**When NOT to use:**
- ❌ For security (use security-reviewer)
- ❌ For test coverage (use test-runner)

**Example usage:**
```
"Use code-reviewer to review api/worker.py"
"Check this function for code smells"
"Review code quality before merge"
```

**What it reviews:**
- Function complexity
- Code duplication
- Naming conventions
- Documentation quality
- Type hints
- Design patterns

---

### 12. database-migration

**When to use:**
- ✅ Adding/removing columns
- ✅ Changing data types
- ✅ Creating indexes
- ✅ Data migrations
- ✅ Before schema changes

**When NOT to use:**
- ❌ For application logic changes
- ❌ For data queries (not schema)

**Example usage:**
```
"Use database-migration to create migration for new column"
"Review migration safety"
"Test migration rollback procedure"
```

**What it handles:**
- Migration generation
- Safety reviews
- Rollback testing
- Zero-downtime strategies
- Data migration patterns

---

## Common Workflows

### Workflow 1: Adding a New Feature

```
1. Write code
2. "Use code-reviewer to check code quality"
3. "Run security-reviewer on new code"
4. Write tests
5. "Run test-runner to verify tests pass"
6. Commit code
```

### Workflow 2: Deploying to Production

```
1. "Use deployment-helper for pre-deployment checklist"
2. "Run security-reviewer on all changed files"
3. "Use database-migration to review schema changes"
4. "Run test-runner to verify all tests pass"
5. "Use deployment-helper to perform deployment"
6. "Run performance-monitor during deployment"
7. "Use log-analyzer to check for errors post-deploy"
```

### Workflow 3: Debugging Production Issue

```
1. "Use log-analyzer to find recent errors"
2. "Run performance-monitor to check resources"
3. "Use docker-helper to check container health"
4. Fix issue
5. "Run test-runner to verify fix"
6. "Use deployment-helper to deploy hotfix"
```

### Workflow 4: Optimizing Video Rendering

```
1. "Use ffmpeg-optimizer to review encoding command"
2. Test new settings
3. "Run video-qa to validate output quality"
4. "Use performance-monitor to measure improvement"
5. Update presets
6. "Use api-documenter to update preset docs"
```

### Workflow 5: Weekly Maintenance

```
1. "Run dependency-manager weekly check"
2. "Use log-analyzer to create weekly error summary"
3. "Run performance-monitor for weekly health check"
4. "Use docker-helper to clean up unused resources"
5. Review and plan updates
```

---

## Decision Trees

### "I have an error - which agent?"

```
Is it a video rendering error?
├─ YES → Use log-analyzer to find error
│         └─ Video quality issue? → Use video-qa
│         └─ Encoding too slow? → Use ffmpeg-optimizer
│
└─ NO → What type of error?
          ├─ Security issue → security-reviewer
          ├─ Test failure → test-runner
          ├─ Container issue → docker-helper
          ├─ Database error → database-migration
          ├─ Performance issue → performance-monitor
          └─ Code quality → code-reviewer
```

### "I want to improve something - which agent?"

```
What do you want to improve?
├─ Video encoding speed → ffmpeg-optimizer
├─ Code quality → code-reviewer
├─ Security posture → security-reviewer
├─ Test coverage → test-runner
├─ Documentation → api-documenter
├─ System performance → performance-monitor
├─ Container efficiency → docker-helper
├─ Deployment process → deployment-helper
├─ Dependencies → dependency-manager
└─ Error handling → log-analyzer
```

### "I'm about to deploy - which agents?"

```
Pre-deployment (all mandatory):
1. deployment-helper (checklist)
2. security-reviewer (security scan)
3. test-runner (all tests pass)
4. database-migration (if schema changes)
5. dependency-manager (if deps changed)

During deployment:
1. deployment-helper (execute)
2. docker-helper (monitor)
3. performance-monitor (watch resources)

Post-deployment:
1. log-analyzer (check errors)
2. video-qa (validate output)
3. performance-monitor (verify health)
```

---

## Agent Combinations

Some tasks benefit from multiple agents:

### Security Audit (Comprehensive)
```
1. security-reviewer (code vulnerabilities)
2. dependency-manager (package CVEs)
3. docker-helper (container security)
4. code-reviewer (secure coding practices)
```

### Performance Optimization
```
1. performance-monitor (identify bottleneck)
2. ffmpeg-optimizer (optimize encoding)
3. code-reviewer (code-level optimization)
4. log-analyzer (find slow operations)
```

### Pre-Production Checklist
```
1. test-runner (all tests green)
2. security-reviewer (no vulnerabilities)
3. code-reviewer (quality standards met)
4. deployment-helper (ready to deploy)
5. database-migration (schema safe)
6. dependency-manager (no critical CVEs)
```

---

## Quick Tips

### 🎯 Always Use Before Committing:
- security-reviewer
- test-runner

### 🎯 Always Use Before Deploying:
- deployment-helper
- security-reviewer
- test-runner

### 🎯 Use Weekly:
- dependency-manager
- log-analyzer
- performance-monitor

### 🎯 Use As Needed:
- ffmpeg-optimizer (video work)
- video-qa (after renders)
- docker-helper (container issues)
- api-documenter (API changes)
- code-reviewer (code reviews)
- database-migration (schema changes)

---

## Real Conversation Examples

**See how agents work in actual Claude Code sessions:**

### Example 1: Security Review of New Feature

**You:** "I just added a file upload endpoint in `api/routes/upload.py`. Can you review it for security?"

**Claude:** "I'll use the security-reviewer agent to check for common vulnerabilities in file upload handlers."

*[Uses security-reviewer agent]*

**Claude:** "Found 3 critical issues:

1. **No file size limit** (line 45)
   ```python
   # Bad
   file.save(f"/tmp/{filename}")

   # Fix
   MAX_SIZE = 50 * 1024 * 1024  # 50MB
   if len(file_data) > MAX_SIZE:
       raise ValueError("File too large")
   ```

2. **No file type validation** (line 47)
   - Add MIME type checking
   - Whitelist allowed extensions

3. **Path traversal vulnerability** (line 52)
   ```python
   # Bad
   path = f"/uploads/{user_filename}"

   # Fix
   from pathlib import Path
   safe_path = Path("/uploads") / Path(user_filename).name
   ```

I can help implement these fixes. Would you like me to update the file?"

---

### Example 2: Debugging Production Issue

**You:** "We're getting errors in production. Can you help debug?"

**Claude:** "Let me check the logs first."

*[Uses log-analyzer agent]*

**Claude:** "Found 47 errors in the last hour, mostly:
```
Error: S3 upload failed - Connection timeout
Count: 38 occurrences
First seen: 2025-11-10 14:23:15
```

This looks like a connectivity issue. Let me check system resources..."

*[Uses performance-monitor agent]*

**Claude:** "System looks healthy:
- CPU: 45% (normal)
- Memory: 62% (normal)
- Disk: 23% (good)
- Network: Normal throughput

The issue appears to be with S3 connectivity, not system resources. Here's what to check:

1. Verify S3_ENDPOINT is correct in .env
2. Check if S3 service is accessible: `curl $S3_ENDPOINT`
3. Review S3 credentials validity
4. Check network firewall rules

Would you like me to help verify these?"

---

### Example 3: Pre-Deployment Checklist

**You:** "We're ready to deploy to production. Can you run the pre-deployment checks?"

**Claude:** "I'll use the deployment-helper agent to run the checklist."

*[Uses deployment-helper agent]*

**Claude:** "Pre-Deployment Checklist Results:

✅ **Passed (10/12)**
- Tests passing
- Security scan clean
- Dependencies up to date
- Database migrations ready
- Docker images built
- Environment variables set
- Backup created
- Documentation updated
- API endpoints documented
- Monitoring configured

❌ **Failed (2/12)**
- **SSL certificate expires in 5 days** - CRITICAL
  Action: Renew certificate before deployment

- **Celery workers not scaled up** - WARNING
  Current: 2 workers
  Recommended for production: 4 workers
  Action: Update docker-compose.prod.yml

**Recommendation:** Fix the SSL certificate issue before deploying (CRITICAL). The worker scaling is a warning but should be addressed for optimal performance.

Should I help you renew the SSL certificate?"

---

### Example 4: Optimizing Video Encoding

**You:** "This FFmpeg command is taking too long: `ffmpeg -i input.mp4 -c:v libx264 -preset veryslow -crf 18 output.mp4`"

**Claude:** "Let me use ffmpeg-optimizer to analyze this."

*[Uses ffmpeg-optimizer agent]*

**Claude:** "Found the issue! You're using `preset veryslow` which is extremely slow on CPU.

**Current command analysis:**
- Preset: `veryslow` - 5-10x slower than needed
- CRF: 18 - High quality (good)
- Encoding speed estimate: 0.2x realtime (very slow)

**Optimized command:**
```bash
ffmpeg -i input.mp4 -c:v libx264 -preset medium -crf 23 output.mp4
```

**Impact:**
- Speed: 5-8x faster encoding (0.2x → 1.5x realtime)
- Quality: Still very good (CRF 23 is excellent for web)
- File size: Slightly larger (~10%), but negligible for web delivery

**Why this works:**
- `medium` preset is the sweet spot for CPU encoding
- CRF 23 gives perceptually identical quality for most content
- You'll finish in 1/5th the time with minimal quality difference

Would you like me to test this on a sample first?"

---

## Common Mistakes

**Avoid these pitfalls when using agents:**

### ❌ Mistake 1: Using Wrong Agent for the Task

**Wrong:** "Use performance-monitor to check my code quality"
**Right:** "Use code-reviewer to check my code quality"

**Why:** Each agent is specialized. Performance-monitor checks CPU/memory/disk, not code quality.

---

### ❌ Mistake 2: Being Too Vague

**Wrong:** "Check for issues"
**Right:** "Use security-reviewer on api/routes/upload.py to check for file upload vulnerabilities"

**Why:** Specific requests get specific, actionable results. Vague requests lead to vague answers.

---

### ❌ Mistake 3: Ignoring Agent Recommendations

**Wrong:** Dismissing all security warnings as "false positives" without investigation
**Right:** Review each suggestion, understand the risk, implement critical fixes

**Why:** Agents are designed to catch real issues. If something seems wrong, investigate first.

---

### ❌ Mistake 4: Not Combining Agents

**Wrong:** Only running security-reviewer before deploying
**Right:** Running security-reviewer + test-runner + deployment-helper

**Why:** Different agents catch different issues. Combine them for comprehensive coverage.

---

### ❌ Mistake 5: Not Reading Agent Output

**Wrong:** "Did the tests pass?" without reading the detailed output
**Right:** Read the full report, understand failures, check coverage gaps

**Why:** Agent reports contain valuable details: which tests failed, why, what to fix, coverage gaps.

---

### ❌ Mistake 6: Running Agents Only at the End

**Wrong:** Writing 500 lines of code, then running security-reviewer
**Right:** Running agents incrementally as you develop

**Why:** Catching issues early is faster and easier than fixing them later.

---

### ❌ Mistake 7: Not Using Agents for Learning

**Wrong:** Just applying fixes without understanding why
**Right:** Reading agent explanations, learning security/performance best practices

**Why:** Agents teach best practices. Understanding the "why" makes you a better developer.

---

## Performance Tips

**Make agents faster and more useful:**

### For Faster Agent Responses

1. **Be specific about what to check**
   - Good: "Check api/upload.py for path traversal vulnerabilities"
   - Bad: "Check all files for everything"

2. **Point to specific files/functions**
   - "Review the `encode_video()` function in renderer/encoder.py"
   - Not: "Check the video encoding stuff"

3. **Ask for summaries when output is long**
   - "Summarize the key security issues only"
   - "Show me just the critical findings"

---

### For Better Results

1. **Provide context**
   - "This is a file upload handler that stores videos to S3"
   - Not just: "Review this file"

2. **Mention your concerns**
   - "I'm worried about command injection in the FFmpeg wrapper"
   - "Check if this migration could cause data loss"

3. **Ask follow-up questions**
   - "Why is this a security issue?"
   - "What's the best way to fix this?"
   - "Can you show me an example?"

---

### For Complex Tasks

1. **Use multiple agents in sequence**
   ```
   1. "Use security-reviewer to find issues"
   2. [Fix issues]
   3. "Run security-reviewer again to verify fixes"
   4. "Run test-runner to ensure nothing broke"
   ```

2. **Iterate: Fix → Re-run → Verify**
   - Don't try to fix everything at once
   - Fix critical issues first
   - Re-run agent to verify

3. **Combine with manual review**
   - Agents are very good, not perfect
   - Use them to catch 95% of issues
   - Manual review catches the edge cases

---

## FAQ

### Q: Can I use multiple agents at once?

**A:** Yes! For example:

```
"Use security-reviewer and code-reviewer on api/upload.py"
```

However, it's often clearer to run them sequentially so you can act on findings from each.

---

### Q: How often should I run agents?

**A:**

**Every commit:**
- security-reviewer
- test-runner

**Every code change:**
- code-reviewer (as you write)
- test-runner (to verify)

**Before deployment:**
- security-reviewer
- test-runner
- deployment-helper
- dependency-manager

**Weekly maintenance:**
- dependency-manager (check for updates)
- log-analyzer (review error patterns)
- performance-monitor (check trends)

**As needed:**
- ffmpeg-optimizer (when working with video)
- video-qa (after renders)
- docker-helper (when container issues occur)
- api-documenter (when API changes)
- database-migration (when schema changes)

---

### Q: Do agents replace code review?

**A:** No, they **augment** it.

**Agents are great at:**
- Finding common security vulnerabilities
- Checking code complexity
- Running tests consistently
- Identifying performance issues

**Humans are better at:**
- Understanding business logic
- Architectural decisions
- User experience considerations
- Complex edge cases

**Best practice:** Use agents for automated checks, humans for strategic review.

---

### Q: Can I customize agents?

**A:** Yes! Edit the `.md` files in `.claude/agents/`

Each agent is just a markdown file with instructions. You can:
- Add project-specific checks
- Customize output format
- Add additional examples
- Tune for your workflow

Example: Add a custom check to security-reviewer:
```markdown
## Custom VOILIA Checks

### Check for Exposed Render Paths
- Look for any code that returns /tmp/voilia-renders paths to users
- These should be S3 presigned URLs, never local paths
```

---

### Q: What if an agent gives a false positive?

**A:** Investigate first, then:

1. **Verify it's actually a false positive**
   - Sometimes "false positives" are real issues
   - Understand the agent's reasoning

2. **Document why it's safe**
   ```python
   # SECURITY: This is safe because input is validated against
   # ALLOWED_PRESETS whitelist above (line 45)
   preset = user_input
   ```

3. **If consistently wrong, customize the agent**
   - Edit the agent's .md file to skip this check
   - Or add context for why it's acceptable in your codebase

---

### Q: Can agents work with languages other than Python?

**A:** Yes! Agents work with:

- **Python** - Full support for FastAPI, Django, Flask, etc.
- **JavaScript/TypeScript** - Full support for Node.js, React, Next.js
- **Bash/Shell** - For scripts and deployment automation
- **Docker** - docker-helper reviews Dockerfiles and compose files
- **SQL** - database-migration reviews migrations
- **YAML/JSON** - Configuration files

The agents analyze any code you provide them.

---

### Q: How do I know which agent to use?

**A:** Use the [Cheat Sheet](#one-page-cheat-sheet) or [Decision Trees](#decision-trees).

**Quick mental model:**
- **Problem with code?** → code-reviewer or security-reviewer
- **Problem with system?** → performance-monitor or docker-helper
- **Problem with video?** → ffmpeg-optimizer or video-qa
- **Problem in production?** → log-analyzer
- **About to deploy?** → deployment-helper
- **Need docs?** → api-documenter
- **Database change?** → database-migration
- **Package updates?** → dependency-manager
- **Tests?** → test-runner

---

## Troubleshooting

**Common issues when using agents:**

### "Agent didn't understand my request"

**Problem:** Vague or ambiguous instructions

**Fix:**
- Be specific: "Use security-reviewer on api/upload.py"
- Not: "check security"

**Example:**
```
❌ "Check the video stuff"
✅ "Use ffmpeg-optimizer to review the encoding command in renderer/encoder.py line 45"
```

---

### "Agent output is too verbose"

**Problem:** Agent provided more detail than needed

**Fix:**
- Ask for summary: "Summarize the key issues only"
- Request specific information: "Show only critical security findings"
- Ask for just the command: "Show me the optimized FFmpeg command without explanation"

**Example:**
```
❌ [Receives 200 lines of output]
✅ "Summarize the security-reviewer findings in 3 bullet points"
```

---

### "Agent missed something obvious"

**Problem:** Agents have limitations and context windows

**Fix:**
- Agents are very good, not perfect
- Always do manual review for critical code
- Point out what was missed: "Also check for race conditions in the job queue"
- Report patterns to improve agent instructions (edit the .md file)

**Remember:** Agents catch 95% of issues. You catch the remaining 5%.

---

### "I don't know which agent to use"

**Problem:** Unclear which agent fits the task

**Fix:**
- Check the [Cheat Sheet](#one-page-cheat-sheet)
- Use the [Decision Trees](#decision-trees)
- When in doubt, describe your problem: "I have slow Docker containers, which agent should I use?"

---

### "Agent recommendations are overwhelming"

**Problem:** Too many issues found at once

**Fix:**
- Prioritize: Fix critical issues first
- Address one category at a time
- Ask: "Show me only the critical security issues"
- Iterate: Fix a few, re-run, repeat

**Example workflow:**
```
1. "Run security-reviewer" → finds 15 issues
2. "Show me only the critical issues" → 3 issues
3. [Fix those 3]
4. "Run security-reviewer again" → finds 12 issues (3 fixed)
5. Repeat
```

---

### "Agent gave outdated advice"

**Problem:** Agent instructions may not reflect latest best practices

**Fix:**
- Agents are updated periodically
- If you find outdated advice, edit the agent's .md file
- Add current best practices
- Share improvements with team

---

### "How do I test if an agent is working?"

**Problem:** Want to verify agent functionality

**Fix:**

Run the test scripts in `tests/agent-tests/`:

```bash
# Test all agents
bash tests/agent-tests/test_all_agents.sh

# Test specific agent
bash tests/agent-tests/test_security_reviewer.sh
```

Or manually test:
```
"Use security-reviewer on tests/agent-tests/video_processor.py"
# Should find 14 vulnerabilities in this test file
```

---

### "Agent is taking too long"

**Problem:** Agent seems stuck or slow

**Fix:**
- Large files take longer - be patient
- Narrow the scope: Check specific files, not entire codebase
- For very large codebases, use agents on changed files only

**Example:**
```
❌ "Run security-reviewer on all files" (100+ files)
✅ "Run security-reviewer on recently changed files: api/upload.py, api/render.py"
```

---

## Getting Help

**To use any agent, simply ask Claude Code:**

```
"Use [agent-name] to [task]"
```

**Examples:**
- "Use security-reviewer to check api/upload.py"
- "Run test-runner to execute all tests"
- "Use ffmpeg-optimizer to review this command"
- "Run performance-monitor to check system health"

**For more details on any agent:**
- Read the agent's `.md` file in `.claude/agents/`
- Each agent has comprehensive documentation and examples

---

## Version History

- **v1.0** (2025-11-10): Initial master guide creation
  - All 12 agents documented
  - Workflows and decision trees added
  - Common use cases covered

---

**Remember:** These agents are tools to help you. Use them liberally, combine them as needed, and customize them for your workflow!
