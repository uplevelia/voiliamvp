"""
Sample VOILIA API endpoints for testing api-documenter agent
"""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

# Models with minimal documentation
class RenderRequest(BaseModel):
    video_url: str
    preset: str = "web-optimized"
    effects: List[str] = []
    watermark_url: Optional[str] = None

class JobResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    output_url: Optional[str] = None

# Endpoint 1: Poorly documented
@app.post("/render")
async def create_render(request: RenderRequest):
    """Create render job"""
    return {"job_id": "abc123", "status": "pending"}

# Endpoint 2: No documentation at all
@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    return {
        "job_id": job_id,
        "status": "processing",
        "progress": 45
    }

# Endpoint 3: Needs better examples
@app.get("/presets")
async def list_presets():
    """List available encoding presets"""
    return {
        "presets": [
            "web-optimized",
            "high-quality",
            "fast-preview"
        ]
    }

# Endpoint 4: Missing error responses
@app.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a rendering job"""
    return {"message": "Job cancelled"}
