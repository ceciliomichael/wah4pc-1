from fhir.resources.patient import Patient
from pydantic import ValidationError
import json

def validate_fhir_patient(fhir_data: dict) -> bool:  
    """  
    Validates the structure of a FHIR Patient resource using fhir.resources.
    Returns True if valid, False otherwise.  
    """  
    print("\n[VALIDATION] Starting FHIR Patient resource validation...")
    
    try:  
        print("[VALIDATION] Checking resource type...")
        if fhir_data.get("resourceType") != "Patient":
            print(f"[VALIDATION FAILED] Invalid resourceType: {fhir_data.get('resourceType')}")
            return False
        print("[VALIDATION] ✓ Resource type is valid: 'Patient'")
        
        print("[VALIDATION] Checking required fields...")
        # Check identifier
        identifiers = fhir_data.get("identifier", [])
        if not identifiers:
            print("[VALIDATION FAILED] Missing required field: identifier")
            return False
        print(f"[VALIDATION] ✓ Has {len(identifiers)} identifier(s)")
        
        # Check name
        names = fhir_data.get("name", [])
        if not names:
            print("[VALIDATION FAILED] Missing required field: name")
            return False
        
        has_family = False
        for name in names:
            if name.get("family"):
                has_family = True
                break
        
        if not has_family:
            print("[VALIDATION FAILED] Missing required field: name.family")
            return False
        print(f"[VALIDATION] ✓ Has valid name structure with family name")
        
        print("[VALIDATION] Parsing with FHIR resources library...")
        # The Patient model from fhir.resources will parse and validate the dictionary.
        # It raises a ValidationError if the data is not compliant.
        Patient(**fhir_data)
        print("[VALIDATION] ✓ Successfully parsed with FHIR resources library")
        
        print("[VALIDATION] All validation checks passed!")
        return True  
    except ValidationError as e:  
        print(f"[VALIDATION FAILED] FHIR validation error: {e}")
        return False
    except (AssertionError, KeyError, IndexError) as e:
        print(f"[VALIDATION FAILED] Data structure error: {e}")
        return False 