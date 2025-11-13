# inventor_api.py (Enhanced)
import pythoncom
import win32com.client
from typing import Dict, Any, Optional


def parse_comment_mapping(comment: str) -> Dict[str, Optional[str]]:
    """
    Parse Inventor parameter Comment field for CalcsLive mapping.

    Format: "#AC:symbol #Note:{{user text}}"

    Args:
        comment: Parameter comment string

    Returns:
        Dict with 'mapping' and 'note' keys
        Example: {"mapping": "flow_rate", "note": "Main pump flow"}
    """
    result = {"mapping": None, "note": None}

    if not comment:
        return result

    parts = comment.split()
    for part in parts:
        if part.startswith('#AC:'):
            result["mapping"] = part[4:]  # Extract symbol after #AC:
        elif part.startswith('#Note:'):
            # Extract note text, removing {{ and }}
            note_text = part[6:]  # Remove #Note: prefix
            result["note"] = note_text.strip('{}')

    return result


def build_comment_string(symbol: Optional[str], note: Optional[str]) -> str:
    """
    Build Comment field string with mapping and optional note.

    Args:
        symbol: CalcsLive PQ symbol (e.g., "flow_rate")
        note: Optional user note text

    Returns:
        Formatted comment string
        Example: "#AC:flow_rate #Note:{{Main pump flow rate}}"
    """
    parts = []

    if symbol:
        parts.append(f"#AC:{symbol}")

    if note:
        # Clean note text and wrap in {{ }}
        clean_note = note.replace('{{', '').replace('}}', '').strip()
        if clean_note:
            parts.append(f"#Note:{{{{{clean_note}}}}}")

    return ' '.join(parts)


def get_user_parameters() -> Dict[str, Any]:
    """
    Get User Parameters ONLY from active Inventor document.
    Works for Parts and Assemblies - treats them the same (single component approach).
    Includes Comment field parsing for CalcsLive mappings.

    IMPORTANT: Values are in Inventor internal units (cm-based).
    Dashboard must handle conversion to/from SI units using dimensional analysis.

    Returns:
        Dict with user parameters array or error message

    Example return:
        {
            "success": True,
            "documentName": "beam_calc.ipt",
            "parameters": [
                {
                    "name": "Length",
                    "value": 500.0,  # Inventor internal units (cm)
                    "unit": "mm",    # User's display unit
                    "expression": "",
                    "comment": "#AC:L #Note:{{Main beam length}}",
                    "mapping": "L",
                    "note": "Main beam length",
                    "isReadOnly": False
                }
            ]
        }

    Note: Dashboard handles unit conversion using CalcsLive units API:
        - Query /api/units/dimension?unit={unit} for dimensional data
        - Convert: inventor_cm_value / (100^L) = si_m_value
        - Where L is the length dimension power from dimensional analysis
    """
    pythoncom.CoInitialize()
    try:
        # Connect to running Inventor instance
        app = win32com.client.GetActiveObject("Inventor.Application")
        doc = app.ActiveDocument

        # Verify document exists
        if doc is None:
            return {"success": False, "error": "No active Inventor document"}

        # Check if ComponentDefinition exists (works for Parts and Assemblies)
        if not hasattr(doc, 'ComponentDefinition'):
            return {
                "success": False,
                "error": "Document does not have ComponentDefinition"
            }

        # Get User Parameters ONLY (not all Parameters)
        user_params = doc.ComponentDefinition.Parameters.UserParameters
        result = []

        for param in user_params:
            try:
                # Safely access parameter properties
                param_name = param.Name if hasattr(param, 'Name') else str(param)
                param_value = param.Value if hasattr(param, 'Value') else 0
                param_unit = param.Units if (hasattr(param, 'Units') and param.Units) else ""
                param_expression = param.Expression if hasattr(param, 'Expression') else ""
                param_comment = param.Comment if hasattr(param, 'Comment') else ""

                # Get internal unit and display value using Inventor's API
                internal_unit = ""
                display_value = None

                try:
                    # Get internal/database unit from expression using Inventor's API
                    # This tells us what unit Inventor uses internally (e.g., "cm", "g", "rad")
                    if param_expression and param_unit:
                        internal_unit = doc.UnitsOfMeasure.GetDatabaseUnitsFromExpression(
                            param_expression,
                            param_unit
                        )
                    elif param_unit:
                        # For parameters without expression, infer from unit
                        # Use empty expression to get default database unit for this unit type
                        internal_unit = doc.UnitsOfMeasure.GetDatabaseUnitsFromExpression(
                            "",
                            param_unit
                        )
                except Exception as unit_error:
                    print(f"WARNING: Could not get internal unit for '{param_name}': {unit_error}")
                    internal_unit = ""

                # Get display value using Inventor's unit conversion
                if internal_unit and param_unit and param_value is not None:
                    try:
                        # Convert from internal unit to display unit
                        display_value = doc.UnitsOfMeasure.ConvertUnits(
                            param_value,  # Internal/database value
                            internal_unit,  # From internal unit (e.g., "cm", "g", "rad")
                            param_unit  # To display unit (e.g., "mm", "kg", "deg")
                        )
                    except Exception as conv_error:
                        # Conversion failed - use raw value as fallback
                        display_value = param_value
                        print(f"WARNING: Unit conversion failed for '{param_name}': {conv_error}")
                else:
                    # No units or missing info - use raw value
                    display_value = param_value

                # Parse Comment field for mapping
                comment_data = parse_comment_mapping(param_comment)

                result.append({
                    "name": param_name,
                    "value": param_value,  # Inventor internal/database units
                    "displayValue": display_value,  # Value in display unit (from Inventor)
                    "unit": param_unit,  # Display unit (e.g., "mm", "in")
                    "internalUnit": internal_unit,  # Internal unit (empty - inferred by dashboard)
                    "expression": param_expression,
                    "comment": param_comment,
                    "mapping": comment_data["mapping"],
                    "note": comment_data["note"]
                })

            except Exception as param_error:
                # If we can't read this parameter, skip it and log
                print(f"WARNING: Could not read parameter '{param_name}': {param_error}")
                continue

        return {
            "success": True,
            "documentName": doc.DisplayName,  # User-friendly metadata
            "parameters": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "errorType": type(e).__name__
        }
    finally:
        pythoncom.CoUninitialize()


