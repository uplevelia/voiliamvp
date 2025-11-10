# Database Migration Agent

## Purpose
Manage database schema changes using Alembic migrations for VOILIA project. Generate safe migrations, review for data loss risks, test rollback procedures, and ensure zero-downtime deployments.

## Core Tasks

### 1. Generate Migration from Models

**Auto-generate migration:**
```bash
# Generate migration from SQLAlchemy model changes
alembic revision --autogenerate -m "add watermark_settings column"

# Review generated migration file
cat alembic/versions/abc123_add_watermark_settings.py

# Check what will be applied
alembic upgrade --sql head
```

**Manual migration template:**
```bash
# Create empty migration for data changes
alembic revision -m "migrate_old_preset_format"

# Edit the generated file
vim alembic/versions/xyz789_migrate_old_preset_format.py
```

**Example migration:**
```python
"""add watermark settings column

Revision ID: abc123def456
Revises: previous_revision
Create Date: 2025-11-10 12:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123def456'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    # Add column
    op.add_column(
        'render_jobs',
        sa.Column('watermark_settings', sa.JSON(), nullable=True)
    )

    # Create index
    op.create_index(
        'ix_render_jobs_created_at',
        'render_jobs',
        ['created_at']
    )

def downgrade():
    # Remove index
    op.drop_index('ix_render_jobs_created_at', table_name='render_jobs')

    # Remove column
    op.drop_column('render_jobs', 'watermark_settings')
```

### 2. Migration Safety Review

**Data loss risk checklist:**
```markdown
## Migration Safety Checklist

### ❌ Dangerous Operations (can lose data)
- [ ] DROP TABLE
- [ ] DROP COLUMN
- [ ] ALTER COLUMN ... DROP DEFAULT
- [ ] ALTER COLUMN ... TYPE (without USING clause)
- [ ] TRUNCATE TABLE
- [ ] DELETE without WHERE clause

### ⚠️ Risky Operations (need careful review)
- [ ] ADD COLUMN ... NOT NULL (without DEFAULT)
- [ ] ALTER COLUMN ... NOT NULL
- [ ] ADD UNIQUE CONSTRAINT
- [ ] ADD FOREIGN KEY CONSTRAINT
- [ ] RENAME TABLE/COLUMN

### ✅ Safe Operations
- [ ] CREATE TABLE
- [ ] ADD COLUMN ... NULL
- [ ] ADD COLUMN ... DEFAULT
- [ ] CREATE INDEX (CONCURRENTLY in production)
- [ ] DROP INDEX
```

**Review script:**
```python
#!/usr/bin/env python
# review_migration.py

import re
import sys

DANGEROUS_PATTERNS = [
    r'op\.drop_table',
    r'op\.drop_column',
    r'\.drop\(',
    r'DELETE FROM',
    r'TRUNCATE',
]

RISKY_PATTERNS = [
    r'NOT NULL',
    r'UNIQUE',
    r'FOREIGN KEY',
    r'\.rename\(',
]

def review_migration(file_path):
    """Review migration for dangerous operations"""

    with open(file_path, 'r') as f:
        content = f.read()

    issues = []

    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"❌ DANGEROUS: Found '{pattern}'")

    # Check for risky patterns
    for pattern in RISKY_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"⚠️  RISKY: Found '{pattern}'")

    # Report
    if issues:
        print("Migration Safety Review:")
        print("━" * 50)
        for issue in issues:
            print(issue)
        print("━" * 50)
        print("Review carefully before applying!")
        return 1
    else:
        print("✅ Migration looks safe")
        return 0

if __name__ == "__main__":
    sys.exit(review_migration(sys.argv[1]))
```

### 3. Test Migrations

