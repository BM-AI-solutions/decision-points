"""
Data backup and recovery system for production deployment.

This module provides:
1. Automated database backups
2. File system backups
3. Backup encryption
4. Backup rotation and retention policies
5. Backup verification
6. Disaster recovery procedures
"""

import os
import sys
import time
import json
import shutil
import tarfile
import zipfile
import hashlib
import subprocess
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Callable, Union
import logging
import boto3
from botocore.exceptions import ClientError
import google.cloud.storage
from google.oauth2 import service_account

from utils.logger import setup_logger
from utils.security_enhancements import encrypt_data, decrypt_data

# Set up module logger
logger = setup_logger('utils.backup')

# ===== Backup Configuration =====

class BackupConfig:
    """Backup configuration settings."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize backup configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Set default values
        self.backup_dir = self.config.get('backup_dir', './backups')
        self.retention_days = self.config.get('retention_days', 30)
        self.backup_frequency = self.config.get('backup_frequency', 'daily')
        self.encrypt_backups = self.config.get('encrypt_backups', True)
        self.compression_type = self.config.get('compression_type', 'gzip')
        self.cloud_storage = self.config.get('cloud_storage', {})
        self.notification_email = self.config.get('notification_email')
        self.backup_types = self.config.get('backup_types', ['database', 'files'])
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables.
        
        Returns:
            BackupConfig instance
        """
        config = {
            'backup_dir': os.environ.get('BACKUP_DIR', './backups'),
            'retention_days': int(os.environ.get('BACKUP_RETENTION_DAYS', 30)),
            'backup_frequency': os.environ.get('BACKUP_FREQUENCY', 'daily'),
            'encrypt_backups': os.environ.get('ENCRYPT_BACKUPS', 'true').lower() == 'true',
            'compression_type': os.environ.get('BACKUP_COMPRESSION', 'gzip'),
            'notification_email': os.environ.get('BACKUP_NOTIFICATION_EMAIL'),
            'backup_types': os.environ.get('BACKUP_TYPES', 'database,files').split(','),
            'cloud_storage': {
                'provider': os.environ.get('BACKUP_CLOUD_PROVIDER'),
                'bucket': os.environ.get('BACKUP_CLOUD_BUCKET'),
                'prefix': os.environ.get('BACKUP_CLOUD_PREFIX', 'backups/')
            }
        }
        
        return cls(config)

# ===== Backup Utilities =====

def generate_backup_filename(prefix: str, extension: str = 'tar.gz') -> str:
    """Generate a backup filename with timestamp.
    
    Args:
        prefix: Filename prefix
        extension: File extension
        
    Returns:
        Backup filename
    """
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.{extension}"

def calculate_file_hash(filepath: str, algorithm: str = 'sha256') -> str:
    """Calculate file hash for verification.
    
    Args:
        filepath: Path to file
        algorithm: Hash algorithm
        
    Returns:
        File hash
    """
    hash_func = getattr(hashlib, algorithm)()
    
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()

