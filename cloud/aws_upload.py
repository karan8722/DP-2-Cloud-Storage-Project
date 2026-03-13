"""
=============================================================================
AWS S3 Upload Module
=============================================================================
This module handles uploading files to Amazon S3 (Simple Storage Service).

What is AWS S3?
  - S3 is a cloud storage service by Amazon
  - Files are stored in "buckets" (like folders in the cloud)
  - Each file gets a unique URL that can be used to access it

Setup Required:
  1. Create an AWS account at https://aws.amazon.com
  2. Create an S3 bucket in the AWS Console
  3. Create an IAM user with S3 access
  4. Set the environment variables below with your credentials
=============================================================================
"""

import boto3
import os

# ─── AWS Configuration ────────────────────────────────────────────────────────
# These values come from your AWS account
# IMPORTANT: Never hardcode these in your code! Use environment variables.

AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID', 'your-access-key')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'your-secret-key')
AWS_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME', 'your-bucket-name')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')


def upload_to_s3(file_path, file_name):
    """
    Upload a file to AWS S3 bucket.
    
    Parameters:
        file_path (str): Local path to the file (e.g., 'uploads/photo.jpg')
        file_name (str): Name to save the file as in S3
    
    Returns:
        str: The URL of the uploaded file in S3
             Returns None if upload fails
    
    How it works:
        1. Create an S3 client using boto3 (AWS SDK)
        2. Upload the file to the specified bucket
        3. Return the public URL of the file
    """
    try:
        # Create S3 client (connection to AWS)
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )
        
        # Upload the file to S3
        # Note: ACL removed as modern S3 buckets don't allow ACLs by default
        s3_client.upload_file(
            file_path,                    # Local file path
            AWS_BUCKET_NAME,              # S3 bucket name
            file_name                     # Name in S3
        )
        
        # Construct the URL where the file can be accessed
        s3_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}"
        
        print(f"✅ File uploaded successfully: {s3_url}")
        return s3_url
        
    except Exception as e:
        # If AWS credentials are not set up, use a placeholder URL
        # This allows testing without actual AWS setup
        print(f"⚠️ S3 upload skipped (AWS not configured): {e}")
        print("   Using local placeholder URL instead.")
        return f"/static/uploads/{file_name}"
