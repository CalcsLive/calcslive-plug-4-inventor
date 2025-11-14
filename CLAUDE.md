# CalcsLive Plug for Inventor - Bridge Server

*Part of the CalcsLive Plug ecosystem - Developer guidance for Claude Code*

## Project Context

**This Repository**: CalcsLive-Inventor Bridge (Python server component)
**Main Project**: C:\E3d\E3dProJs\2025\25018-tiptap-calcs-3
**Related Plugs**: n8n, Google Sheets, FreeCAD (see main project CLAUDE.md)

## Quick Links

**Main Project Documentation**:
- Dashboard UI: `pages/inventor/dashboard.vue` (1,131 lines)
- Help Guide: `content/help/inventor-integration.md` (498 lines)
- Status Doc: `.claude/implementation/inventor-integration-status-2025-11-14.md` (1,224 lines)
- Marketing: `.claude/marketing/inventor-plug-announcement.md` (745 lines)

**This Repository**:
- Server Entry: `main.py` - FastAPI with CORS
- API Logic: `inventor_api.py` - COM automation (499 lines)
- Tests: `test_comment_parser.py` - 23 comprehensive tests

## Architecture Overview

### CalcsLive Plug for Inventor Components

```
┌──────────────────────────────────────────────────────────────┐
│                    Inventor Model (.ipt/.iam)                │
│              User Parameters with Comment mappings           │
└────────────────────────┬─────────────────────────────────────┘
                         │ (COM API via win32com)
                         ↓
┌──────────────────────────────────────────────────────────────┐
│          THIS REPO: CalcsLive-Inventor Bridge                │
│  - FastAPI server (localhost:8000)                           │
│  - Comment parsing (CA0:symbol #note)                        │
│  - Unit handling (Inventor cm ↔ Dashboard)                   │
└────────────────────────┬─────────────────────────────────────┘
                         │ (HTTP REST API)
                         ↓
┌──────────────────────────────────────────────────────────────┐
│          MAIN REPO: CalcsLive Plug Dashboard                 │
│  - Web UI (pages/inventor/dashboard.vue)                     │
│  - Unit conversion (cm ↔ SI via dimensional analysis)        │
│  - PQ mapping interface                                      │
└────────────────────────┬─────────────────────────────────────┘
                         │ (CalcsLive API)
                         ↓
┌──────────────────────────────────────────────────────────────┐
│              CalcsLive Calculation Platform                  │
│  - Unit-aware calculation engine                             │
│  - 67+ engineering unit categories                           │
└──────────────────────────────────────────────────────────────┘
```

## Comment-Based Mapping System

### Syntax: `CA0:symbol #note`

**Format Components**:
- **Namespace**: `CA0`, `CA1`, etc. (CA = CalcsLive Article)
- **Symbol**: MathJS-compatible CalcsLive PQ symbol (e.g., `L`, `rho`, `η`)
- **Note**: Optional user documentation (preserved as-is)

