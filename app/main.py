# main.py

import uvicorn
from fastapi import FastAPI, Request, Response, Depends
from app.api.v1.routes.routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
from contextlib import asynccontextmanager
from app.services.logging import setup_logging
from app.utils.logger import log_info
import httpx
import sys
import os
from . import config


# session_manager = SessionManager()
logger = setup_logging()

# @asynccontextmanager
# async def lifespan(app: FastAPI):

#     log_info("Starting up RangMantra ")
#     log_info(f"httpx version: {httpx.__version__}")
    
#     try:
        
#         yield
#     finally:
#         log_info("Shutting down")


app = FastAPI(
    title="RangMantra - Add Color to your Photo",
    description="Add Color to your Photo.",
    version="1.0.0",
    # lifespan=lifespan,
    debug=True,
    redirect_slashes=False
)

# Allow frontend origins
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:3000",  # React default port
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:5173",
    "https://rangmantra.netlify.app",
    "https://development--rangmantra.netlify.app"
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler for HTTP exceptions
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    log_info(f"HTTP exception: {exc.detail}, status_code: {exc.status_code}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    log_info(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# Add custom exception handler for all other exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    log_info(f"Unhandled exception in {request.url.path}: {str(exc)}")
    log_info(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )

# ----- Register routers -----
# v1 grouped under /v1/routes
app.include_router(api_router, prefix="/v1")

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint providing basic API information.
    """
    return {
        "name": "RangMantra - Add Color to your Photo",
        "App version": "1.0.0",
        "python_version": sys.version,
        "docs_url": "/docs",
        "health_check": "https://rangmantra.netlify.app/v1/health"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
