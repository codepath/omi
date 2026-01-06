# Database Backup System

Automated database backup system with push notifications including database names.

## Features

- **Automated Firestore backups** using Google Cloud export
- **Multiple database support** - backup several databases with one configuration
- **Push notifications** - admin users receive notifications with database name
- **Separate notifications** - each database backup sends its own notification
- **Success/failure tracking** - notifications indicate backup status
- **Scheduled execution** - daily backups at configured time (default: 2 AM UTC)
- **Manual triggers** - run backups on-demand for testing or emergency

## Configuration

### Environment Variables

Add these to your `.env` file (see `backup_config.example.env`):

```bash
# Required
GOOGLE_CLOUD_PROJECT=your-project-id
BACKUP_ADMIN_USERS=user_id_1,user_id_2

# Optional
BACKUP_BUCKET=your-backup-bucket
BACKUP_DATABASES=production-db,staging-db,dev-db
BACKUP_SCHEDULE_HOUR=2
```

### Configuration Options

#### `GOOGLE_CLOUD_PROJECT` (required)
Your Google Cloud project ID where Firestore is hosted.

#### `BACKUP_ADMIN_USERS` (required)
Comma-separated list of user IDs who should receive backup notifications.
Users must have FCM tokens registered in the system.

#### `BACKUP_BUCKET` (optional)
Google Cloud Storage bucket for backups.
Default: `{project_id}-backups`

#### `BACKUP_DATABASES` (optional)
Databases to backup. Two formats supported:

**Simple (comma-separated):**
```bash
BACKUP_DATABASES=production-db,staging-db,dev-db
```

**Advanced (JSON with per-database project IDs):**
```bash
BACKUP_DATABASES=[{"name": "production-db", "project_id": "prod-project"}, {"name": "staging-db"}]
```

Default: Single database named `main-database`

#### `BACKUP_SCHEDULE_HOUR` (optional)
Hour (UTC, 0-23) when daily backup runs.
Default: `2` (2 AM UTC)

## Usage

### Automatic Scheduled Backups

Integrate with existing cron system in `utils/other/notifications.py`:

```python
from utils.other.backup_scheduler import start_backup_cron_job

async def start_cron_job():
    if should_run_job():
        print('start_cron_job')
        await send_daily_notification()
        await send_daily_summary_notification()
        await start_backup_cron_job()  # Add this line
```

### Manual Backup (All Databases)

```bash
cd backend
python -m utils.other.backup_scheduler
```

### Manual Backup (Specific Database)

```bash
cd backend
python -m utils.other.backup_scheduler production-db
```

With custom project ID:
```bash
python -m utils.other.backup_scheduler production-db my-project-id
```

### Programmatic Usage

```python
from utils.database_backup import backup_database, backup_multiple_databases

# Single database
result = backup_database('production-db', 'my-project-id', ['admin_user_1'])

# Multiple databases
databases = [
    {'name': 'production-db', 'project_id': 'prod-project'},
    {'name': 'staging-db', 'project_id': 'staging-project'}
]
results = backup_multiple_databases(databases, ['admin_user_1', 'admin_user_2'])
```

## Notification Format

### Success Notification
- **Title:** "Database Backup Completed"
- **Body:** "Database backup completed: production-db"
- **Data:**
  - `type`: "database_backup"
  - `status`: "success"
  - `database_name`: "production-db"
  - `timestamp`: "20250106_143022"
  - `backup_path`: "gs://bucket/path/to/backup"

### Failure Notification
- **Title:** "Database Backup Failed"
- **Body:** "Database backup failed: production-db"
- **Data:**
  - `type`: "database_backup"
  - `status`: "failed"
  - `database_name`: "production-db"
  - `error`: "Error message"

## Requirements

### Google Cloud Setup

1. **gcloud CLI** must be installed and authenticated
2. **Service account** must have permissions:
   - `datastore.databases.export`
   - `storage.buckets.create`
   - `storage.objects.create`
3. **Backup bucket** must exist or service account must have create permissions

### Install gcloud CLI

**macOS:**
```bash
brew install google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Authenticate:**
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

## Architecture

### File Structure
- `utils/database_backup.py` - Core backup and notification logic
- `utils/other/backup_scheduler.py` - Scheduling and cron integration
- `utils/other/backup_config.example.env` - Configuration template

### Flow
1. **Scheduler** checks if current time matches backup schedule
2. **Executor** loads database configs and admin user IDs
3. **Backup Handler** performs Firestore export for each database
4. **Notifier** sends push notification with database name
5. **Logger** records success/failure for monitoring

## Troubleshooting

### No notifications received
- Check `BACKUP_ADMIN_USERS` is set with valid user IDs
- Verify users have FCM tokens registered
- Check Firebase Cloud Messaging is configured

### Backup fails
- Ensure gcloud CLI is installed: `which gcloud`
- Verify authentication: `gcloud auth list`
- Check project ID: `gcloud config get-value project`
- Verify permissions: `gcloud projects get-iam-policy PROJECT_ID`

### Timeout errors
- Default timeout is 1 hour
- For large databases, run manual backup during low-traffic periods
- Consider increasing timeout in `database_backup.py` line 63

## Testing

Test the backup system without waiting for cron:

```python
import asyncio
from utils.other.backup_scheduler import manual_backup

# Test single database
asyncio.run(manual_backup('test-db'))

# Test all configured databases
asyncio.run(manual_backup())
```

## Issue Reference

This implementation addresses [Issue #5](https://github.com/your-repo/issues/5):
- ✅ Includes database name in notifications
- ✅ Supports multiple databases
- ✅ Sends separate notifications per database
- ✅ Clear identification of backed up database
- ✅ Better audit trail for backup operations
