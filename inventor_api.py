# inventor_api.py (Enhanced)
import pythoncom
import win32com.client
from typing import Dict, Any

def get_fx_parameters() -> Dict[str, Any]:
    """
    Get f(x) parameters from active Inventor document.
    
    Returns:
        Dict with parameter data or error message
    """
    pythoncom.CoInitialize()
    try:
        # Connect to running Inventor instance
        app = win32com.client.GetActiveObject("Inventor.Application")
        doc = app.ActiveDocument
        
        # Verify document exists
        if doc is None:
            return {"error": "No active Inventor document"}

        # Document type constants
        kPartDocumentObject = 12291
        kAssemblyDocumentObject = 12292

        # Debug: Log the actual document type
        actual_doc_type = doc.DocumentType
        print(f"DEBUG: Document type = {actual_doc_type}")

        # For now, let's be more lenient and just check if ComponentDefinition exists
        if not hasattr(doc, 'ComponentDefinition'):
            return {
                "success": False,
                "error": f"Document does not have ComponentDefinition. Document type: {actual_doc_type}"
            }

        params = doc.ComponentDefinition.Parameters
        result = {}

        for param in params:
            try:
                # Safely access parameter properties with fallbacks
                param_name = param.Name if hasattr(param, 'Name') else str(param)

                result[param_name] = {
                    "value": param.Value if hasattr(param, 'Value') else 0,
                    "unit": param.Units if (hasattr(param, 'Units') and param.Units) else "",
                    "expression": param.Expression if hasattr(param, 'Expression') else "",
                    "isReadOnly": param.IsReadOnly if hasattr(param, 'IsReadOnly') else False,
                    "comment": param.Comment if hasattr(param, 'Comment') else "",
                }
            except Exception as param_error:
                # If we can't read this parameter, skip it and log
                print(f"WARNING: Could not read parameter: {param_error}")
                continue
        
        return {
            "success": True,
            "documentName": doc.DisplayName,  # ✨ NEW: Document context
            "documentType": "Part" if doc.DocumentType == kPartDocumentObject else "Assembly",
            "parameters": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "errorType": type(e).__name__  # ✨ NEW: Error classification
        }
    finally:
        pythoncom.CoUninitialize()


def update_fx_parameter(name: str, value: float, unit: str = None) -> Dict[str, Any]:
    """
    Update a single f(x) parameter value in active Inventor document.

    Args:
        name: Parameter name (e.g., "Length", "Width")
        value: New value to set
        unit: Optional unit string (if different from parameter's current unit)

    Returns:
        Dict with success status or error message
    """
    pythoncom.CoInitialize()
    try:
        app = win32com.client.GetActiveObject("Inventor.Application")
        doc = app.ActiveDocument

        if doc is None:
            return {"success": False, "error": "No active Inventor document"}

        params = doc.ComponentDefinition.Parameters

        # Find parameter by name
        try:
            param = params.Item(name)
        except:
            return {"success": False, "error": f"Parameter '{name}' not found"}

        # Check if parameter is read-only
        if param.IsReadOnly:
            return {"success": False, "error": f"Parameter '{name}' is read-only (calculated)"}

        # Update value
        # Note: Inventor handles unit conversion automatically if value includes unit
        if unit and unit != param.Units:
            # Convert value with unit
            # Inventor's Value property handles this automatically
            param.Expression = f"{value} {unit}"
        else:
            # Direct value assignment
            param.Value = value

        return {
            "success": True,
            "parameter": name,
            "newValue": param.Value,
            "unit": param.Units
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "errorType": type(e).__name__
        }
    finally:
        pythoncom.CoUninitialize()


def get_mappings() -> Dict[str, Any]:
    """
    Get CalcsLive mappings stored in Inventor file custom properties.

    Returns:
        Dict with mappings data or error message
    """
    pythoncom.CoInitialize()
    try:
        app = win32com.client.GetActiveObject("Inventor.Application")
        doc = app.ActiveDocument

        if doc is None:
            return {"success": False, "error": "No active Inventor document"}

        # Access custom property set
        try:
            custom_props = doc.PropertySets.Item("Inventor User Defined Properties")

            # Try to get CalcsLiveMappings property
            try:
                mappings_json = custom_props.Item("CalcsLiveMappings").Value

                # Parse JSON
                import json
                mappings = json.loads(mappings_json)

                return {
                    "success": True,
                    "mappings": mappings
                }
            except:
                # Property doesn't exist yet - return empty mappings
                return {
                    "success": True,
                    "mappings": {}
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to access custom properties: {str(e)}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "errorType": type(e).__name__
        }
    finally:
        pythoncom.CoUninitialize()


def save_mappings(mappings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save CalcsLive mappings to Inventor file custom properties.

    Args:
        mappings: Dict containing mapping configuration (will be JSON serialized)

    Returns:
        Dict with success status or error message
    """
    pythoncom.CoInitialize()
    try:
        app = win32com.client.GetActiveObject("Inventor.Application")
        doc = app.ActiveDocument

        if doc is None:
            return {"success": False, "error": "No active Inventor document"}

        # Convert mappings to JSON string
        import json
        mappings_json = json.dumps(mappings, indent=2)

        # Access custom property set
        try:
            custom_props = doc.PropertySets.Item("Inventor User Defined Properties")

            # Try to update existing property, or create new one
            try:
                # Update existing property
                prop = custom_props.Item("CalcsLiveMappings")
                prop.Value = mappings_json
            except:
                # Create new property
                custom_props.Add(mappings_json, "CalcsLiveMappings")

            return {
                "success": True,
                "message": "Mappings saved to Inventor file"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to save custom properties: {str(e)}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "errorType": type(e).__name__
        }
    finally:
        pythoncom.CoUninitialize()