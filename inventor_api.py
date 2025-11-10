# inventor_api.py
import pythoncom
import win32com.client

def get_fx_parameters():
    # Initialize COM for this thread
    pythoncom.CoInitialize()
    try:
        app = win32com.client.GetActiveObject("Inventor.Application")
        doc = app.ActiveDocument

        # Optional: verify document type (kPartDocumentObject = 12291)
        if doc.DocumentType not in (12291, 12292):  # Part or Assembly
            return {"error": "Active document is not a part or assembly"}

        params = doc.ComponentDefinition.Parameters
        result = {}
        for param in params:
            result[param.Name] = {
                "value": param.Value,
                "unit": param.Units or "unitless",
                "expression": param.Expression,
            }
        return result

    except Exception as e:
        return {"error": str(e)}
    finally:
        # Uninitialize COM to avoid resource leaks
        pythoncom.CoUninitialize()