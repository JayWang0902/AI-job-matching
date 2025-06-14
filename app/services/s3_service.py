import os
import boto3
import uuid
from typing import Dict, Optional
from botocore.client import Config
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class S3Service:
    """S3文件存储服务"""
    
    def __init__(self):
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.s3_bucket = os.getenv('S3_BUCKET_NAME', 'ai-job-matching-resumes')
        
        # 初始化S3客户端
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region,
            config=Config(signature_version='s3v4')
        )
    
    def generate_presigned_upload_url(
        self, 
        s3_key: str, 
        content_type: str = 'application/pdf',
        expires_in: int = 3600
    ) -> Dict:
        """生成预签名上传URL和表单字段"""
        try:
            # 生成预签名POST表单
            response = self.s3_client.generate_presigned_post(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Fields={
                    'Content-Type': content_type,
                    'x-amz-meta-upload-type': 'resume'
                },
                Conditions=[
                    {'Content-Type': content_type},
                    ['content-length-range', 1, 10 * 1024 * 1024],  # 1B到10MB
                    {'x-amz-meta-upload-type': 'resume'}
                ],
                ExpiresIn=expires_in
            )
            
            return {
                'upload_url': response['url'],
                'upload_fields': response['fields'],
                'expires_in': expires_in
            }
            
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise Exception(f"无法生成上传URL: {str(e)}")
    
    def generate_s3_key(self, user_id: int, original_filename: str) -> str:
        """生成S3对象键"""
        file_ext = original_filename.split('.')[-1] if '.' in original_filename else 'pdf'
        unique_id = str(uuid.uuid4())
        return f"resumes/user_{user_id}/{unique_id}.{file_ext}"
    
    def check_file_exists(self, s3_key: str) -> bool:
        """检查文件是否存在"""
        try:
            self.s3_client.head_object(Bucket=self.s3_bucket, Key=s3_key)
            return True
        except ClientError:
            return False
    
    def get_file_size(self, s3_key: str) -> Optional[int]:
        """获取文件大小"""
        try:
            response = self.s3_client.head_object(Bucket=self.s3_bucket, Key=s3_key)
            return response['ContentLength']
        except ClientError:
            return None
    
    def generate_download_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """生成预签名下载URL"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.s3_bucket, 'Key': s3_key},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating download URL: {e}")
            raise Exception(f"无法生成下载URL: {str(e)}")
    
    def delete_file(self, s3_key: str) -> bool:
        """删除S3文件"""
        try:
            self.s3_client.delete_object(Bucket=self.s3_bucket, Key=s3_key)
            return True
        except ClientError as e:
            logger.error(f"Error deleting file: {e}")
            return False

# 全局S3服务实例
s3_service = S3Service()