"""
Storage Service - S3-compatible file storage
Handles file upload, download, deletion with encryption
"""

from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError
import structlog
import uuid
from datetime import datetime

from app.core.config import settings
from app.core.security import encrypt_data, decrypt_data

logger = structlog.get_logger(__name__)


class StorageService:
    """S3-compatible storage service"""
    
    def __init__(self):
        """Initialize S3 client"""
        self.s3_client = None
        
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
                endpoint_url=settings.S3_ENDPOINT_URL,
                use_ssl=settings.S3_USE_SSL
            )
        else:
            logger.warning("S3 credentials not configured - file storage will not work")
    
    async def upload_file(
        self,
        content: bytes,
        filename: str,
        content_type: Optional[str] = None,
        encrypt: bool = True
    ) -> Dict[str, Any]:
        """
        Upload file to S3
        
        Args:
            content: File content as bytes
            filename: Original filename
            content_type: MIME type
            encrypt: Whether to encrypt the file
        
        Returns:
            Dict with upload details (path, bucket, encrypted, etc.)
        """
        if not self.s3_client:
            raise Exception("S3 client not initialized - check AWS credentials")
        
        try:
            # Generate unique filename
            timestamp = datetime.utcnow().strftime("%Y%m%d")
            unique_id = str(uuid.uuid4())[:8]
            file_extension = filename.rsplit('.', 1)[-1] if '.' in filename else 'bin'
            storage_filename = f"{timestamp}/{unique_id}_{filename}"
            
            # Encrypt if requested
            upload_content = content
            encryption_key_id = None
            
            if encrypt:
                try:
                    # In production, use AWS KMS or similar
                    encrypted_str = encrypt_data(content.decode('latin-1'))
                    upload_content = encrypted_str.encode('latin-1')
                    encryption_key_id = "default-key"
                except Exception as e:
                    logger.warning("Encryption failed, uploading without encryption", error=str(e))
                    encrypt = False
            
            # Upload to S3
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=storage_filename,
                Body=upload_content,
                **extra_args
            )
            
            logger.info("File uploaded to S3", 
                       filename=filename, 
                       path=storage_filename,
                       encrypted=encrypt)
            
            return {
                "filename": filename,
                "path": storage_filename,
                "bucket": settings.S3_BUCKET_NAME,
                "encrypted": encrypt,
                "encryption_key_id": encryption_key_id
            }
            
        except ClientError as e:
            logger.error("S3 upload failed", error=str(e))
            raise Exception(f"Failed to upload file: {str(e)}")
    
    async def get_download_url(
        self,
        storage_path: str,
        bucket: Optional[str] = None,
        expires_in: int = 3600
    ) -> str:
        """
        Generate pre-signed download URL
        
        Args:
            storage_path: S3 object key
            bucket: Bucket name (default from settings)
            expires_in: URL expiration in seconds
        
        Returns:
            Pre-signed download URL
        """
        if not self.s3_client:
            raise Exception("S3 client not initialized")
        
        bucket = bucket or settings.S3_BUCKET_NAME
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket,
                    'Key': storage_path
                },
                ExpiresIn=expires_in
            )
            
            logger.info("Download URL generated", path=storage_path)
            
            return url
            
        except ClientError as e:
            logger.error("Failed to generate download URL", error=str(e))
            raise Exception(f"Failed to generate download URL: {str(e)}")
    
    async def delete_file(
        self,
        storage_path: str,
        bucket: Optional[str] = None
    ) -> bool:
        """
        Delete file from S3
        
        Args:
            storage_path: S3 object key
            bucket: Bucket name (default from settings)
        
        Returns:
            True if successful
        """
        if not self.s3_client:
            raise Exception("S3 client not initialized")
        
        bucket = bucket or settings.S3_BUCKET_NAME
        
        try:
            self.s3_client.delete_object(
                Bucket=bucket,
                Key=storage_path
            )
            
            logger.info("File deleted from S3", path=storage_path)
            
            return True
            
        except ClientError as e:
            logger.error("S3 delete failed", error=str(e))
            raise Exception(f"Failed to delete file: {str(e)}")
    
    async def download_file(
        self,
        storage_path: str,
        bucket: Optional[str] = None,
        decrypt: bool = False
    ) -> bytes:
        """
        Download file from S3
        
        Args:
            storage_path: S3 object key
            bucket: Bucket name (default from settings)
            decrypt: Whether to decrypt the file
        
        Returns:
            File content as bytes
        """
        if not self.s3_client:
            raise Exception("S3 client not initialized")
        
        bucket = bucket or settings.S3_BUCKET_NAME
        
        try:
            response = self.s3_client.get_object(
                Bucket=bucket,
                Key=storage_path
            )
            
            content = response['Body'].read()
            
            # Decrypt if requested
            if decrypt:
                try:
                    decrypted_str = decrypt_data(content.decode('latin-1'))
                    content = decrypted_str.encode('latin-1')
                except Exception as e:
                    logger.warning("Decryption failed", error=str(e))
            
            logger.info("File downloaded from S3", path=storage_path)
            
            return content
            
        except ClientError as e:
            logger.error("S3 download failed", error=str(e))
            raise Exception(f"Failed to download file: {str(e)}")
