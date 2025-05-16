from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from matson_tracker import get_tracking_info
import os
from typing import Dict, Optional
from pydantic import BaseModel

class StatusResponse(BaseModel):
    status: str
    last_update: str
    location: str
    vessel: str

class HealthResponse(BaseModel):
    status: str
    service: str

app = FastAPI(
    title="Corvette Tracker API",
    description="API for tracking the shipping status of a Corvette using Matson's tracking system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        HealthResponse: A simple health status response
    """
    return {"status": "healthy", "service": "corvette-tracker-api"}

@app.get("/status", response_model=StatusResponse, tags=["Tracking"])
async def get_status():
    """
    Get the current tracking status of the Corvette.
    
    Returns:
        StatusResponse: Current tracking information including status, last update, location, and vessel
        
    Raises:
        HTTPException: If unable to fetch tracking information
    """
    try:
        tracking_info = await get_tracking_info()
        if tracking_info:
            return {
                "status": tracking_info["status"],
                "last_update": tracking_info["last_update"],
                "location": tracking_info["location"],
                "vessel": tracking_info["vessel"]
            }
        else:
            raise HTTPException(status_code=404, detail="Unable to fetch tracking information")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 