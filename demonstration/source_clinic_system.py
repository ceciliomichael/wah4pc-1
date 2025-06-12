import requests
import json

# The endpoint of our main interoperability application
INTEROP_API_URL = "http://localhost:8000/api/translate"

# Sample patient data in a simplified, proprietary "HL7-like" format
sample_patient_data = {
    "patientId": "C456",
    "firstName": "Maria",
    "lastName": "Santos",
    "dateOfBirth": "19920315"
}

def send_patient_data():
    """
    Sends a patient record to the interoperability service for translation.
    """
    print("--- Source Clinic System ---")
    print(f"Sending patient data for {sample_patient_data['firstName']} {sample_patient_data['lastName']}...")
    
    payload = {
        "source_format": "hl7",
        "target_format": "fhir",
        "data": sample_patient_data
    }
    
    try:
        response = requests.post(INTEROP_API_URL, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        
        print("Translation request successful!")
        print("Response from Interoperability Service:")
        print(json.dumps(response_data, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to the Interoperability Service. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    send_patient_data() 