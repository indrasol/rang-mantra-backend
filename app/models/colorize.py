from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ColorizeStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class ColorizeRequest(BaseModel):
    user_id: str = Field(..., description="ID of the user requesting colorization")
    user_email: Optional[str] = Field(None, description="Email of the user for folder organization")


class ColorizeResponse(BaseModel):
    request_id: str = Field(..., description="Unique ID for this colorization request")
    status: ColorizeStatus = Field(..., description="Status of the colorization request")
    original_url: Optional[str] = Field(None, description="URL to the original image")
    colorized_url: Optional[str] = Field(None, description="URL to the colorized image")
    error_message: Optional[str] = Field(None, description="Error message if colorization failed")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the request was created")
    completed_at: Optional[datetime] = Field(None, description="When the request was completed")
