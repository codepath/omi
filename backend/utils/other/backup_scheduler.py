import asyncio
import os
from datetime import datetime
from typing import List, Dict
import pytz

from utils.database_backup import backup_multiple_databases


async def start_backup_cron_job():
    """
    Start backup cron job if current time matches backup schedule
    Runs daily at configured time (default: 02:00 UTC)
    """
    if should_run_backup_job():
        print('Starting scheduled database backup job')
        await execute_database_backups()


def should_run_backup_job() -> bool:
    """
    Check if backup job should run based on current time
    Runs at 02:00 UTC (or configured time) daily

    Returns:
        True if job should run, False otherwise
    """
    current_utc = datetime.now(pytz.utc)

    # Get backup hour from environment (default: 2 AM UTC)
    backup_hour = int(os.environ.get('BACKUP_SCHEDULE_HOUR', '2'))

    # Run at the top of the hour
    if current_utc.hour == backup_hour and current_utc.minute == 0:
        return True

    return False


def get_database_configs() -> List[Dict[str, str]]:
    """
    Get database configurations from environment variables

    Environment variable format:
    BACKUP_DATABASES='production-db,staging-db,dev-db'
    or
    BACKUP_DATABASES='[{"name": "production-db", "project_id": "prod-project"}, {"name": "staging-db"}]'

    Returns:
        List of database configuration dictionaries
    """
    databases_env = os.environ.get('BACKUP_DATABASES', '')

    if not databases_env:
        # Default to single main database
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'omi-project')
        return [{'name': 'main-database', 'project_id': project_id}]

    # Try to parse as JSON first
    try:
        import json
        configs = json.loads(databases_env)
        if isinstance(configs, list):
            return configs
    except (json.JSONDecodeError, ValueError):
        pass

    # Parse as comma-separated list
    database_names = [name.strip() for name in databases_env.split(',') if name.strip()]
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'omi-project')

    return [{'name': name, 'project_id': project_id} for name in database_names]


def get_admin_user_ids() -> List[str]:
    """
    Get admin user IDs who should receive backup notifications

    Environment variable format:
    BACKUP_ADMIN_USERS='user1_id,user2_id,user3_id'

    Returns:
        List of admin user IDs
    """
    admin_users_env = os.environ.get('BACKUP_ADMIN_USERS', '')

    if not admin_users_env:
        print('Warning: No BACKUP_ADMIN_USERS configured. Backup notifications will not be sent.')
        return []

    return [uid.strip() for uid in admin_users_env.split(',') if uid.strip()]


async def execute_database_backups():
    """
    Execute backups for all configured databases
    Sends separate notification for each database with its name
    """
    try:
        # Get database configurations
        database_configs = get_database_configs()
        admin_user_ids = get_admin_user_ids()

        if not database_configs:
            print('No databases configured for backup')
            return

        print(f'Starting backup for {len(database_configs)} database(s)')

        # Perform backups (this will send individual notifications for each database)
        results = await asyncio.to_thread(
            backup_multiple_databases,
            database_configs,
            admin_user_ids
        )

        # Log results
        successful = sum(1 for r in results if r.get('success'))
        failed = len(results) - successful

        print(f'Backup job completed: {successful} successful, {failed} failed')

        for result in results:
            db_name = result.get('database_name', 'unknown')
            if result.get('success'):
                print(f'  ✓ {db_name}: {result.get("backup_path")}')
            else:
                print(f'  ✗ {db_name}: {result.get("error", "Unknown error")}')

    except Exception as e:
        print(f'Error executing database backups: {e}')


async def manual_backup(database_name: str = None, project_id: str = None):
    """
    Manually trigger a database backup (useful for testing or on-demand backups)

    Args:
        database_name: Optional specific database name to backup
        project_id: Optional project ID override
    """
    from utils.database_backup import backup_database

    admin_user_ids = get_admin_user_ids()

    if database_name:
        # Backup specific database
        print(f'Manually triggering backup for: {database_name}')
        result = await asyncio.to_thread(
            backup_database,
            database_name,
            project_id,
            admin_user_ids
        )
        return result
    else:
        # Backup all configured databases
        print('Manually triggering backup for all configured databases')
        await execute_database_backups()


# Example standalone script usage
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        # Manual backup with database name
        db_name = sys.argv[1]
        project = sys.argv[2] if len(sys.argv) > 2 else None
        asyncio.run(manual_backup(db_name, project))
    else:
        # Run all configured backups
        asyncio.run(execute_database_backups())
