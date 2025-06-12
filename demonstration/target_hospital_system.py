from fastapi import FastAPI, Request
import json
from typing import Dict, Any

app = FastAPI(
    title="Target Hospital EMR",
    description="A mock system that receives FHIR Patient data."
)

@app.post("/fhir/patient")
async def receive_patient_data(request: Request):
    """
    Receives a FHIR Patient resource and prints it to the console.
    """
    fhir_data = await request.json()
    
    print("\n--- Target Hospital System ---")
    print("Received a new FHIR Patient resource!")
    print(json.dumps(fhir_data, indent=2))
    
    patient_name = fhir_data.get("name", [{}])[0]
    family_name = patient_name.get("family", "N/A")
    given_name = patient_name.get("given", ["N/A"])[0]
    
    return {
        "status": "success",
        "message": f"Patient data for {given_name} {family_name} successfully received and processed."
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Target Hospital System on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001) 