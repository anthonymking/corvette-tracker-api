from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from matson_tracker import get_tracking_info
import os

app = FastAPI(title="Corvette Tracker API")

# Add CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "corvette-tracker-api"}

@app.get("/status")
async def get_status():
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