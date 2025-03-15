import logging
import os
import socket
import platform
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv

from app.database import Base, engine, SessionLocal
from app.endpoints.auth import router as auth_router
from app.config import settings

# Load environment variables from .env file
load_dotenv()

# Get environment variables with defaults
PORT = int(os.getenv("PORT", 8000))
ENV = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true" if not hasattr(settings, "DEBUG") else settings.DEBUG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log"),
    ],
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Holes For Poles API",
    description="Cloud Automation Web Application API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if hasattr(settings, "CORS_ORIGINS") else os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting application in {ENV} environment")
    logger.info(f"Debug mode: {DEBUG}")
    
# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")

# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP exception {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error": str(exc) if DEBUG else ""},
    )

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint that returns a welcome message.
    """
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to Holes For Poles API!",
        "status": "online",
        "documentation": "/docs",
        "environment": ENV
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health endpoint that returns detailed server status information.
    Used for monitoring and health checks.
    """
    logger.debug("Health check endpoint accessed")
    
    # Gather system information
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    
    try:
        # Create a database session to test database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "connected"
        status = "healthy"
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        db_status = "disconnected"
        status = "unhealthy"
    
    return {
        "status": status,
        "database": db_status,
        "timestamp": datetime.now().isoformat(),
        "version": app.version,
        "environment": ENV,
        "hostname": hostname,
        "ip_address": ip_address,
        "python_version": platform.python_version(),
        "system_info": {
            "os": platform.system(),
            "os_version": platform.version(),
            "machine": platform.machine(),
        }
    }

# Run the application when executed directly
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on port {PORT}")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=PORT,
        reload=DEBUG
    )
