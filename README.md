# CalcsLive Plug for Inventor - Python Bridge

**Status**: ✅ Basic functionality working - Parameter export tested successfully!

Unit-aware calculation integration between Autodesk Inventor f(x) parameters and CalcsLive calculations.

## Architecture

```
Inventor f(x)  ⟷  Python FastAPI Bridge  ⟷  CalcsLive Dashboard
 (COM API)         (localhost:8000)          (Vue/Nuxt UI)
```

**Technology Stack**:
- **Python 3**: win32com.client (direct COM access to Inventor)
- **FastAPI**: Modern HTTP server with auto-documentation
- **pywin32**: Native Windows COM interface (no .NET bridge needed!)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Inventor

1. Open Autodesk Inventor
2. Open or create a Part or Assembly document
3. Add some f(x) parameters (e.g., Length, Width, Height)

### 3. Start Bridge Server

```bash
python main.py
```

Server will start at: `http://localhost:8000`

**Or with auto-reload for development**:
```bash
uvicorn main:app --reload --port 8000
```

### 4. Test Connection

**Browser**: Open http://localhost:8000
- Should see: `{"status":"ok","service":"CalcsLive Inventor Bridge"}`

**CalcsLive Test Page**:
- Navigate to: http://localhost:3000/inventor/paramsTest
- Click "Fetch Inventor Parameters"
- Should display all f(x) parameters from active Inventor document!

## API Endpoints

### `GET /` - Health Check
```bash
curl http://localhost:8000/
```

Response: `{"status":"ok","service":"CalcsLive Inventor Bridge"}`

### `GET /status` - Inventor Connection Status
```bash
curl http://localhost:8000/status
```

**Connected**:
```json
{
  "status": "connected",
  "inventor": "running",
  "document": "Part1.ipt",
  "parameterCount": 5
}
```

**Disconnected**:
```json
{
  "status": "disconnected",
  "inventor": "not_running",
  "error": "Invalid class string"
}
```

### `GET /parameters` - Export All f(x) Parameters
```bash
curl http://localhost:8000/parameters
```

**Response**:
```json
{
  "success": true,
  "documentName": "Part1.ipt",
  "documentType": "Part",
  "parameters": {
    "Length": {
      "value": 100.0,
      "unit": "mm",
      "expression": "100 mm",
      "isReadOnly": false,
      "comment": ""
    },
    "Volume": {
      "value": 150000.0,
      "unit": "mm^3",
      "expression": "Length * Width * Height",
      "isReadOnly": true,
      "comment": "Calculated volume"
    }
  }
}
```

### `POST /parameters/update` - Update Single Parameter
```bash
curl -X POST http://localhost:8000/parameters/update \
  -H "Content-Type: application/json" \
  -d '{"name": "Length", "value": 150.0, "unit": "mm"}'
```

### `GET /mappings` - Get CalcsLive Mappings
Get mapping configuration stored in Inventor file custom properties.

### `POST /mappings` - Save CalcsLive Mappings
Save mapping configuration to Inventor file custom properties.

## Auto-Generated API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## File Structure

```
calcslive-plug-4-inventor/
├── main.py              # FastAPI HTTP server
├── inventor_api.py      # Inventor COM API wrapper
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore patterns
└── README.md           # This file
```

## How It Works

### Direct COM Access via pywin32

```python
import win32com.client

# Connect to running Inventor instance
app = win32com.client.GetActiveObject("Inventor.Application")
doc = app.ActiveDocument
params = doc.ComponentDefinition.Parameters
```

**Key Advantage**: Direct COM access without .NET bridge layer!

### Parameter Export

```python
for param in params:
    result[param.Name] = {
        "value": param.Value,
        "unit": param.Units,
        "expression": param.Expression,
        "isReadOnly": param.IsReadOnly
    }
```

### Mapping Storage

CalcsLive mappings stored in Inventor file custom properties:

```python
custom_props = doc.PropertySets.Item("Inventor User Defined Properties")
custom_props.Add(mappings_json, "CalcsLiveMappings")
```

**Benefit**: Mappings persist with Inventor file!

## Troubleshooting

### Error: "Invalid class string"

**Cause**: Inventor is not running or no document is open.

**Solution**:
1. Start Inventor
2. Open a Part (.ipt) or Assembly (.iam) document
3. Restart the bridge server

### Error: "Port 8000 already in use"

**Find and kill the process**:
```bash
# Find process on port 8000
netstat -ano | findstr :8000

# Kill it (replace PID with actual process ID)
taskkill //F //PID <PID>
```

### CORS Errors in Browser

**Solution**: Add your origin to `main.py`:
```python
allow_origins=[
    "http://localhost:3000",
    "http://localhost:5173",  # Add your dev server port
]
```

## Development

### Live Reload

```bash
uvicorn main:app --reload --port 8000
```

Server auto-restarts on code changes.

### Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Run server
python main.py
```

## Project Status

### ✅ Completed
- [x] Basic HTTP server (FastAPI)
- [x] Inventor COM connection
- [x] Parameter export endpoint
- [x] Parameter update endpoint
- [x] Mappings storage endpoint
- [x] Status check endpoint
- [x] Test UI (paramsTest.vue)
- [x] Error handling and validation

### 🚧 In Progress
- [ ] Full CalcsLive dashboard integration
- [ ] Parameter mapping UI (clone from FreeCAD)
- [ ] Bidirectional sync workflow
- [ ] Unit conversion helpers

### 📋 Planned
- [ ] Bulk parameter update
- [ ] Auto-reconnect on Inventor restart
- [ ] Standalone EXE (PyInstaller)
- [ ] Auto-start on Windows login
- [ ] System tray icon
- [ ] Installer (NSIS or Inno Setup)

## Comparison to FreeCAD Bridge

| Feature | FreeCAD Bridge | Inventor Bridge |
|---------|---------------|----------------|
| **Language** | Python | Python ✅ |
| **API Access** | FreeCAD Python API | win32com (COM) ✅ |
| **Port** | 8787 | 8000 |
| **Parameter Source** | VarSet object | f(x) parameters ✅ |
| **Dashboard** | `/freecad/dashboard` | `/inventor/dashboard` |

**Code Reusability**: ~95% of FreeCAD dashboard can be reused! 🎉

## Why Python (Not .NET)?

**Advantages**:
1. ✅ AC3D Bridge experience (proven patterns)
2. ✅ Direct COM access via pywin32 (no .NET bridge!)
3. ✅ FreeCAD Bridge code reuse (HTTP patterns)
4. ✅ Faster development (Python comfort zone)
5. ✅ Modern stack (FastAPI, type hints, async)

**Performance**: Comparable to .NET (both use COM interop)

## Related Projects

- **CalcsLive Platform**: https://calcs.live
- **CalcsLive Plug for FreeCAD**: https://github.com/CalcsLive/calcslive-plug-4-freecad
- **AC3D Bridge** (predecessor): https://v2-docs.donwen.com/ac3d-bridge/help.html

## License

MIT License - same as CalcsLive main project

## Support

- **Email**: don.wen@calcs.live
- **CalcsLive Docs**: https://calcs.live/help/inventor-integration

---

**Last Updated**: November 10, 2025
**Status**: Basic functionality complete ✅
**Next**: Full dashboard integration