def create_manifest(backup_path: str, files: List[str], metadata: Dict[str, Any]) -> str:
    """Create a backup manifest file.
    
    Args:
        backup_path: Path to backup directory
        files: List of files in backup
        metadata: Backup metadata
        
    Returns:
        Path to manifest file
    """
    manifest = {
        'backup_id': metadata.get('backup_id'),
        'timestamp': metadata.get('timestamp'),
        'backup_type': metadata.get('backup_type'),
        'files': []
    }
    
    # Add file information
    for file_path in files:
        file_info = {
            'path': file_path,
            'size': os.path.getsize(file_path),
            'hash': calculate_file_hash(file_path)
        }
        manifest['files'].append(file_info)
    
    # Add additional metadata
    for key, value in metadata.items():
        if key not in manifest:
            manifest[key] = value
    
    # Write manifest file
    manifest_path = os.path.join(backup_path, 'manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return manifest_path

# ===== Database Backup =====

def backup_postgres_db(config: BackupConfig, db_config: Dict[str, Any]) -> str:
    """Backup PostgreSQL database.
    
    Args:
        config: Backup configuration
        db_config: Database configuration
        
    Returns:
        Path to backup file
    """
    db_name = db_config.get('name')
    db_user = db_config.get('user')
    db_host = db_config.get('host', 'localhost')
    db_port = db_config.get('port', 5432)
    
    # Generate backup filename
    backup_filename = generate_backup_filename(f"postgres_{db_name}", "sql.gz")
    backup_path = os.path.join(config.backup_dir, backup_filename)
    
    # Set environment variables for pg_dump
    env = os.environ.copy()
    if 'password' in db_config:
        env['PGPASSWORD'] = db_config['password']
    
    try:
        # Execute pg_dump command
        cmd = [
            'pg_dump',
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '-d', db_name,
            '-F', 'c',  # Custom format
            '-Z', '9',  # Maximum compression
            '-f', backup_path
        ]
        
        subprocess.run(cmd, env=env, check=True, capture_output=True)
        
        logger.info(f"PostgreSQL backup created: {backup_path}")
        return backup_path
    
    except subprocess.CalledProcessError as e:
        logger.error(f"PostgreSQL backup failed: {e.stderr.decode()}")
        raise RuntimeError(f"Database backup failed: {e.stderr.decode()}")

def backup_mysql_db(config: BackupConfig, db_config: Dict[str, Any]) -> str:
    """Backup MySQL database.
    
    Args:
        config: Backup configuration
        db_config: Database configuration
        
    Returns:
        Path to backup file
    """
    db_name = db_config.get('name')
    db_user = db_config.get('user')
    db_host = db_config.get('host', 'localhost')
    db_port = db_config.get('port', 3306)
    
    # Generate backup filename
    backup_filename = generate_backup_filename(f"mysql_{db_name}", "sql.gz")
    backup_path = os.path.join(config.backup_dir, backup_filename)
    
    try:
        # Execute mysqldump command
        cmd = [
            'mysqldump',
            '-h', db_host,
            '-P', str(db_port),
            '-u', db_user,
            db_name
        ]
        
        if 'password' in db_config:
            cmd.extend(['-p' + db_config['password']])
        
        with open(backup_path, 'wb') as f:
            mysqldump = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            gzip_cmd = subprocess.Popen(['gzip'], stdin=mysqldump.stdout, stdout=f)
            mysqldump.stdout.close()
            gzip_cmd.communicate()
        
        logger.info(f"MySQL backup created: {backup_path}")
        return backup_path
    
    except subprocess.CalledProcessError as e:
        logger.error(f"MySQL backup failed: {str(e)}")
        raise RuntimeError(f"Database backup failed: {str(e)}")

def backup_mongodb(config: BackupConfig, db_config: Dict[str, Any]) -> str:
    """Backup MongoDB database.
    
    Args:
        config: Backup configuration
        db_config: Database configuration
        
    Returns:
        Path to backup file
    """
    db_name = db_config.get('name')
    db_host = db_config.get('host', 'localhost')
    db_port = db_config.get('port', 27017)
    
    # Generate backup directory
    backup_dir = os.path.join(config.backup_dir, f"mongodb_{db_name}_{int(time.time())}")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename
    backup_filename = generate_backup_filename(f"mongodb_{db_name}", "archive.gz")
    backup_path = os.path.join(config.backup_dir, backup_filename)
    
    try:
        # Execute mongodump command
        cmd = [
            'mongodump',
            '--host', db_host,
            '--port', str(db_port),
            '--db', db_name,
            '--gzip',
            '--archive=' + backup_path
        ]
        
        if 'user' in db_config and 'password' in db_config:
            cmd.extend([
                '--username', db_config['user'],
                '--password', db_config['password'],
                '--authenticationDatabase', db_config.get('auth_db', 'admin')
            ])
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        logger.info(f"MongoDB backup created: {backup_path}")
        return backup_path
    
    except subprocess.CalledProcessError as e:
        logger.error(f"MongoDB backup failed: {e.stderr.decode()}")
        raise RuntimeError(f"Database backup failed: {e.stderr.decode()}")

def backup_database(config: BackupConfig, db_config: Dict[str, Any]) -> str:
    """Backup database based on type.
    
    Args:
        config: Backup configuration
        db_config: Database configuration
        
    Returns:
        Path to backup file
    """
    db_type = db_config.get('type', '').lower()
    
    if db_type == 'postgres' or db_type == 'postgresql':
        return backup_postgres_db(config, db_config)
    elif db_type == 'mysql' or db_type == 'mariadb':
        return backup_mysql_db(config, db_config)
    elif db_type == 'mongodb':
        return backup_mongodb(config, db_config)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

# ===== File System Backup =====

def backup_files(config: BackupConfig, paths: List[str], exclude_patterns: Optional[List[str]] = None) -> str:
    """Backup files and directories.
    
    Args:
        config: Backup configuration
        paths: List of paths to backup
        exclude_patterns: Patterns to exclude
        
    Returns:
        Path to backup file
    """
    # Generate backup filename
    backup_filename = generate_backup_filename("files", "tar.gz")
    backup_path = os.path.join(config.backup_dir, backup_filename)
    
    # Default exclude patterns
    exclude_patterns = exclude_patterns or [
        '*.pyc', '__pycache__', '*.log', '*.tmp', '*.bak',
        '.git', '.svn', 'node_modules', 'venv', 'env'
    ]
    
    try:
        with tarfile.open(backup_path, 'w:gz') as tar:
            for path in paths:
                if os.path.isdir(path):
                    # Backup directory
                    for root, dirs, files in os.walk(path):
                        # Apply exclude patterns to directories
                        dirs[:] = [d for d in dirs if not any(
                            d == pattern or d.endswith(pattern.strip('*'))
                            for pattern in exclude_patterns
                        )]
                        
                        # Add files to archive
                        for file in files:
                            file_path = os.path.join(root, file)
                            
                            # Skip excluded files
                            if any(file.endswith(pattern.strip('*')) for pattern in exclude_patterns):
                                continue
                            
                            # Add file to archive
                            arcname = os.path.relpath(file_path, os.path.dirname(path))
                            tar.add(file_path, arcname=arcname)
                else:
                    # Backup single file
                    if os.path.exists(path):
                        arcname = os.path.basename(path)
                        tar.add(path, arcname=arcname)
        
        logger.info(f"File backup created: {backup_path}")
        return backup_path
    
    except Exception as e:
        logger.error(f"File backup failed: {str(e)}")
        raise RuntimeError(f"File backup failed: {str(e)}")

# ===== Backup Encryption =====

def encrypt_backup(backup_path: str, output_path: Optional[str] = None) -> str:
    """Encrypt a backup file.
    
    Args:
        backup_path: Path to backup file
        output_path: Path for encrypted output (default: backup_path + .enc)
        
    Returns:
        Path to encrypted backup
    """
    if output_path is None:
        output_path = backup_path + '.enc'
    
    try:
        with open(backup_path, 'rb') as f:
            backup_data = f.read()
        
        # Encrypt the backup data
        encrypted_data = encrypt_data(backup_data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted_data.encode())
        
        logger.info(f"Backup encrypted: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Backup encryption failed: {str(e)}")
        raise RuntimeError(f"Backup encryption failed: {str(e)}")

def decrypt_backup(encrypted_path: str, output_path: Optional[str] = None) -> str:
    """Decrypt an encrypted backup file.
    
    Args:
        encrypted_path: Path to encrypted backup
        output_path: Path for decrypted output (default: remove .enc extension)
        
    Returns:
        Path to decrypted backup
    """
    if output_path is None:
        output_path = encrypted_path.replace('.enc', '')
    
    try:
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read().decode()
        
        # Decrypt the backup data
        decrypted_data = decrypt_data(encrypted_data)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        
        logger.info(f"Backup decrypted: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Backup decryption failed: {str(e)}")
        raise RuntimeError(f"Backup decryption failed: {str(e)}")

# ===== Cloud Storage =====

def upload_to_s3(file_path: str, bucket: str, key_prefix: str) -> str:
    """Upload backup to Amazon S3.
    
    Args:
        file_path: Path to backup file
        bucket: S3 bucket name
        key_prefix: S3 key prefix
        
    Returns:
        S3 object URL
    """
    try:
        s3_client = boto3.client('s3')
        
        # Generate S3 key
        filename = os.path.basename(file_path)
        s3_key = f"{key_prefix.rstrip('/')}/{filename}"
        
        # Upload file
        s3_client.upload_file(file_path, bucket, s3_key)
        
        # Generate URL
        url = f"s3://{bucket}/{s3_key}"
        
        logger.info(f"Backup uploaded to S3: {url}")
        return url
    
    except ClientError as e:
        logger.error(f"S3 upload failed: {str(e)}")
        raise RuntimeError(f"S3 upload failed: {str(e)}")

def upload_to_gcs(file_path: str, bucket: str, key_prefix: str) -> str:
    """Upload backup to Google Cloud Storage.
    
    Args:
        file_path: Path to backup file
        bucket: GCS bucket name
        key_prefix: GCS key prefix
        
    Returns:
        GCS object URL
    """
    try:
        # Initialize GCS client
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            storage_client = google.cloud.storage.Client(credentials=credentials)
        else:
            storage_client = google.cloud.storage.Client()
        
        # Get bucket
        bucket_obj = storage_client.bucket(bucket)
        
        # Generate GCS key
        filename = os.path.basename(file_path)
        gcs_key = f"{key_prefix.rstrip('/')}/{filename}"
        
        # Upload file
        blob = bucket_obj.blob(gcs_key)
        blob.upload_from_filename(file_path)
        
        # Generate URL
        url = f"gs://{bucket}/{gcs_key}"
        
        logger.info(f"Backup uploaded to GCS: {url}")
        return url
    
    except Exception as e:
        logger.error(f"GCS upload failed: {str(e)}")
        raise RuntimeError(f"GCS upload failed: {str(e)}")

def upload_backup_to_cloud(config: BackupConfig, file_path: str) -> Optional[str]:
    """Upload backup to configured cloud storage.
    
    Args:
        config: Backup configuration
        file_path: Path to backup file
        
    Returns:
        Cloud storage URL or None if not configured
    """
    cloud_config = config.cloud_storage
    provider = cloud_config.get('provider', '').lower()
    
    if not provider:
        return None
    
    bucket = cloud_config.get('bucket')
    prefix = cloud_config.get('prefix', 'backups/')
    
    if not bucket:
        logger.warning("Cloud storage bucket not configured")
        return None
    
    if provider == 'aws' or provider == 's3':
        return upload_to_s3(file_path, bucket, prefix)
    elif provider == 'gcp' or provider == 'gcs':
        return upload_to_gcs(file_path, bucket, prefix)
    else:
        logger.warning(f"Unsupported cloud provider: {provider}")
        return None

# ===== Backup Rotation =====

def cleanup_old_backups(config: BackupConfig) -> int:
    """Delete backups older than retention period.
    
    Args:
        config: Backup configuration
        
    Returns:
        Number of backups deleted
    """
    retention_days = config.retention_days
    backup_dir = config.backup_dir
    
    if retention_days <= 0:
        logger.info("Backup retention disabled, skipping cleanup")
        return 0
    
    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
    deleted_count = 0
    
    try:
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            
            # Skip directories and non-backup files
            if os.path.isdir(file_path) or not any(
                filename.endswith(ext) for ext in ['.tar.gz', '.sql.gz', '.zip', '.enc']
            ):
                continue
            
            # Get file modification time
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            # Delete if older than retention period
            if file_time < cutoff_date:
                os.remove(file_path)
                deleted_count += 1
                logger.info(f"Deleted old backup: {filename}")
        
        return deleted_count
    
    except Exception as e:
        logger.error(f"Backup cleanup failed: {str(e)}")
        return 0

# ===== Backup Verification =====

def verify_backup(backup_path: str, manifest_path: Optional[str] = None) -> bool:
    """Verify backup integrity.
    
    Args:
        backup_path: Path to backup file
        manifest_path: Path to manifest file
        
    Returns:
        True if backup is valid
    """
    try:
        # Check if backup file exists
        if not os.path.exists(backup_path):
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        # Verify file size
        file_size = os.path.getsize(backup_path)
        if file_size == 0:
            logger.error(f"Backup file is empty: {backup_path}")
            return False
        
        # If manifest provided, verify against it
        if manifest_path and os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Find backup file in manifest
            for file_info in manifest.get('files', []):
                if os.path.basename(file_info.get('path')) == os.path.basename(backup_path):
                    # Verify file size
                    if file_info.get('size') != file_size:
                        logger.error(f"Backup size mismatch: {backup_path}")
                        return False
                    
                    # Verify file hash
                    expected_hash = file_info.get('hash')
                    actual_hash = calculate_file_hash(backup_path)
                    
                    if expected_hash != actual_hash:
                        logger.error(f"Backup hash mismatch: {backup_path}")
                        return False
                    
                    break
        
        # For archive files, check if they can be opened
        if backup_path.endswith('.tar.gz'):
            with tarfile.open(backup_path, 'r:gz') as tar:
                # Check if archive can be read
                tar.getmembers()
        elif backup_path.endswith('.zip'):
            with zipfile.ZipFile(backup_path, 'r') as zip_file:
                # Check if archive can be read
                zip_file.testzip()
        
        logger.info(f"Backup verified: {backup_path}")
        return True
    
    except Exception as e:
        logger.error(f"Backup verification failed: {str(e)}")
        return False

# ===== Main Backup Functions =====

def create_backup(config: Optional[BackupConfig] = None, 
                 backup_type: Optional[str] = None,
                 db_config: Optional[Dict[str, Any]] = None,
                 file_paths: Optional[List[str]] = None) -> Dict[str, Any]:
    """Create a backup.
    
    Args:
        config: Backup configuration
        backup_type: Type of backup (database, files, all)
        db_config: Database configuration
        file_paths: Paths to backup
        
    Returns:
        Backup information
    """
    # Use default config if not provided
    if config is None:
        config = BackupConfig.from_env()
    
    # Default to all backup types if not specified
    if backup_type is None:
        backup_type = 'all'
    
    backup_id = str(int(time.time()))
    timestamp = datetime.utcnow().isoformat()
    backup_files = []
    
    try:
        # Create temporary directory for backup files
        temp_dir = os.path.join(config.backup_dir, f"backup_{backup_id}")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Backup database if requested
        if backup_type in ['database', 'all'] and db_config:
            db_backup_path = backup_database(config, db_config)
            backup_files.append(db_backup_path)
        
        # Backup files if requested
        if backup_type in ['files', 'all'] and file_paths:
            file_backup_path = backup_files(config, file_paths)
            backup_files.append(file_backup_path)
        
        # Create backup manifest
        metadata = {
            'backup_id': backup_id,
            'timestamp': timestamp,
            'backup_type': backup_type,
            'config': {
                'retention_days': config.retention_days,
                'encrypt_backups': config.encrypt_backups
            }
        }
        
        manifest_path = create_manifest(temp_dir, backup_files, metadata)
        backup_files.append(manifest_path)
        
        # Encrypt backups if configured
        if config.encrypt_backups:
            encrypted_files = []
            for file_path in backup_files:
                encrypted_path = encrypt_backup(file_path)
                encrypted_files.append(encrypted_path)
            
            backup_files = encrypted_files
        
        # Upload to cloud storage if configured
        cloud_urls = []
        for file_path in backup_files:
            cloud_url = upload_backup_to_cloud(config, file_path)
            if cloud_url:
                cloud_urls.append(cloud_url)
        
        # Clean up old backups
        deleted_count = cleanup_old_backups(config)
        
        # Return backup information
        backup_info = {
            'backup_id': backup_id,
            'timestamp': timestamp,
            'backup_type': backup_type,
            'files': backup_files,
            'cloud_urls': cloud_urls,
            'encrypted': config.encrypt_backups,
            'cleanup': {
                'deleted_count': deleted_count
            }
        }
        
        logger.info(f"Backup completed: {backup_id}")
        return backup_info
    
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        raise RuntimeError(f"Backup failed: {str(e)}")

def restore_backup(backup_path: str, restore_dir: Optional[str] = None,
                  db_config: Optional[Dict[str, Any]] = None,
                  encrypted: bool = False) -> Dict[str, Any]:
    """Restore from backup.
    
    Args:
        backup_path: Path to backup file
        restore_dir: Directory to restore files to
        db_config: Database configuration for database restore
        encrypted: Whether backup is encrypted
        
    Returns:
        Restore information
    """
    # Generate restore ID
    restore_id = str(int(time.time()))
    timestamp = datetime.utcnow().isoformat()
    
    # Set default restore directory
    if restore_dir is None:
        restore_dir = f"./restore_{restore_id}"
    
    os.makedirs(restore_dir, exist_ok=True)
    
    try:
        # Decrypt backup if encrypted
        if encrypted:
            backup_path = decrypt_backup(backup_path)
        
        # Determine backup type from filename
        is_database = any(backup_path.endswith(ext) for ext in ['.sql', '.sql.gz', '.dump', '.archive.gz'])
        is_files = any(backup_path.endswith(ext) for ext in ['.tar.gz', '.zip'])
        
        restored_paths = []
        
        # Restore database backup
        if is_database and db_config:
            # Implementation depends on database type
            # For PostgreSQL:
            if db_config.get('type') == 'postgres':
                cmd = [
                    'pg_restore',
                    '-h', db_config.get('host', 'localhost'),
                    '-p', str(db_config.get('port', 5432)),
                    '-U', db_config.get('user'),
                    '-d', db_config.get('name'),
                    '-c',  # Clean (drop) before restore
                    backup_path
                ]
                
                env = os.environ.copy()
                if 'password' in db_config:
                    env['PGPASSWORD'] = db_config['password']
                
                subprocess.run(cmd, env=env, check=True)
                restored_paths.append(f"Database: {db_config.get('name')}")
        
        # Restore file backup
        if is_files:
            if backup_path.endswith('.tar.gz'):
                with tarfile.open(backup_path, 'r:gz') as tar:
                    tar.extractall(path=restore_dir)
            elif backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zip_file:
                    zip_file.extractall(path=restore_dir)
            
            restored_paths.append(restore_dir)
        
        # Return restore information
        restore_info = {
            'restore_id': restore_id,
            'timestamp': timestamp,
            'backup_path': backup_path,
            'restore_dir': restore_dir,
            'restored_paths': restored_paths
        }
        
        logger.info(f"Restore completed: {restore_id}")
        return restore_info
    
    except Exception as e:
        logger.error(f"Restore failed: {str(e)}")
        raise RuntimeError(f"Restore failed: {str(e)}")