# Backward compatibility alias
def get_fx_parameters() -> Dict[str, Any]:
    """
    Backward compatibility wrapper for get_user_parameters().

    DEPRECATED: Use get_user_parameters() instead.
    This now returns User Parameters only (not all parameters).
    """
    return get_user_parameters()


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


def update_parameter_mapping(name: str, symbol: Optional[str] = None, note: Optional[str] = None,
                            value: Optional[float] = None, unit: Optional[str] = None) -> Dict[str, Any]:
    """
    Update User Parameter's Comment field with CalcsLive mapping.
    Optionally also update the parameter's value.

    Args:
        name: Parameter name (e.g., "Length", "Width")
        symbol: CalcsLive PQ symbol to map to (e.g., "L", "flow_rate")
        note: Optional user note text
        value: Optional new value to set
        unit: Optional unit for the new value

    Returns:
        Dict with success status or error message

    Example:
        update_parameter_mapping("Length", symbol="L", note="Main beam length", value=5.0, unit="m")
    """
    pythoncom.CoInitialize()
    try:
        app = win32com.client.GetActiveObject("Inventor.Application")
        doc = app.ActiveDocument

        if doc is None:
            return {"success": False, "error": "No active Inventor document"}

        # Access User Parameters
        user_params = doc.ComponentDefinition.Parameters.UserParameters

        # Find parameter by name
        try:
            param = user_params.Item(name)
        except:
            return {"success": False, "error": f"User Parameter '{name}' not found"}

        # Update Comment field with mapping
        new_comment = build_comment_string(symbol, note)
        param.Comment = new_comment

        # Optionally update value (AC3D Bridge pattern: direct value assignment)
        # IMPORTANT: value must already be in Inventor's internal units (cm-based)
        # Dashboard handles unit conversion before sending the value
        if value is not None:
            try:
                # Direct value assignment - Inventor handles the rest
                param.Value = value
            except Exception as e:
                # Value update failed (parameter might have formula/constraints)
                # But Comment was updated successfully
                return {
                    "success": False,
                    "error": f"Failed to update value: {str(e)}",
                    "comment": new_comment,
                    "parameter": name,
                    "mapping": symbol,
                    "note": note
                }

        return {
            "success": True,
            "parameter": name,
            "comment": param.Comment,
            "mapping": symbol,
            "note": note,
            "value": param.Value,
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