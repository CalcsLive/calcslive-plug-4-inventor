# inventor_api.py (Enhanced)
import pythoncom
import win32com.client
from typing import Dict, Any, Optional


def parse_comment_mapping(comment: str) -> Dict[str, Optional[str]]:
    """
    Parse Inventor parameter Comment field for CalcsLive mapping.

    New Format: "CA0:symbol #note text" or "CA0:symbol"
    - Namespace: CA0, CA1, etc. (required)
    - Symbol: MathJS-compatible symbol (required)
    - Note: Optional text after # (can contain # if wrapped in backticks)

    Examples:
        "CA0:L" → {"mapping": "L", "note": None}
        "CA0:L #Length parameter" → {"mapping": "L", "note": "Length parameter"}
        "CA0:L #`Length #1` #`Design #3`" → {"mapping": "L", "note": "`Length #1` #`Design #3`"}

    Args:
        comment: Parameter comment string

    Returns:
        Dict with 'mapping' and 'note' keys
        Example: {"mapping": "L", "note": "Length parameter"}
    """
    result = {"mapping": None, "note": None}

    if not comment or not comment.strip():
        return result

    comment = comment.strip()

    # Split on first # to separate namespace:symbol from note
    if '#' in comment:
        mapping_part, note_part = comment.split('#', 1)  # maxsplit=1 preserves # in notes
        result["note"] = note_part.strip() if note_part.strip() else None
    else:
        mapping_part = comment
        result["note"] = None

    # Parse namespace:symbol
    mapping_part = mapping_part.strip()
    if ':' not in mapping_part:
        return {"mapping": None, "note": None}  # Invalid: no namespace

    namespace, symbol = mapping_part.split(':', 1)
    namespace = namespace.strip()
    symbol = symbol.strip()

    # Validate namespace (must be CA followed by digit(s))
    if not namespace.startswith('CA') or len(namespace) < 3:
        return {"mapping": None, "note": None}

    # Validate namespace has digit after CA
    try:
        int(namespace[2:])  # Check CA0, CA1, etc.
    except ValueError:
        return {"mapping": None, "note": None}

    # Validate symbol (non-empty, no colons - MathJS compatibility)
    if not symbol or ':' in symbol:
        return {"mapping": None, "note": None}

    result["mapping"] = symbol

    return result


def build_comment_string(symbol: Optional[str], note: Optional[str], namespace: str = "CA0") -> str:
    """
    Build Comment field string with mapping and optional note.

    New Format: "CA0:symbol #note text" or "CA0:symbol"

    Args:
        symbol: CalcsLive PQ symbol (e.g., "L", "rho", "η")
        note: Optional user note text (preserved as-is)
        namespace: Namespace prefix (default: "CA0")

    Returns:
        Formatted comment string
        Examples:
            build_comment_string("L", None) → "CA0:L"
            build_comment_string("L", "Length parameter") → "CA0:L #Length parameter"
            build_comment_string("L", "`Length #1` #`Design #3`") → "CA0:L #`Length #1` #`Design #3`"
    """
    if not symbol:
        return ""

    # Build namespace:symbol part
    comment = f"{namespace}:{symbol}"

    # Append note if provided (preserve as-is, including any # or backticks)
    if note and note.strip():
        comment = f"{comment} #{note.strip()}"

    return comment


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


def create_user_parameter(name: str, value: str = "", comment: str = "", unit: str = "Text") -> Dict[str, Any]:
    """
    Create a new User Parameter in active Inventor document.

    Args:
        name: Parameter name (e.g., "ArticleId", "Description")
        value: Initial value (default: empty string for text parameters)
        comment: Comment/note for the parameter (e.g., "eg: 3MAV4GNFQ-3FU, taken from the calculation article url")
        unit: Unit type (default: "Text" for text parameters, or "cm", "mm", etc. for numeric)

    Returns:
        Dict with success status or error message

    Example:
        create_user_parameter(
            "ArticleId",
            "3MAV4GNFQ-3FU",
            "eg: 3MAV4GNFQ-3FU, taken from the calculation article url",
            "Text"
        )
    """
    pythoncom.CoInitialize()
    try:
        app = win32com.client.GetActiveObject("Inventor.Application")
        doc = app.ActiveDocument

        if doc is None:
            return {"success": False, "error": "No active Inventor document"}

        # Access User Parameters collection
        user_params = doc.ComponentDefinition.Parameters.UserParameters

        # Check if parameter already exists
        try:
            existing_param = user_params.Item(name)
            return {
                "success": False,
                "error": f"User Parameter '{name}' already exists",
                "parameterExists": True,
                "existingValue": existing_param.Expression,
                "existingUnit": existing_param.Units,
                "existingComment": existing_param.Comment
            }
        except:
            # Parameter doesn't exist - good, we can create it
            pass

        # Create new User Parameter
        try:
            if unit.lower() == "text" or unit == "":
                # Text parameter - use AddByValue with kTextUnits enum
                # Inventor API documentation: kTextUnits = 11346 (Text/String type)
                new_param = user_params.AddByValue(name, value or "", 11346)
            else:
                # Numeric parameter with units - use AddByExpression
                expression = f"{value} {unit}" if value else f"0 {unit}"
                new_param = user_params.AddByExpression(name, expression, unit)

            # Set comment if provided
            if comment:
                new_param.Comment = comment

            return {
                "success": True,
                "parameter": name,
                "value": new_param.Expression,
                "unit": new_param.Units,
                "comment": new_param.Comment,
                "message": f"User Parameter '{name}' created successfully"
            }

        except Exception as create_error:
            error_code = getattr(create_error, 'hresult', None)
            return {
                "success": False,
                "error": f"Failed to create parameter: {str(create_error)}",
                "errorType": type(create_error).__name__,
                "errorCode": error_code,
                "details": "Check parameter name validity and Inventor document state"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "errorType": type(e).__name__
        }
    finally:
        pythoncom.CoUninitialize()