**Examples**:
```
CA0:L                           # Simple mapping
CA0:L #Length parameter         # With note
CA0:rho #Material density       # Greek letter
CA0:L #`Length #1` #`Rev #3`    # Note contains # (backticks)
```

**Why Comment Field?**:
- ✅ Native Inventor persistence (saved with .ipt/.iam files)
- ✅ Non-intrusive (models work without CalcsLive Plug)
- ✅ Lightweight (no custom properties or external files)
- ✅ Version control friendly (plain text)

## Key Functions

### `parse_comment_mapping(comment: str)` → Dict

Parse Inventor Comment field for CalcsLive mapping.

**Returns**:
```python
{
    "mapping": "L",              # Symbol or None
    "note": "Length parameter"   # Note or None
}
```

**Test Coverage**: 23 comprehensive tests in `test_comment_parser.py`

### `build_comment_string(symbol, note, namespace="CA0")` → str

Build Comment field string from components.

**Examples**:
```python
build_comment_string("L", None) → "CA0:L"
build_comment_string("L", "Length parameter") → "CA0:L #Length parameter"
```

### `get_user_parameters()` → Dict

Export User Parameters from active Inventor document.

**Returns**:
```python
{
    "success": True,
    "documentName": "beam.ipt",
    "parameters": [
        {
            "name": "Length",
            "value": 500.0,        # Inventor internal units (cm)
            "displayValue": 5000.0, # Inventor display units (mm)
            "unit": "mm",          # Display unit
            "internalUnit": "cm",  # Internal unit
            "expression": "",
            "comment": "CA0:L #Main beam",
            "mapping": "L",
            "note": "Main beam"
        }
    ]
}
```

**IMPORTANT - Unit Handling**:
- `value`: Inventor's internal units (cm-based for length)
- `displayValue`: Inventor's display units (as shown in f(x))
- Dashboard handles conversion to CalcsLive SI units using dimensional analysis

### `update_parameter_mapping(name, symbol, note, value, unit)` → Dict

Update User Parameter Comment field with mapping, optionally update value.

**Request**:
```python
update_parameter_mapping(
    name="Length",
    symbol="L",
    note="Main beam length",
    value=500.0,  # Inventor internal units (cm)
    unit=None     # Optional display unit
)
```

**Value Handling**:
- Dashboard converts CalcsLive SI → Inventor internal units before calling
- Bridge accepts values in Inventor internal units (cm-based)
- Inventor handles display unit conversion automatically

## API Endpoints

### Primary Endpoints

**`GET /inventor/parameters`**
- Export User Parameters with mappings
- Includes Comment parsing
- Returns dimensional data for conversion

**`POST /inventor/parameters/mapping`**
- Set or update Comment field mapping
- Optionally update parameter value
- Handles formula detection (read-only parameters)

**`POST /inventor/parameters/update`**
- Update parameter value without changing mapping
- Unit conversion handled by Inventor

**`DELETE /inventor/parameters/mapping`**
- Remove mapping from Comment field
- Parameter value unchanged

### Legacy Endpoints (Deprecated)

- `GET /parameters` → Use `/inventor/parameters`
- `GET /mappings` → PropertySets approach (replaced by Comment field)
- `POST /mappings` → PropertySets approach (replaced by Comment field)

## Development Workflow

### Testing Changes

1. **Edit Code**: Modify `inventor_api.py` or `main.py`
2. **Restart Bridge**: Ctrl+C, then `python main.py`
3. **Test via Dashboard**: Open calcs.live/inventor/dashboard
4. **Run Tests**: `pytest test_comment_parser.py -v`

### Common Development Tasks

**Add New API Endpoint**:
1. Add function to `inventor_api.py` (COM logic)
2. Add route to `main.py` (FastAPI endpoint)
3. Update Dashboard to call new endpoint
4. Test end-to-end workflow

**Modify Comment Syntax**:
1. Update `parse_comment_mapping()` and `build_comment_string()`
2. Update tests in `test_comment_parser.py`
3. Verify backward compatibility with existing mappings
4. Update documentation in main repo

**Debug COM Issues**:
1. Check Inventor is open with active document
2. Verify User Parameters exist (not just Model Parameters)
3. Test COM connection: `python -c "import win32com.client; app = win32com.client.GetActiveObject('Inventor.Application'); print(app.Caption)"`
4. Check console output for detailed error messages

## Unit Conversion Architecture

### Inventor Internal Units

**Inventor Storage**:
- Length: cm (centimeters)
- Mass: kg (kilograms)
- Angle: rad (radians)
- Volume: cm³
- Density: kg/cm³

### Dashboard Conversion Flow

```
Inventor → Bridge → Dashboard → CalcsLive

Step 1 (Bridge): Export raw value in cm
    value = 500.0 cm (Inventor internal)

Step 2 (Dashboard): Query dimensional data
    GET /api/units/dimension?unit=mm
    Response: { dimension: { L: 1 } }

Step 3 (Dashboard): Convert using dimensional analysis
    si_value = inventor_value / (100^L)
    si_value = 500.0 / 100 = 5.0 m

Step 4 (CalcsLive): Calculate in SI
    All calculations use SI base units

Step 5 (Return): Convert back to Inventor
    inventor_value = si_value * (100^L)
    inventor_value = 5.0 * 100 = 500.0 cm
```

**Why Dashboard Does Conversion?**:
- ✅ Bridge stays simple (no unit conversion logic)
- ✅ CalcsLive units system handles complexity
- ✅ Single source of truth for unit data
- ✅ Works for all 67+ unit categories

## Integration with Main Project

### Dashboard Files (Main Repo)

**`pages/inventor/dashboard.vue`**:
- Connects to Bridge via `fetch('http://localhost:8000/inventor/parameters')`
- Handles unit conversion (cm ↔ SI)
- PQ mapping interface
- Bidirectional sync controls

**Key Dashboard Functions**:
```javascript
// Load parameters from Bridge
async function loadInventorParameters()

