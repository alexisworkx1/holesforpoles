from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="Cloud Automation Web Application",
    description="A FastAPI application for cloud automation",
    version="0.1.0"
)

@app.get("/")
async def root():
    """
    Root endpoint that returns a welcome message.
    """
    return {
        "message": "Welcome to the Cloud Automation Web Application!",
        "status": "online",
        "documentation": "/docs"
    }

@app.get("/health")
async def health():
    """
    Health endpoint that returns the server status.
    """
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "version": app.version
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