**Test upgrade and downgrade:**
```bash
#!/bin/bash
# test-migration.sh

set -e

MIGRATION_ID=$1

echo "=== Testing Migration: $MIGRATION_ID ==="
echo ""

# 1. Backup current database
echo "[1/5] Creating database backup..."
pg_dump -h localhost -U postgres voilia > /tmp/voilia_backup.sql
echo "✓ Backup created"

# 2. Get current revision
echo "[2/5] Current revision:"
alembic current
CURRENT_REV=$(alembic current | grep -oP '[a-f0-9]{12}')

# 3. Test upgrade
echo "[3/5] Testing upgrade to $MIGRATION_ID..."
if alembic upgrade "$MIGRATION_ID"; then
  echo "✓ Upgrade successful"
else
  echo "✗ Upgrade failed"
  echo "Restoring database..."
  psql -h localhost -U postgres voilia < /tmp/voilia_backup.sql
  exit 1
fi

# 4. Test downgrade
echo "[4/5] Testing downgrade..."
if alembic downgrade "$CURRENT_REV"; then
  echo "✓ Downgrade successful"
else
  echo "✗ Downgrade failed"
  echo "Restoring database..."
  psql -h localhost -U postgres voilia < /tmp/voilia_backup.sql
  exit 1
fi

# 5. Re-apply for testing
echo "[5/5] Re-applying migration..."
alembic upgrade "$MIGRATION_ID"

echo ""
echo "✅ Migration tested successfully"
echo "Current schema:"
alembic current
```

### 4. Data Migration Patterns

**Add column with default:**
```python
def upgrade():
    # Add nullable column first
    op.add_column('render_jobs', sa.Column('priority', sa.Integer(), nullable=True))

    # Update existing rows
    op.execute("UPDATE render_jobs SET priority = 5 WHERE priority IS NULL")

    # Then make it NOT NULL
    op.alter_column('render_jobs', 'priority', nullable=False)
```

**Rename column safely:**
```python
def upgrade():
    # Step 1: Add new column
    op.add_column('render_jobs', sa.Column('preset_name', sa.String(50), nullable=True))

    # Step 2: Copy data
    op.execute("UPDATE render_jobs SET preset_name = preset WHERE preset_name IS NULL")

    # Step 3: Make new column NOT NULL
    op.alter_column('render_jobs', 'preset_name', nullable=False)

    # Step 4: Drop old column (in next migration after deploy)
    # op.drop_column('render_jobs', 'preset')
```

**Split column into multiple:**
```python
def upgrade():
    # Add new columns
    op.add_column('render_jobs', sa.Column('video_codec', sa.String(20), nullable=True))
    op.add_column('render_jobs', sa.Column('audio_codec', sa.String(20), nullable=True))

    # Migrate data from old column
    connection = op.get_bind()
    render_jobs = connection.execute(
        "SELECT id, codec_settings FROM render_jobs WHERE codec_settings IS NOT NULL"
    )

    for job_id, codec_settings in render_jobs:
        # Parse old format
        settings = json.loads(codec_settings)
        connection.execute(
            "UPDATE render_jobs SET video_codec = %s, audio_codec = %s WHERE id = %s",
            (settings['video'], settings['audio'], job_id)
        )

    # Make columns NOT NULL
    op.alter_column('render_jobs', 'video_codec', nullable=False)
    op.alter_column('render_jobs', 'audio_codec', nullable=False)

def downgrade():
    # Reconstruct original data
    connection = op.get_bind()
    render_jobs = connection.execute(
        "SELECT id, video_codec, audio_codec FROM render_jobs"
    )

    for job_id, video_codec, audio_codec in render_jobs:
        settings = json.dumps({'video': video_codec, 'audio': audio_codec})
        connection.execute(
            "UPDATE render_jobs SET codec_settings = %s WHERE id = %s",
            (settings, job_id)
        )

    op.drop_column('render_jobs', 'audio_codec')
    op.drop_column('render_jobs', 'video_codec')
```

### 5. Zero-Downtime Migrations

**Multi-phase deployment:**
```markdown
## Zero-Downtime Migration Strategy

### Phase 1: Add new schema (backward compatible)
```python
def upgrade():
    # Add new column (nullable)
    op.add_column('render_jobs', sa.Column('new_field', sa.String(), nullable=True))

    # Deploy application code that writes to both old and new fields
```

### Phase 2: Migrate data (background job)
```python
# Run data migration in batches
def migrate_data_batch():
    connection = op.get_bind()
    while True:
        result = connection.execute("""
            UPDATE render_jobs
            SET new_field = old_field
            WHERE new_field IS NULL
            LIMIT 1000
        """)
        if result.rowcount == 0:
            break
        time.sleep(1)  # Avoid overwhelming DB
