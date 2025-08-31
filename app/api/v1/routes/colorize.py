from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, Header
from fastapi.responses import JSONResponse
import uuid
import asyncio
from datetime import datetime
from typing import Optional
import json

from app.core.google_ai_client import ImageColorizer
from app.services.storage_service import StorageService
from app.models.colorize import ColorizeRequest, ColorizeResponse, ColorizeStatus
from app.db.supabase_db import get_supabase_client, safe_supabase_operation

router = APIRouter()
colorizer = ImageColorizer()
storage_service = StorageService()

@router.post("/upload", response_model=ColorizeResponse)
async def upload_image(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    user_email: Optional[str] = Form(None),
    authorization: Optional[str] = Header(None)
):
    """
    Upload a black and white image and start the colorization process
    
    Args:
        file: The black and white image file
        user_id: The ID of the user
        user_email: Optional email of the user for organization
        authorization: JWT token for authentication
    """
    # Validate that the file is an image
    content_type = file.content_type
    if not content_type or not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Create a unique request ID
        request_id = str(uuid.uuid4())
        
        # Read file contents
        file_content = await file.read()
        
        # Upload original image to storage
        original_path = await storage_service.upload_original_image(user_id, file_content)
        
        # Get the public URL for the original image
        original_url = await storage_service.get_public_url(
            storage_service.BUCKET_ORIGINAL, 
            original_path
        )
        
        # Create initial response
        response = ColorizeResponse(
            request_id=request_id,
            status=ColorizeStatus.PROCESSING,
            original_url=original_url,
            created_at=datetime.utcnow()
        )
        
        # Store the request in database 
        def store_request():
            return get_supabase_client().table("colorize_requests").insert({
                "id": request_id,
                "user_id": user_id,
                "user_email": user_email,
                "status": ColorizeStatus.PROCESSING.value,
                "original_path": original_path,
                "original_url": original_url,
                "created_at": response.created_at.isoformat()
            }).execute()
        
        await safe_supabase_operation(
            store_request,
            error_message="Failed to store colorize request"
        )
        
        # Start colorization in background
        asyncio.create_task(process_colorization(request_id, user_id, file_content, original_path))
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")

@router.get("/status/{request_id}", response_model=ColorizeResponse)
async def get_status(request_id: str):
    """
    Get the status of a colorization request
    
    Args:
        request_id: The ID of the request to check
    """
    try:
        # Query the database for the request
        def get_request():
            return get_supabase_client().table("colorize_requests").select("*").eq("id", request_id).execute()
        
        result = await safe_supabase_operation(
            get_request,
            error_message="Failed to get colorize request status"
        )
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail=f"Request with ID {request_id} not found")
        
        request_data = result.data[0]
        
        # Convert to response model
        return ColorizeResponse(
            request_id=request_data["id"],
            status=request_data["status"],
            original_url=request_data.get("original_url"),
            colorized_url=request_data.get("colorized_url"),
            error_message=request_data.get("error_message"),
            created_at=datetime.fromisoformat(request_data["created_at"]),
            completed_at=datetime.fromisoformat(request_data["completed_at"]) if request_data.get("completed_at") else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get request status: {str(e)}")

async def process_colorization(request_id: str, user_id: str, image_bytes: bytes, original_path: str):
    """
    Process an image colorization in the background
    
    Args:
        request_id: The unique ID for this request
        user_id: The ID of the user
        image_bytes: The binary content of the original image
        original_path: The path to the original image in storage
    """
    try:
        # Process the image using Google AI
        colorized_image_bytes = await colorizer.colorize_image(image_bytes)
        
        # Upload the colorized image
        colorized_path = await storage_service.upload_colorized_image(
            user_id, 
            colorized_image_bytes, 
            original_path
        )
        
        # Get the public URLs
        original_url, colorized_url = await storage_service.get_image_urls(original_path, colorized_path)
        
        # Update the status in the database
        def update_status():
            return get_supabase_client().table("colorize_requests").update({
                "status": ColorizeStatus.COMPLETE.value,
                "colorized_path": colorized_path,
                "colorized_url": colorized_url,
                "completed_at": datetime.utcnow().isoformat()
            }).eq("id", request_id).execute()
        
        await safe_supabase_operation(
            update_status,
            error_message="Failed to update colorize request status"
        )
    
    except Exception as e:
        error_message = str(e)
        
        # Update the status to failed
        def update_failed_status():
            return get_supabase_client().table("colorize_requests").update({
                "status": ColorizeStatus.FAILED.value,
                "error_message": error_message,
                "completed_at": datetime.utcnow().isoformat()
            }).eq("id", request_id).execute()
        
        await safe_supabase_operation(
            update_failed_status,
            error_message="Failed to update colorize request status"
        )
