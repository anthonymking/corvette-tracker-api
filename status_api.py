from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from matson_tracker import get_tracking_info, send_notification, send_test_notification
import os
from typing import Dict, Optional
from pydantic import BaseModel
import json
from datetime import datetime
import pytz

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

async def background_status_updater():
    last_status = None
    last_notification_date = None
    hst = pytz.timezone('Pacific/Honolulu')
    while True:
        try:
            status = await get_tracking_info()
            with open("status_cache.json", "w") as f:
                json.dump(status, f)
            print("[Background] Status cache updated.")

            # Email notification logic
            current_status = status["status"]
            now = datetime.now(hst)
            today_str = now.strftime("%Y-%m-%d")
            should_notify = False
            reason = None

            # Daily 6am HST notification
            if now.hour == 6 and (last_notification_date != today_str):
                should_notify = True
                reason = "6am daily update"
            # Status change notification
            elif last_status is not None and current_status != last_status:
                should_notify = True
                reason = "Status change"

            if should_notify:
                notification_info = {
                    "previous_status": last_status if last_status else "Initial Status",
                    "current_status": current_status,
                    "location": status.get('location', 'Unknown'),
                    "vessel": status.get('vessel', 'Unknown'),
                    "last_update": status.get('last_update', '')
                }
                send_notification(f"Corvette Tracker - Status Update ({reason})", notification_info)
                last_notification_date = today_str
                print(f"[Background] Email sent: {reason}")

            last_status = current_status
        except Exception as e:
            print(f"[Background] Failed to update status cache: {e}")
        await asyncio.sleep(3600)  # Wait 1 hour

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_status_updater())

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
    Get the current tracking status of the Corvette from the cache.
    """
    try:
        with open("status_cache.json", "r") as f:
            tracking_info = json.load(f)
        return tracking_info
    except Exception as e:
        raise HTTPException(status_code=500, detail="Status cache not available or invalid.")

@app.post("/test-email", tags=["Testing"])
def test_email():
    send_test_notification()
    return {"message": "Test notification sent."}

@app.get("/send-status-email", tags=["Testing"])
def send_status_email():
    try:
        with open("status_cache.json", "r") as f:
            tracking_info = json.load(f)
        notification_info = {
            "previous_status": tracking_info.get("status", "Unknown"),
            "current_status": tracking_info.get("status", "Unknown"),
            "location": tracking_info.get("location", "Unknown"),
            "vessel": tracking_info.get("vessel", "Unknown"),
            "last_update": tracking_info.get("last_update", "")
        }
        send_notification("Corvette Tracker - Manual Status Email", notification_info)
        return {"message": "Status notification sent.", "status": tracking_info}
    except Exception as e:
        return {"error": str(e)}

@app.get("/send-current-status", tags=["Testing"])
async def send_current_status_endpoint():
    """
    Manually trigger sending the current status email.
    """
    try:
        tracking_info = await get_tracking_info()
        if tracking_info:
            send_current_status(tracking_info)
            return {"message": "Current status email sent successfully", "status": tracking_info}
        else:
            return {"error": "Failed to fetch tracking information"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 