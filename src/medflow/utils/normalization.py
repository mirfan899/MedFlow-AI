def normalize_soap(soap_note: dict):
    """
    Normalize SOAP keys from model output to internal schema.
    Accepts:
    - S / O / A
    - subjective / objective / assessment
    """
    return {
        "subjective": soap_note.get("subjective") or soap_note.get("S") or {},
        "objective": soap_note.get("objective") or soap_note.get("O") or {},
        "assessment": soap_note.get("assessment") or soap_note.get("A") or {}
    }
