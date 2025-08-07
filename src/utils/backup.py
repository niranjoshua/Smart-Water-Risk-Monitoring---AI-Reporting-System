import boto3
import os
import shutil
from datetime import datetime
import logging
from botocore.exceptions import ClientError

class BackupManager:
    def __init__(self, bucket_name: str = None):
        self.bucket_name = bucket_name or os.getenv('BACKUP_BUCKET_NAME')
        self.s3_client = boto3.client('s3')
        self.logger = logging.getLogger(__name__)

    def create_local_backup(self, db_path: str) -> str:
        """Create a local backup of the database"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"backups/water_monitoring_{timestamp}.db"
        
        # Ensure backup directory exists
        os.makedirs('backups', exist_ok=True)
        
        # Copy database file
        shutil.copy2(db_path, backup_path)
        self.logger.info(f"Local backup created: {backup_path}")
        return backup_path

    def upload_to_s3(self, file_path: str) -> bool:
        """Upload backup to S3"""
        try:
            file_name = os.path.basename(file_path)
            self.s3_client.upload_file(file_path, self.bucket_name, file_name)
            self.logger.info(f"Backup uploaded to S3: {file_name}")
            return True
        except ClientError as e:
            self.logger.error(f"Error uploading to S3: {str(e)}")
            return False

    def clean_old_backups(self, retention_days: int = 30):
        """Clean up old backup files"""
        try:
            # Clean local backups
            cutoff_date = datetime.now().timestamp() - (retention_days * 86400)
            backup_dir = "backups"
            
            for backup_file in os.listdir(backup_dir):
                file_path = os.path.join(backup_dir, backup_file)
                if os.path.getctime(file_path) < cutoff_date:
                    os.remove(file_path)
                    self.logger.info(f"Removed old backup: {file_path}")

            # Clean S3 backups
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['LastModified'].timestamp() < cutoff_date:
                        self.s3_client.delete_object(
                            Bucket=self.bucket_name,
                            Key=obj['Key']
                        )
                        self.logger.info(f"Removed old S3 backup: {obj['Key']}")
                        
        except Exception as e:
            self.logger.error(f"Error cleaning old backups: {str(e)}")

    def perform_backup(self, db_path: str):
        """Perform complete backup process"""
        try:
            # Create local backup
            backup_path = self.create_local_backup(db_path)
            
            # Upload to S3
            if self.upload_to_s3(backup_path):
                self.logger.info("Backup process completed successfully")
            else:
                self.logger.error("Failed to upload backup to S3")
                
            # Clean old backups
            self.clean_old_backups()
            
        except Exception as e:
            self.logger.error(f"Backup process failed: {str(e)}")
            raise