```

### Phase 3: Make required (another deploy)
```python
def upgrade():
    # All data migrated, make NOT NULL
    op.alter_column('render_jobs', 'new_field', nullable=False)

    # Deploy code that only uses new_field
```

### Phase 4: Remove old schema (final deploy)
```python
def upgrade():
    # Safe to drop old column
    op.drop_column('render_jobs', 'old_field')
```
```

**Index creation (no downtime):**
```python
def upgrade():
    # Use CONCURRENTLY to avoid table lock
    op.create_index(
        'ix_render_jobs_status_created',
        'render_jobs',
        ['status', 'created_at'],
        postgresql_concurrently=True
    )

def downgrade():
    op.drop_index('ix_render_jobs_status_created', table_name='render_jobs')
```

### 6. Migration Status Management

**Check migration status:**
```bash
# Current database revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --verbose | grep "(pending)"

# Show last 5 migrations
alembic history -r -5:

# Verify database schema
alembic check
```

**Migration status script:**
```bash
#!/bin/bash
# check-migration-status.sh

echo "=== Migration Status ==="
echo ""

# Current revision
echo "Current revision:"
alembic current
echo ""

# Pending migrations
PENDING=$(alembic history --verbose | grep -c "(pending)")
if [ $PENDING -eq 0 ]; then
  echo "✅ No pending migrations"
else
  echo "⚠️  Pending migrations: $PENDING"
  echo ""
  echo "Pending changes:"
  alembic history --verbose | grep -A 1 "(pending)"
fi

echo ""

# Database connectivity
echo "Database connection:"
if psql -h localhost -U postgres -d voilia -c "SELECT 1" > /dev/null 2>&1; then
  echo "✓ Connected"
else
  echo "✗ Cannot connect"
  exit 1
fi
```

### 7. Rollback Procedures

**Rollback single migration:**
```bash
# Downgrade one revision
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade abc123def456

# Downgrade to base (empty database)
alembic downgrade base

# Show SQL without applying
alembic downgrade -1 --sql
```

**Emergency rollback script:**
```bash
#!/bin/bash
# emergency-rollback.sh

set -e

echo "⚠️  EMERGENCY DATABASE ROLLBACK ⚠️"
echo ""

# Get current revision
CURRENT=$(alembic current | grep -oP '[a-f0-9]{12}')
echo "Current revision: $CURRENT"

# Get previous revision
PREVIOUS=$(alembic history -r -2: | grep -oP '[a-f0-9]{12}' | tail -1)
echo "Rolling back to: $PREVIOUS"

read -p "Continue with rollback? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Rollback cancelled"
  exit 0
fi

# Backup before rollback
echo ""
echo "Creating backup..."
pg_dump -h localhost -U postgres voilia > "/tmp/backup-before-rollback-$(date +%Y%m%d_%H%M%S).sql"
echo "✓ Backup created"

# Perform rollback
echo ""
echo "Rolling back migration..."
if alembic downgrade "$PREVIOUS"; then
  echo "✅ ROLLBACK SUCCESSFUL"
  alembic current
else
  echo "❌ ROLLBACK FAILED"
  echo "Restore from backup if needed"
  exit 1
fi
```

### 8. Conflict Resolution

**Merge migrations:**
```bash
# If you have parallel development branches
alembic history

# Shows:
# abc123 -> (head)
# def456 -> (head)
# Both point to same parent

# Create merge migration
alembic merge -m "merge parallel migrations" abc123 def456

# This creates a merge revision pointing to both heads
```

**Handle conflicts:**
```python
# If autogenerate creates conflicting changes
def upgrade():
    # Check if column already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('render_jobs')]

    if 'new_column' not in columns:
        op.add_column('render_jobs', sa.Column('new_column', sa.String()))
```

### 9. Performance Considerations

