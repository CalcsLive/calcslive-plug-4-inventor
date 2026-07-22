# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.datastructures import MutableHeaders
from inventor_api import (
    get_user_parameters,
    update_parameter_mapping,
    create_user_parameter,
    convert_units
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

# Private Network Access (PNA) middleware — required for Chrome/Brave to allow
# requests from https://calcslive.com to localhost (loopback address).
# Chrome sends OPTIONS preflight with Access-Control-Request-Private-Network: true
# and blocks the request unless the response includes Allow-Private-Network: true.
#
# Using raw ASGI (not BaseHTTPMiddleware) — BaseHTTPMiddleware can silently drop
# headers when the wrapped middleware returns a streaming response.
class PrivateNetworkAccessMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {k.lower(): v for k, v in scope.get("headers", [])}
        method = scope.get("method", "")

        # Intercept PNA preflight — short-circuit before CORSMiddleware sees it
        if method == "OPTIONS" and b"access-control-request-private-network" in headers:
            origin = headers.get(b"origin", b"*")
            await send({
                "type": "http.response.start",
                "status": 204,
                "headers": [
                    (b"access-control-allow-origin", origin),
                    (b"access-control-allow-methods", b"*"),
                    (b"access-control-allow-headers", b"*"),
                    (b"access-control-allow-private-network", b"true"),
                    (b"vary", b"origin"),
                ],
            })
            await send({"type": "http.response.body", "body": b""})
            return

        # Non-preflight: pass through, inject PNA header into the response
        async def send_with_pna(message: dict) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)["access-control-allow-private-network"] = "true"
            await send(message)

        await self.app(scope, receive, send_with_pna)

# CORS for CalcsLive dashboard (added first = inner layer)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://calcslive.com",
        "https://www.calcslive.com",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Private Network Access middleware (added last = outermost layer, runs first)
# Must be outermost so it intercepts PNA preflights before CORSMiddleware
app.add_middleware(PrivateNetworkAccessMiddleware)

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


@app.post("/inventor/convert")
def convert_unit_value(data: dict):
    """
    Convert a value between units using Inventor's UnitsOfMeasure API.

    This leverages Inventor's robust unit conversion which handles:
    - Standard conversions (mm ↔ in, kg ↔ lb, etc.)
    - Temperature with proper offsets (°C ↔ °F ↔ K)
    - Complex derived units (kg/m³, N·m, etc.)

    Request body:
    {
        "value": 609.6,      // required - numeric value to convert
        "fromUnit": "mm",    // required - source unit
        "toUnit": "in"       // required - target unit
    }

    Returns:
    {
        "success": true,
        "value": 24.0,       // converted value
        "fromUnit": "mm",
        "toUnit": "in",
        "originalValue": 609.6
    }
    """
    value = data.get("value")
    from_unit = data.get("fromUnit")
    to_unit = data.get("toUnit")

    if value is None:
        raise HTTPException(status_code=400, detail="'value' is required")
    if not from_unit:
        raise HTTPException(status_code=400, detail="'fromUnit' is required")
    if not to_unit:
        raise HTTPException(status_code=400, detail="'toUnit' is required")

    result = convert_units(value, from_unit, to_unit)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)