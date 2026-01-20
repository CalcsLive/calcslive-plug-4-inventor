# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from inventor_api import (
    get_user_parameters,
    update_parameter_mapping,
    create_user_parameter
)
import uvicorn

# Read version from pyproject.toml
def get_version():
    try:
        import toml
        with open("pyproject.toml", "r") as f:
            data = toml.load(f)
            return data["project"]["version"]
    except:
        return "1.1.1"  # Fallback version

app = FastAPI(
    title="CalcsLive Plug for Inventor",
    description="HTTP bridge for Inventor User Parameters with CalcsLive integration",
    version=get_version()
)

# CORS for CalcsLive dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://calcslive.com",
        "https://www.calcslive.com",
        "https://calcslive.com",
        "https://www.calcslive.com"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "CalcsLive Plug for Inventor", "version": get_version()}

@app.get("/inventor/health")
def health_check():
    """Health check for Inventor-specific endpoints"""
    return {"status": "ok", "service": "CalcsLive Plug for Inventor", "version": get_version()}

@app.get("/inventor/document")
def get_document_info():
    """Get active Inventor document information"""
    result = get_user_parameters()
    if result.get("success"):
        return {
            "status": "connected",
            "documentName": result.get("documentName"),
            "parameterCount": len(result.get("parameters", []))
        }
    else:
        raise HTTPException(status_code=503, detail=result.get("error"))

@app.get("/inventor/parameters")
def read_user_parameters():
    """
    Get User Parameters from active Inventor document.
    Includes Comment field parsing for CalcsLive mappings and dimensional analysis.
    """
    result = get_user_parameters()

    if not result.get("success"):
        raise HTTPException(status_code=503, detail=result.get("error"))

    return result

@app.post("/inventor/parameters/mapping")
def set_parameter_mapping(data: dict):
    """
    Set or update User Parameter Comment field with CalcsLive mapping.
    Optionally also update the parameter value.

    Request body:
    {
        "name": "Length",           // required
        "symbol": "L",              // optional - CalcsLive PQ symbol
        "note": "Main beam length", // optional - user note
        "value": 5.0,               // optional - new value
        "unit": "m"                 // optional - unit for new value
    }

    To remove mapping, pass symbol=null or omit it
    """
    name = data.get("name")
    symbol = data.get("symbol")
    note = data.get("note")
    value = data.get("value")
    unit = data.get("unit")

    if not name:
        raise HTTPException(status_code=400, detail="Parameter 'name' is required")

    result = update_parameter_mapping(name, symbol, note, value, unit)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result

@app.delete("/inventor/parameters/mapping")
def remove_parameter_mapping(data: dict):
    """
    Remove CalcsLive mapping from User Parameter Comment field.

    Request body:
    {
        "name": "Length"  // required
    }
    """
    name = data.get("name")

    if not name:
        raise HTTPException(status_code=400, detail="Parameter 'name' is required")

    # Clear mapping by setting symbol to None
    result = update_parameter_mapping(name, symbol=None, note=None)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result

@app.post("/inventor/parameters/create")
def create_parameter(data: dict):
    """
    Create a new User Parameter in Inventor.

    Request body:
    {
        "name": "ArticleId",           // required - parameter name
        "value": "3MAV4GNFQ-3FU",      // optional - initial value
        "comment": "eg: 3MAV4GNFQ-3FU, taken from the calculation article url",  // optional
        "unit": "Text"                 // optional - default "Text" for text parameters
    }

    Use cases:
    - Create ArticleId parameter for CalcsLive integration
    - Create custom text or numeric parameters programmatically
    """
    name = data.get("name")
    value = data.get("value", "")
    comment = data.get("comment", "")
    unit = data.get("unit", "Text")

    if not name:
        raise HTTPException(status_code=400, detail="Parameter 'name' is required")

    result = create_user_parameter(name, value, comment, unit)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)