// Convert units (Dashboard responsibility)
async function convertInventorToCalcsLive(value, unit)
async function convertCalcsLiveToInventor(value, unit)

// Sync operations
async function syncToCalcsLive()    // Inventor → CalcsLive
async function syncTo3dParams()     // CalcsLive → Inventor
async function update3dModel()      // Persist to Inventor
```

### When to Edit Which Repo

**Edit Bridge Repo** (this repo):
- API endpoint changes
- COM automation logic
- Comment parsing syntax
- Error handling in Inventor access

**Edit Main Repo**:
- Dashboard UI/UX
- Unit conversion logic
- PQ mapping interface
- User-facing documentation

**Edit Both**:
- API contract changes (endpoint + dashboard client)
- Unit handling architecture
- New feature spanning both sides

## Testing Strategy

### Unit Tests (This Repo)

**`test_comment_parser.py`**: 23 tests covering:
- Valid mappings: `CA0:L`, `CA0:L #note`, Greek letters
- Notes with special characters: `#` in notes, backticks
- Invalid cases: Missing namespace, invalid namespace, colons in symbol
- Edge cases: Empty comments, whitespace, None values
- Round-trip: build → parse → verify

**Run Tests**:
```bash
pytest test_comment_parser.py -v
```

### Integration Tests (Manual)

1. **Bridge Health Check**:
   ```bash
   curl http://127.0.0.1:8000/
   # Expected: {"status":"ok","service":"CalcsLive Plug for Inventor"}
   ```

2. **Parameter Export**:
   ```bash
   curl http://127.0.0.1:8000/inventor/parameters
   # Expected: JSON with parameters array
   ```

3. **End-to-End Workflow**:
   - Open Inventor with User Parameters
   - Start Bridge: `python main.py`
   - Open Dashboard: calcs.live/inventor/dashboard
   - Create mapping via drag-and-drop
   - Verify Comment field in Inventor f(x)
   - Sync bidirectionally
   - Update 3D Model
   - Verify values persist after reopening

## Troubleshooting

### Bridge Won't Start

**Error: "Inventor.Application not found"**
- Cause: Inventor not running or COM registration issue
- Fix: Launch Inventor, then start Bridge

**Error: "Port 8000 already in use"**
- Cause: Previous Bridge instance still running
- Fix: Kill process on port 8000, or change port in `main.py`

### Parameters Not Loading

**Error: "No active Inventor document"**
- Cause: No document open in Inventor
- Fix: Open any .ipt or .iam file

**Empty Parameters Array**
- Cause: No User Parameters exist (only Model Parameters)
- Fix: Create User Parameters via f(x) manager

### Mapping Not Persisting

**Comment Field Blank After Update**
- Cause: Parameter might be read-only or protected
- Fix: Check `IsReadOnly` property, verify parameter type

**Mapping Lost After Reopening**
- Cause: Document not saved after mapping
- Fix: Save Inventor file after "Update 3D Model"

## Related Documentation

**Main Project CLAUDE.md**: Ecosystem overview, all CalcsLive Plugs
**Inventor Status Doc**: `.claude/implementation/inventor-integration-status-2025-11-14.md`
**User Help Guide**: `content/help/inventor-integration.md`
**Marketing Content**: `.claude/marketing/inventor-plug-announcement.md`

**Other CalcsLive Plugs**:
- n8n Integration: `25031-n8n-node-calcslive`
- FreeCAD Integration: VarSet-based approach
- Google Sheets: Custom formula functions

## Development Philosophy

**Keep Bridge Minimal**: Bridge is a thin translation layer between Inventor COM and HTTP. Complex logic belongs in Dashboard (main repo) or CalcsLive platform.

**Dashboard Handles Units**: All unit conversion logic lives in Dashboard using CalcsLive units API. Bridge only exports raw Inventor values.

**Comment Field is Source of Truth**: Mappings stored in native Inventor Comment field - no external files, no custom properties (unless PropertySets explicitly needed).

**Backward Compatibility**: Legacy endpoints remain functional. New features added alongside, not replacing.

---

*Last Updated: 2025-11-14*
*Status: ✅ Production-ready*
*Related: CalcsLive Plug ecosystem (n8n, FreeCAD, Google Sheets, Inventor)*
