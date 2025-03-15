import os
import logging
import socket
import platform
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
# Get environment variables with defaults
PORT = int(os.getenv("PORT", 8000))
ENV = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

app = FastAPI(
    title="Cloud Automation Web Application",
    description="A FastAPI application for cloud automation",
    version="0.1.0",
    debug=DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc) if DEBUG else ""}
    )

# HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting application in {ENV} environment")
    logger.info(f"Debug mode: {DEBUG}")
    
# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")
@app.get("/")
async def root():
    """
    Root endpoint that returns a welcome message.
    """
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to the Cloud Automation Web Application!",
        "status": "online",
        "documentation": "/docs",
        "environment": ENV
    }

@app.get("/health")
async def health() -> Dict[str, Any]:
    """
    Health endpoint that returns detailed server status information.
    Used for monitoring and health checks.
    """
    logger.debug("Health check endpoint accessed")
    
    # Gather system information
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    
    return {
        "status": "operational",
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
        },
        "uptime": "unknown"  # In a production app, you might track this
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
