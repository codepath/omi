import os
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any
from firebase_admin import auth
import database.notifications as notification_db
from utils.notifications import send_notification


class DatabaseBackup:
    """Handle database backup operations with notifications"""

    def __init__(self, database_name: str, project_id: str):
        """
        Initialize database backup handler

        Args:
            database_name: Name/identifier of the database being backed up
            project_id: Google Cloud project ID
        """
        self.database_name = database_name
        self.project_id = project_id
        self.backup_bucket = os.environ.get('BACKUP_BUCKET', f'{project_id}-backups')

    def perform_backup(self) -> Dict[str, Any]:
        """
        Perform Firestore database backup using gcloud command

        Returns:
            Dict containing backup status and metadata
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_path = f'gs://{self.backup_bucket}/firestore-backups/{self.database_name}/{timestamp}'

        try:
            print(f'Starting backup for database: {self.database_name}')

            # Use gcloud command to export Firestore database
            # This requires gcloud CLI to be installed and authenticated
            command = [
                'gcloud', 'firestore', 'export',
                backup_path,
                '--project', self.project_id,
                '--format', 'json'
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            if result.returncode == 0:
                print(f'Backup completed successfully for {self.database_name}')
                return {
                    'success': True,
                    'database_name': self.database_name,
                    'backup_path': backup_path,
                    'timestamp': timestamp,
                    'message': f'Database backup completed: {self.database_name}'
                }
            else:
                error_msg = result.stderr or 'Unknown error'
                print(f'Backup failed for {self.database_name}: {error_msg}')
                return {
                    'success': False,
                    'database_name': self.database_name,
                    'error': error_msg,
                    'message': f'Database backup failed: {self.database_name}'
                }

        except subprocess.TimeoutExpired:
            error_msg = 'Backup operation timed out after 1 hour'
            print(f'Backup timeout for {self.database_name}')
            return {
                'success': False,
                'database_name': self.database_name,
                'error': error_msg,
                'message': f'Database backup timed out: {self.database_name}'
            }
        except Exception as e:
            error_msg = str(e)
            print(f'Backup exception for {self.database_name}: {error_msg}')
            return {
                'success': False,
                'database_name': self.database_name,
                'error': error_msg,
                'message': f'Database backup error: {self.database_name}'
            }

    def send_backup_notification(self, backup_result: Dict[str, Any], admin_user_ids: list = None):
        """
        Send backup completion notification to admin users

        Args:
            backup_result: Result dictionary from perform_backup()
            admin_user_ids: List of admin user IDs to notify (optional)
        """
        if not admin_user_ids:
            # If no admin users specified, try to get from environment or skip
            admin_users_env = os.environ.get('BACKUP_ADMIN_USERS', '')
            admin_user_ids = [uid.strip() for uid in admin_users_env.split(',') if uid.strip()]

        if not admin_user_ids:
            print('No admin users configured for backup notifications')
            return

        # Prepare notification message
        database_name = backup_result['database_name']
        success = backup_result['success']

        if success:
            title = 'Database Backup Completed'
            body = f'Database backup completed: {database_name}'
            data = {
                'type': 'database_backup',
                'status': 'success',
                'database_name': database_name,
                'timestamp': backup_result.get('timestamp', ''),
                'backup_path': backup_result.get('backup_path', '')
            }
        else:
            title = 'Database Backup Failed'
            body = f'Database backup failed: {database_name}'
            data = {
                'type': 'database_backup',
                'status': 'failed',
                'database_name': database_name,
                'error': backup_result.get('error', 'Unknown error')
            }

        # Send notification to each admin user
        for user_id in admin_user_ids:
            try:
                token = notification_db.get_token_only(user_id)
                if token:
                    send_notification(token, title, body, data)
                    print(f'Backup notification sent to user {user_id} for database {database_name}')
                else:
                    print(f'No notification token found for admin user {user_id}')
            except Exception as e:
                print(f'Failed to send backup notification to user {user_id}: {e}')


def backup_database(database_name: str, project_id: str = None, admin_user_ids: list = None) -> Dict[str, Any]:
    """
    Convenience function to backup a database and send notification

    Args:
        database_name: Name/identifier of the database to backup
        project_id: Google Cloud project ID (defaults to environment variable)
        admin_user_ids: List of admin user IDs to notify (optional)

    Returns:
        Dict containing backup result
    """
    if not project_id:
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'omi-project')

    backup_handler = DatabaseBackup(database_name, project_id)
    result = backup_handler.perform_backup()

    # Send notification
    backup_handler.send_backup_notification(result, admin_user_ids)

    return result


def backup_multiple_databases(database_configs: list, admin_user_ids: list = None) -> list:
    """
    Backup multiple databases and send separate notifications for each

    Args:
        database_configs: List of dicts with 'name' and optionally 'project_id'
        admin_user_ids: List of admin user IDs to notify (optional)

    Returns:
        List of backup results
    """
    results = []

    for config in database_configs:
        database_name = config.get('name')
        project_id = config.get('project_id')

        if not database_name:
            print('Skipping database config without name')
            continue

        result = backup_database(database_name, project_id, admin_user_ids)
        results.append(result)

    return results
