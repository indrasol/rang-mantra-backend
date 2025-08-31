import uuid
import base64
from io import BytesIO
from typing import Tuple

from app.db.supabase_db import get_supabase_client, safe_supabase_operation
from fastapi import HTTPException

class StorageService:
    """
    Service for managing file storage in Supabase
    """
    
    BUCKET_ORIGINAL = "original-images"
    BUCKET_COLORIZED = "colorized-images"
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def ensure_buckets_exist(self):
        """
        Ensure that the required storage buckets exist
        """
        buckets_to_check = [self.BUCKET_ORIGINAL, self.BUCKET_COLORIZED]
        
        for bucket_name in buckets_to_check:
            await self._ensure_bucket_exists(bucket_name)
    
    async def _ensure_bucket_exists(self, bucket_name: str):
        """
        Check if a bucket exists, and create it if it doesn't
        """
        try:
            # Check if bucket exists
            def check_bucket():
                buckets = self.client.storage.list_buckets()
                return any(bucket.name == bucket_name for bucket in buckets)
            
            bucket_exists = await safe_supabase_operation(
                check_bucket,
                error_message=f"Failed to check if bucket {bucket_name} exists"
            )
            
            if not bucket_exists:
                # Create the bucket if it doesn't exist
                def create_bucket():
                    return self.client.storage.create_bucket(
                        bucket_name
                    )
                
                await safe_supabase_operation(
                    create_bucket,
                    error_message=f"Failed to create bucket {bucket_name}"
                )
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Storage bucket setup failed: {str(e)}")
    
    async def upload_original_image(self, user_id: str, file_content: bytes) -> str:
        """
        Upload an original black and white image to storage
        
        Args:
            user_id: The ID of the user
            file_content: The binary content of the file
            
        Returns:
            str: The path to the stored file
        """
        await self.ensure_buckets_exist()
        
        # Generate a unique filename for this user's upload
        filename = f"{user_id}/{uuid.uuid4()}.png"
        
        # Upload the file
        def upload_file():
            return self.client.storage.from_(self.BUCKET_ORIGINAL).upload(
                path=filename,
                file=file_content,
                file_options={"content-type": "image/png"}
            )
        
        await safe_supabase_operation(
            upload_file,
            error_message="Failed to upload original image"
        )
        
        return filename
    
    async def upload_colorized_image(self, user_id: str, file_content: bytes, original_filename: str) -> str:
        """
        Upload a colorized image to storage
        
        Args:
            user_id: The ID of the user
            file_content: The binary content of the file
            original_filename: The filename of the original image
            
        Returns:
            str: The path to the stored file
        """
        await self.ensure_buckets_exist()
        
        # Keep same filename structure as original but in colorized bucket
        filename = original_filename
        
        # Upload the file
        def upload_file():
            return self.client.storage.from_(self.BUCKET_COLORIZED).upload(
                path=filename,
                file=file_content,
                file_options={"content-type": "image/png"}
            )
        
        await safe_supabase_operation(
            upload_file,
            error_message="Failed to upload colorized image"
        )
        
        return filename
    
    async def get_public_url(self, bucket: str, path: str) -> str:
        """
        Get a public URL for a file
        
        Args:
            bucket: The name of the bucket
            path: The path to the file
            
        Returns:
            str: The public URL for the file
        """
        def get_url():
            return self.client.storage.from_(bucket).get_public_url(path)
        
        return await safe_supabase_operation(
            get_url,
            error_message="Failed to get public URL"
        )
    
    async def get_image_urls(self, original_path: str, colorized_path: str) -> Tuple[str, str]:
        """
        Get public URLs for both the original and colorized images
        
        Args:
            original_path: Path to the original image
            colorized_path: Path to the colorized image
            
        Returns:
            Tuple[str, str]: The public URLs for the original and colorized images
        """
        original_url = await self.get_public_url(self.BUCKET_ORIGINAL, original_path)
        colorized_url = await self.get_public_url(self.BUCKET_COLORIZED, colorized_path)
        
        return original_url, colorized_url
