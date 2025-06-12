# Healthcare Interoperability System

A Python-based middleware service that translates healthcare data formats using a local AI model.

## System Overview

This system functions as a middleware service, receiving healthcare data in one format, using a local AI model to translate it, validating the output, and routing it to a target system.

## Technology Stack

* **Language:** Python 3.9+  
* **Web Framework:** FastAPI (for creating a high-performance API)  
* **Data Validation:** Pydantic (integrated with FastAPI for request/response models)  
* **HTTP Client:** httpx (for making asynchronous requests to the AI service)  
* **FHIR Validation:** fhirpy (for structural validation of FHIR resources)  
* **Dependency Management:** pip with a requirements.txt file

## Project Structure

```
/interoperability_system/  
│  
├── .env                  # Environment variables (API keys, endpoints)  
├── requirements.txt      # Project dependencies  
│  
└── app/  
    │  
    ├── __init__.py  
    ├── main.py             # FastAPI application entry point  
    ├── models.py           # Pydantic models for API data structures  
    │  
    └── services/  
        ├── __init__.py  
        ├── ai_service.py       # Logic for communicating with the AI model  
        ├── translation_tools.py# The actual translation functions (tools)  
        └── validation_service.py # Logic for validating translated data
```

## Setup and Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```
3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Configure the .env file with your AI service details:
   ```
   AI_API_ENDPOINT="http://localhost:1234/v1/chat/completions"
   AI_API_KEY="your_api_key"
   AI_MODEL_NAME="your_model_name"
   ```

## Running the Application

Start the FastAPI server:
```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

### POST /api/translate

Translates healthcare data from one format to another.

**Request Body:**
```json
{
  "source_format": "hl7",
  "target_format": "fhir",
  "data": {
    "patientId": "C123",
    "firstName": "Juan",
    "lastName": "Dela Cruz",
    "dateOfBirth": "19800101"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "translated_data": {
    "resourceType": "Patient",
    "identifier": [
      {
        "system": "urn:clinic:patient-id",
        "value": "C123"
      }
    ],
    "name": [
      {
        "family": "Dela Cruz",
        "given": [
          "Juan"
        ]
      }
    ],
    "birthDate": "1980-01-01"
  }
}
```

## Documentation

API documentation is automatically generated and available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## End-to-End Demonstration

To see the full system in action, you can run the included mock source and target systems. This simulates a real-world scenario where a clinic sends data to a hospital.

### How to Run the Demonstration

You will need **three separate terminal windows**.

**Terminal 1: Start the Target Hospital System**
This server will run on port `8001` and wait to receive the final, translated data.
```bash
python demonstration/target_hospital_system.py
```

**Terminal 2: Start the Main Interoperability Service**
This is our core application that performs the translation. It runs on port `8000`.
```bash
uvicorn app.main:app --reload
```

**Terminal 3: Run the Source Clinic System**
This script will send a sample patient record to the main service, starting the process.
```bash
# Make sure your dependencies are up to date
pip install -r requirements.txt

# Run the script
python demonstration/source_clinic_system.py
```

### Expected Outcome

1.  The **Source System** (Terminal 3) will send data and print the success response from the Interoperability Service.
2.  The **Interoperability Service** (Terminal 2) will show logs of the translation, validation, and successful routing to the target.
3.  The **Target System** (Terminal 1) will print the final, translated FHIR resource to the console, confirming it received the data.

## CLI-Based Demonstration Systems

For a more comprehensive demonstration, interactive CLI-based systems have been created for both the clinic and hospital sides. These systems provide a more realistic simulation of healthcare systems using the interoperability service.

### Folder Structure

- `wah4clinics/` - Source clinic system with patient management
- `wah4hospital/` - Target hospital system that receives translated FHIR data
- `app/` - The core interoperability service

### Setup

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Demonstration

You'll need **three separate terminal windows**:

**Terminal 1: Start the Hospital System**
```bash
python wah4hospital/hospital_system.py
```
This starts both the hospital CLI interface and its API server on port 8001.

**Terminal 2: Start the Interoperability Service**
```bash
uvicorn app.main:app --reload
```
This starts the translation service on port 8000.

**Terminal 3: Start the Clinic System**
```bash
python wah4clinics/clinic_system.py
```
This starts the clinic CLI interface.

### Using the Systems

**Clinic System Features:**
- View all patients in the clinic database
- Add new patients
- Send patient records to the hospital through the interoperability service
- Track records that have been sent

**Hospital System Features:**
- Automatically receives translated FHIR resources
- View all patients in the hospital database
- Check pending records awaiting processing
- Process and acknowledge pending records
- Search for patients by ID or name

### Workflow Example

1. In the Clinic System:
   - Select "View All Patients" to see available records
   - Select "Send Patient Record to Hospital" and choose a patient
   
2. The Interoperability Service:
   - Receives the clinic's data format
   - Translates it to FHIR format using the AI service
   - Validates the FHIR structure
   - Forwards it to the hospital system
   
3. In the Hospital System:
   - Select "Check Pending Records" to see the incoming data
   - Select "Process Pending Records" to acknowledge and store them
   - Select "View All Patients" to see the processed records 