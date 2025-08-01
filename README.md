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

This project is organized into several key directories and files, providing a clear separation of concerns for the core interoperability service, demonstration systems, and web-based applications.

```
/wah4pc-1/
│
├── app/                      # Core Healthcare Interoperability Service
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application entry point
│   ├── models.py             # Pydantic models for API data structures
│   └── services/             # Contains business logic services
│       ├── __init__.py
│       ├── ai_service.py     # Logic for communicating with the AI model
│       ├── translation_tools.py # The actual data translation functions (tools)
│       └── validation_service.py # Logic for validating translated data
│
├── demonstration/            # Contains simple CLI-based demonstration scripts
│   ├── source_clinic_system.py # Simulates a clinic sending data
│   └── target_hospital_system.py # Simulates a hospital receiving data
│
├── web4clinics/              # Web-based Clinic EMR System (Frontend + Backend)
│   ├── package.json          # Node.js dependencies and scripts
│   ├── server.js             # Express.js server for the clinic application
│   ├── public/               # Frontend assets (HTML, CSS, JS)
│   │   ├── app.js
│   │   ├── index.html
│   │   └── styles.css
│   └── wah4clinics/          # Data storage for the clinic app
│       ├── patients.json
│       └── sent_records.json
│
├── web4hospitals/            # Web-based Hospital EMR System (Frontend + Backend)
│   ├── package.json          # Node.js dependencies and scripts
│   ├── server.js             # Express.js server for the hospital application
│   ├── public/               # Frontend assets (HTML, CSS, JS)
│   │   ├── css/styles.css
│   │   ├── index.html
│   │   └── js/app.js
│   └── data/                 # Data storage for the hospital app
│       ├── pending_queue.json
│       └── received_patients.json
│
├── facility_registry.json    # Global registry of healthcare facilities (used by web apps)
├── requirements.txt          # Python dependencies for the core service
├── README.md                 # Project overview and documentation
└── .env.example              # Example environment variables for AI service configuration (if applicable)
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

## Web-Based Demonstration

For a more comprehensive and interactive demonstration, web-based applications for both the clinic and hospital are available. These provide a modern, user-friendly interface for simulating the healthcare workflow.

### Folder Structure

- `web4clinics/` - A web-based source clinic system (Sunshine Clinic EMR).
- `web4hospitals/` - A web-based target hospital system (Memorial Hospital EMR).
- `app/` - The core interoperability service.

### Prerequisites

- Node.js (v14 or higher)
- npm (which comes with Node.js)
- Python 3.9+ and `pip`

### Setup

1.  **Install Python Dependencies**:
    From the project root, install the required packages for the core interoperability service.
    ```bash
    pip install -r requirements.txt
    ```

2.  **Install Clinic App Dependencies**:
    Navigate to the `web4clinics` directory and install the Node.js packages.
    ```bash
    cd web4clinics
    npm install
    cd ..
    ```

3.  **Install Hospital App Dependencies**:
    Navigate to the `web4hospitals` directory and install the Node.js packages.
    ```bash
    cd web4hospitals
    npm install
    cd ..
    ```

### Running the Demonstration

You will need **three separate terminal windows** running from the project's root directory.

**Terminal 1: Start the Hospital System (Port 8001)**
This starts the web server for the Memorial Hospital EMR.
```bash
cd web4hospitals
npm start
```
- Access it at: `http://localhost:8001`

**Terminal 2: Start the Interoperability Service (Port 8000)**
This starts the core Python-based translation service.
```bash
uvicorn app.main:app --reload
```

**Terminal 3: Start the Clinic System (Port 3000)**
This starts the web server for the Sunshine Clinic EMR.
```bash
cd web4clinics
npm start
```
- Access it at: `http://localhost:3000`

### Workflow Example

1.  **Open the Clinic App** (`http://localhost:3000`):
    - Navigate to the "Patients" tab to see existing patient records.
    - Go to the "Send Records" tab.
    - Select a patient and a target hospital from the dropdowns, then click "Send Patient Record."
    - You will receive a success notification, and the record will appear in the "Sent Records" table.

2.  **Observe the Interoperability Service** (Terminal 2):
    - Logs will appear showing that the data was received, translated from the clinic's format to FHIR, validated, and successfully routed to the hospital system.

3.  **Open the Hospital App** (`http://localhost:8001`):
    - The "Pending Records" card on the dashboard will show a new incoming record.
    - Click "Process Pending Records" to move the record from the queue into the main hospital database.
    - Navigate to the "Patients" tab to view the complete, translated patient record now stored in the hospital's system. 