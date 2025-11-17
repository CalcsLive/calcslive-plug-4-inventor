# CalcsLive Plug for Inventor - Python Bridge

**Status**: ✅ **Production Ready** - Full dashboard integration complete!

**Latest Updates (November 2025)**: Enhanced ArticleId management, mapping deletion, and optimized performance.

Unit-aware calculation integration between Autodesk Inventor User Parameters and CalcsLive calculations platform.

## What is This?

CalcsLive Plug for Inventor is a **two-component system** that supercharges Autodesk Inventor's Parameter Manager (fx) with:

✅ **67+ Engineering Unit Categories** - Mechanical, thermal, electrical, fluid, civil disciplines  
✅ **Bidirectional Engineering-Driven Modeling** - Engineering ⟷ Geometry iterative refinement  
✅ **Decoupled Versatile Calculations** - Reusable calculations independent of CAD models  
✅ **Comment-Based Mapping** - Non-intrusive, no vendor lock-in

**This repository** is the **Bridge Server** component (Python/FastAPI). See [CalcsLive Plug Dashboard](https://www.calcs.live/inventor/dashboard) for the web interface.

## Architecture

```
Inventor User Parameters  ⟷  Bridge Server  ⟷  CalcsLive Dashboard  ⟷  CalcsLive Platform
   (fx with Comments)      (localhost:8000)        (Web UI)              (Calculation Engine)
```

**Technology Stack**:
- **Python 3.8+**: win32com.client (direct COM access to Inventor)
- **FastAPI**: Modern HTTP server with auto-documentation
- **pywin32**: Native Windows COM interface (no .NET bridge needed!)
- **Comment-Based Mapping**: `CA0:symbol #note` format in Inventor Comment fields

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Inventor

1. Open Autodesk Inventor
2. Open or create a Part or Assembly document
3. Add some fx parameters (e.g., Length, Width, Height)

### 3. Start Bridge Server

```bash
python main.py
```

Server will start at: `http://localhost:8000`

**Or with auto-reload for development**:
```bash
uvicorn main:app --reload --port 8000
```

### 4. Connect CalcsLive Dashboard

**Option A - Use Production Dashboard** (Recommended):
1. Open [calcs.live/inventor/dashboard](https://www.calcs.live/inventor/dashboard)
2. Sign in to CalcsLive account (Free tier or higher)
3. Dashboard auto-detects Bridge connection
4. Start mapping parameters via drag-and-drop!

**Option B - Test API Directly**:
```bash
# Health check
curl http://localhost:8000/

# Get all parameters
curl http://localhost:8000/inventor/parameters
```

**Note**: Some browsers (Brave) may block localhost connections from HTTPS sites. See [Troubleshooting](#browser-specific-issues) below.

## API Endpoints

### Primary Endpoints (Production)

**`GET /inventor/parameters`** - Get all User Parameters with mappings
```bash
curl http://localhost:8000/inventor/parameters
```

Returns all User Parameters with parsed Comment field mappings in `CA0:symbol #note` format.

**`POST /inventor/parameters/mapping`** - Update parameter mapping and value
```bash
curl -X POST http://localhost:8000/inventor/parameters/mapping \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Length",
    "symbol": "L",
    "note": "Main beam length",
    "value": 500.0,
    "unit": "cm"
  }'
```

Updates Comment field with `CA0:L #Main beam length` and optionally updates parameter value.

**`POST /inventor/parameters/create`** - Create new User Parameter
```bash
curl -X POST http://localhost:8000/inventor/parameters/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ArticleId",
    "value": "3MAV4GNFQ-3FU",
    "unit": "Text",
    "comment": "CalcsLive Article ID"
  }'
```

Creates text or numeric parameters. **ArticleId** (text parameter) links Inventor model to CalcsLive article.

**`GET /inventor/status`** - Check Inventor connection
```bash
curl http://localhost:8000/inventor/status
```

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
├── .gitignore           # Git ignore patterns
└── README.md            # This file
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

CalcsLive mappings stored in Inventor file user parameters' comment fields. 

**Benefit**: Mappings persist with Inventor file!

## Comment-Based Mapping System

### Mapping Syntax: `CA0:symbol #note`

CalcsLive Plug uses Inventor's **Comment field** for lightweight, non-intrusive mapping storage.

**Format**:
```
CA0:symbol #optional note
```

**Examples**:
```
CA0:L                           # Simple mapping
CA0:L #Main beam length         # With note
CA0:rho #Material density       # Greek letter
CA0:L #`Length #1` #`Rev #3`    # Note contains # (wrapped in backticks)
```

**Why Comment Field?**
- ✅ Native Inventor persistence (saved with .ipt/.iam files)
- ✅ Non-intrusive (models work without CalcsLive Plug)
- ✅ Lightweight (no custom properties or external files)
- ✅ Version control friendly (plain text)

### ArticleId Parameter

**Purpose**: Links your Inventor model to its CalcsLive calculation article.

**Type**: Text parameter (created automatically by Dashboard)

**Example**:
```
Name: ArticleId
Value: "3MAV4GNFQ-3FU"
Type: Text (kTextUnits = 11346)
```

**Benefits**:
- Model "remembers" which calculation it's connected to
- Reopen model → Dashboard auto-loads correct article
- Share model → Recipient gets same calculation automatically
- No vendor lock-in (remove anytime - model works normally)

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

### Browser-Specific Issues

**Brave Browser - "Failed to fetch" Error**:

If using Brave and seeing `ERR_BLOCKED_BY_CLIENT` or "Failed to fetch" errors:

1. Click **Brave Shields** icon (lion logo) in address bar
2. Toggle **Shields down for this site** (calcs.live)
3. Refresh the page

**Why**: Brave's privacy protection blocks localhost connections by default. Disabling Shields for calcs.live allows dashboard to connect to your local Bridge (localhost:8000).

**Alternative**: Use Chrome, Edge, or Firefox - these browsers allow localhost connections from HTTPS sites without additional configuration.

### CORS Errors in Browser

Bridge is pre-configured for production use with:
```python
allow_origins=[
    "https://calcs.live",
    "https://www.calcs.live",
    "http://localhost:3000",  # Development
]
```

For custom development servers, add your origin to `main.py`.

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

## Recent Updates (November 2025)

### ✅ Enhanced Features

**ArticleId Text Parameter Creation**:
- Fixed COM error with correct `kTextUnits = 11346` enum value
- Automatic creation/update of ArticleId parameter by Dashboard
- Models now persist their CalcsLive article connection

**Enhanced Error Handling**:
- Parameter existence detection with detailed response
- COM exception HRESULT codes for debugging
- Clear error messages with actionable guidance

**API Robustness**:
- Text vs numeric parameter handling
- Enhanced validation and error responses
- Backward compatibility maintained

### Project Status

**✅ Production Ready**:
- [x] Comment-based mapping system (`CA0:symbol #note`)
- [x] Full CalcsLive dashboard integration
- [x] Bidirectional sync workflow (Inventor ⟷ CalcsLive)
- [x] ArticleId parameter auto-management
- [x] Unit conversion (Inventor cm ↔ CalcsLive SI)
- [x] Drag-and-drop parameter mapping UI
- [x] Single-click PQ editing
- [x] Mapping deletion with persistence
- [x] Article change confirmation workflow
- [x] Error handling and validation
- [x] Comprehensive testing (23 unit tests)

**📋 Future Enhancements**:
- [ ] Standalone EXE (PyInstaller)
- [ ] Auto-start on Windows login
- [ ] System tray icon
- [ ] Installer (NSIS or Inno Setup)
- [ ] Multi-namespace support (CA1, CA2, etc.)

## Comparison to Similar Projects

### vs. [FreeCAD Bridge](https://github.com/CalcsLive/calcslive-plug-4-freecad)

| Feature | FreeCAD Bridge | Inventor Bridge |
|---------|---------------|----------------|
| **Language** | Python | Python ✅ |
| **API Access** | FreeCAD Python API | win32com (COM) ✅ |
| **Port** | 8787 | 8000 |
| **Parameter Source** | VarSet object | User Parameters (fx) ✅ |
| **Mapping Storage** | VarSet Comment | Parameter Comment ✅ |
| **Dashboard** | `/freecad/dashboard` | `/inventor/dashboard` ✅ |
| **Status** | Production | **Production** ✅ |

**Code Reusability**: Dashboard architecture shared across both bridges - proven pattern!

### vs. AC3D Bridge (Predecessor)

CalcsLive Plug for Inventor is the spiritual successor to [AC3D Bridge](https://v2-docs.donwen.com/ac3d-bridge/help.html) with modern technology:

| Feature | AC3D Bridge (2015) | CalcsLive Plug (2025) |
|---------|-------------------|----------------------|
| **Technology** | .NET WinForms | Python + FastAPI + Vue 3 |
| **UI** | Desktop app | Web dashboard |
| **Calculations** | Embedded XML | Cloud platform |
| **Persistence** | Custom properties | Comment fields |
| **Unit System** | Limited | 67+ categories |

**Lessons Applied**: 10+ years of engineering-driven modeling experience refined into modern architecture.

## Why Python (Not .NET)?

**Advantages**:
1. ✅ AC3D Bridge experience (proven patterns)
2. ✅ Direct COM access via pywin32 (no .NET bridge!)
3. ✅ FreeCAD Bridge code reuse (HTTP patterns)
4. ✅ Faster development (Python comfort zone)
5. ✅ Modern stack (FastAPI, type hints, async)

**Performance**: Comparable to .NET (both use COM interop)

## Key Features

✅ **Comment-Based Mapping** - Non-intrusive `CA0:symbol #note` format in Inventor Comment fields  
✅ **ArticleId Persistence** - Models remember their CalcsLive article connection  
✅ **Bidirectional Sync** - Engineering ⟷ Geometry iterative refinement  
✅ **Unit Conversion** - Automatic conversion between Inventor cm-based and CalcsLive SI  
✅ **Formula Detection** - Auto-detects dependent parameters (read-only)  
✅ **Greek Letter Support** - η, ρ, α, etc. in CalcsLive symbols  
✅ **Zero Vendor Lock-In** - Models work with or without CalcsLive Plug  
✅ **Production Tested** - 23 comprehensive unit tests

## Documentation

- **User Guide**: [calcs.live/help/inventor-integration](https://www.calcs.live/help/inventor-integration) 

## Related Projects

- **CalcsLive Platform**: [calcs.live](https://www.calcs.live) 
- **CalcsLive Plug for FreeCAD**: Similar bridge for FreeCAD VarSet integration
- **AC3D Bridge** (predecessor): [v2-docs.donwen.com/ac3d-bridge](https://v2-docs.donwen.com/ac3d-bridge/help.html) 

## Testing

**Run Unit Tests**:
```bash
pytest test_comment_parser.py -v
```

**Test Coverage**: 23 comprehensive tests covering:
- Valid mappings with Greek letters
- Notes with special characters (`#` in notes, backticks)
- Invalid cases (missing namespace, invalid namespace)
- Edge cases (empty comments, whitespace, None values)
- Round-trip (build → parse → verify)

## License

MIT License 

## Support & Contributing

**Issues & Support**:
- Report bugs: [GitHub Issues](https://github.com/CalcsLive/calcslive-plug-4-inventor/issues)
- Email: don.wen@calcs.live

**Contributing**:
- Pull requests welcome! 
- Follow existing code patterns and maintain test coverage

---

**Last Updated**: November 16, 2025
**Status**: ✅ **Production Ready** - Enhanced with ArticleId management, mapping deletion, and optimized performance
**Dashboard**: [calcs.live/inventor/dashboard](https://www.calcs.live/inventor/dashboard)
