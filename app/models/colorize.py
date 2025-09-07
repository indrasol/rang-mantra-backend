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


class ColorizeEphemeralResponse(BaseModel):
    """Response for the privacy-first, non-persistent colourization flow.

    The backend returns the two images encoded as base64 strings that the
    frontend can turn into Blobs/object URLs. Nothing is stored on disk or in
    Supabase. The `expires_in` field lets the frontend know how long it may
    safely cache the images in memory or sessionStorage before discarding
    them (for example, if you implement an optional server-side cache in the
    future).
    """

    original_base64: str = Field(..., description="Base64 encoded original B&W image")
    colorized_base64: str = Field(..., description="Base64 encoded colourised image returned by Google AI")
    expires_in: int = Field(900, description="Time in seconds the backend suggests the client keep the data in memory")

