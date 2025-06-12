import json

def translate_hl7_v2_json_to_fhir_r4(hl7_data: dict) -> dict:  
    """  
    Translates a simplified HL7-like JSON dictionary to a FHIR R4 Patient resource.  
    This is a specific "tool" the AI can be instructed to use.
    """  
    try:
        print("\n[TRANSLATION] Executing: translate_hl7_v2_json_to_fhir_r4")
        print("[TRANSLATION] Source data:")
        print(json.dumps(hl7_data, indent=2))
        
        # Mapping logic
        fhir_patient = {  
            "resourceType": "Patient",  
            "identifier": [{  
                "system": "urn:clinic:patient-id",  
                "value": hl7_data.get("patientId")  
            }],  
            "name": [{  
                "family": hl7_data.get("lastName"),  
                "given": [hl7_data.get("firstName")]  
            }],
        }
        
        # Map gender - required for FHIR R4
        gender = hl7_data.get("gender", "").lower()
        if gender in ["male", "female", "other", "unknown"]:
            fhir_patient["gender"] = gender
        else:
            fhir_patient["gender"] = "unknown"
            
        # Format date of birth
        dob = hl7_data.get("dateOfBirth", "")
        if len(dob) == 8:
            fhir_patient["birthDate"] = f"{dob[0:4]}-{dob[4:6]}-{dob[6:8]}"
        
        # Add address if available
        if hl7_data.get("address"):
            fhir_patient["address"] = [{
                "text": hl7_data.get("address")
            }]
            
        # Add telecom if available
        if hl7_data.get("phoneNumber"):
            fhir_patient["telecom"] = [{
                "system": "phone",
                "value": hl7_data.get("phoneNumber")
            }]
            
        print("\n[TRANSLATION] Generated FHIR Patient resource:")
        print(json.dumps(fhir_patient, indent=2))
        
        return fhir_patient  
    except (KeyError, IndexError) as e:  
        print(f"[ERROR] Missing or malformed HL7 data: {e}")
        raise ValueError(f"Missing or malformed HL7 data: {e}")

def translate_custom_clinic_format_v1_to_fhir_r4(custom_data: dict) -> dict:
    """
    Translates a proprietary "Custom Clinic V1" format to a FHIR R4 Patient resource.
    This is another specific "tool" the AI can use, demonstrating flexibility.
    """
    try:
        print("\n[TRANSLATION] Executing: translate_custom_clinic_format_v1_to_fhir_r4")
        print("[TRANSLATION] Source data:")
        print(json.dumps(custom_data, indent=2))
        
        # Mapping logic for a different source format
        name_parts = custom_data.get("fullName", "").split(" ", 1)
        
        fhir_patient = {
            "resourceType": "Patient",
            "identifier": [{
                "system": "urn:custom:clinic-id",
                "value": custom_data.get("clinicId")
            }],
            "name": [{
                "family": name_parts[1] if len(name_parts) > 1 else "",
                "given": [name_parts[0]]
            }],
            "telecom": [{
                "system": "phone",
                "value": custom_data.get("contactNumber")
            }]
        }

        # Map gender
        gender = custom_data.get("sex", "").lower()
        if gender in ["male", "female", "other", "unknown"]:
            fhir_patient["gender"] = gender
        elif gender in ["m", "male", "man"]:
            fhir_patient["gender"] = "male"
        elif gender in ["f", "female", "woman"]:
            fhir_patient["gender"] = "female"
        else:
            fhir_patient["gender"] = "unknown"

        # Date format might be different, e.g., "YYYY/MM/DD"
        dob = custom_data.get("birthdate", "")
        if len(dob) == 10 and dob[4] == '/' and dob[7] == '/':
            fhir_patient["birthDate"] = dob.replace("/", "-")
            
        print("\n[TRANSLATION] Generated FHIR Patient resource:")
        print(json.dumps(fhir_patient, indent=2))
            
        return fhir_patient
    except (KeyError, IndexError) as e:
        print(f"[ERROR] Missing or malformed Custom Clinic V1 data: {e}")
        raise ValueError(f"Missing or malformed Custom Clinic V1 data: {e}")

# In the future, you could add more tools here  
# def convert_cda_to_fhir(cda_data: dict) -> dict:  
#     ... 