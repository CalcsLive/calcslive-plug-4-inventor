# main.py (Enhanced)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from inventor_api import get_fx_parameters, update_fx_parameter, get_mappings, save_mappings
import uvicorn

app = FastAPI(
    title="CalcsLive Inventor Bridge",
    description="HTTP bridge for Inventor f(x) parameter access",
    version="0.1.0"
)

# CORS for CalcsLive dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://calcs.live",
        "https://www.calcs.live"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "CalcsLive Inventor Bridge"}

@app.get("/status")
def get_status():
    """Check if Inventor is accessible"""
    result = get_fx_parameters()
    if result.get("success"):
        return {
            "status": "connected",
            "inventor": "running",
            "document": result.get("documentName"),
            "parameterCount": len(result.get("parameters", {}))
        }
    else:
        return {
            "status": "disconnected",
            "inventor": "not_running" if "Inventor.Application" in result.get("error", "") else "error",
            "error": result.get("error")
        }

@app.get("/parameters")
def read_parameters():
    """Export all f(x) parameters from active Inventor document"""
    result = get_fx_parameters()
    
    # Return error with proper HTTP status
    if not result.get("success"):
        raise HTTPException(status_code=503, detail=result.get("error"))
    
    return result

@app.post("/parameters/update")
def update_parameter(data: dict):
    """
    Update a single f(x) parameter value

    Request body:
    {
        "name": "Length",
        "value": 150.0,
        "unit": "mm"  // optional
    }
    """
    name = data.get("name")
    value = data.get("value")
    unit = data.get("unit")

    if not name:
        raise HTTPException(status_code=400, detail="Parameter 'name' is required")
    if value is None:
        raise HTTPException(status_code=400, detail="Parameter 'value' is required")

    result = update_fx_parameter(name, value, unit)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result


@app.get("/mappings")
def read_mappings():
    """Get CalcsLive mappings stored in Inventor file custom properties"""
    result = get_mappings()

    if not result.get("success"):
        raise HTTPException(status_code=503, detail=result.get("error"))

    return result


@app.post("/mappings")
def write_mappings(data: dict):
    """
    Save CalcsLive mappings to Inventor file custom properties

    Request body: mappings dictionary (will be JSON serialized)
    """
    result = save_mappings(data)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)