**Large table migrations:**
```python
def upgrade():
    # For large tables, add column in batches
    op.add_column('render_jobs', sa.Column('priority', sa.Integer(), nullable=True))

    # Update in batches to avoid long-running transaction
    connection = op.get_bind()
    batch_size = 10000
    offset = 0

    while True:
        result = connection.execute(f"""
            UPDATE render_jobs
            SET priority = 5
            WHERE id IN (
                SELECT id FROM render_jobs
                WHERE priority IS NULL
                ORDER BY id
                LIMIT {batch_size}
                OFFSET {offset}
            )
        """)

        if result.rowcount == 0:
            break

        offset += batch_size
        print(f"Updated {offset} rows...")
```

**Index creation:**
```python
def upgrade():
    # Create index concurrently (doesn't lock table)
    op.execute("""
        CREATE INDEX CONCURRENTLY ix_render_jobs_status
        ON render_jobs (status)
    """)

def downgrade():
    op.drop_index('ix_render_jobs_status', table_name='render_jobs')
```

### 10. Migration Best Practices

**Checklist:**
```markdown
## Migration Best Practices

### Before Creating
- [ ] Review SQLAlchemy model changes
- [ ] Consider backward compatibility
- [ ] Plan multi-phase deployment if needed
- [ ] Test with realistic data volume

### Creating Migration
- [ ] Use descriptive migration message
- [ ] Review auto-generated SQL
- [ ] Add both upgrade() and downgrade()
- [ ] Include data migration if needed
- [ ] Add comments for complex logic

### Testing
- [ ] Test upgrade on dev database
- [ ] Test downgrade (rollback)
- [ ] Test with empty database
- [ ] Test with production-like data
- [ ] Check migration time for large tables

### Deployment
- [ ] Backup production database
- [ ] Run migration in maintenance window (if locking)
- [ ] Monitor for errors
- [ ] Verify schema after migration
- [ ] Test application functionality

### After Deployment
- [ ] Verify migration applied: `alembic current`
- [ ] Check database performance
- [ ] Monitor application errors
- [ ] Document any manual steps needed
```

### 11. Common Migration Patterns

**Add column with backfill:**
```python
def upgrade():
    # 1. Add nullable column
    op.add_column('render_jobs', sa.Column('estimated_duration', sa.Integer(), nullable=True))

    # 2. Backfill data
    op.execute("""
        UPDATE render_jobs
        SET estimated_duration = CAST(EXTRACT(EPOCH FROM (completed_at - created_at)) AS INTEGER)
        WHERE status = 'completed' AND estimated_duration IS NULL
    """)

    # 3. Set default for future rows
    op.alter_column('render_jobs', 'estimated_duration', server_default='0')
```

**Change column type:**
```python
def upgrade():
    # Change type with USING clause
    op.execute("""
        ALTER TABLE render_jobs
        ALTER COLUMN priority TYPE smallint
        USING priority::smallint
    """)
```

**Add enum type:**
```python
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create enum type
    status_enum = postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='job_status')
    status_enum.create(op.get_bind())

    # Add column with enum type
    op.add_column('render_jobs', sa.Column('status', status_enum, nullable=False, server_default='pending'))

def downgrade():
    op.drop_column('render_jobs', 'status')

    # Drop enum type
    status_enum = postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='job_status')
    status_enum.drop(op.get_bind())
```

### 12. Quick Reference

**Common commands:**
```bash
# Create migration
alembic revision --autogenerate -m "description"
alembic revision -m "manual migration"

# Apply migrations
alembic upgrade head         # Apply all
alembic upgrade +1           # Apply next one
alembic upgrade abc123       # Apply to specific

# Rollback
alembic downgrade -1         # Rollback one
alembic downgrade abc123     # Rollback to specific
alembic downgrade base       # Rollback all

# Status
alembic current              # Current revision
alembic history              # Show history
alembic show abc123          # Show specific migration

# Generate SQL
alembic upgrade head --sql   # Show SQL without applying
alembic downgrade -1 --sql   # Show rollback SQL

# Verify
alembic check                # Check for pending changes
```

## Output Format

When working with migrations, provide:
1. **Safety assessment**: Data loss risks and mitigation
2. **Migration plan**: Steps for zero-downtime if needed
3. **Test results**: Upgrade and downgrade verification
4. **Rollback procedure**: How to revert if issues arise
5. **Performance impact**: Expected duration and locking

Keep guidance focused on safe, production-ready database changes.
