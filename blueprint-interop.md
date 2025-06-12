### 1\. System Overview

This document outlines the technical blueprint for a Python-based Interoperability System. The system will function as a middleware service, receiving healthcare data in one format, using a local AI model to translate it, validating the output, and routing it to a target system.

### 2\. Technology Stack

* **Language:** Python 3.9+  
* **Web Framework:** FastAPI (for creating a high-performance API)  
* **Data Validation:** Pydantic (integrated with FastAPI for request/response models)  
* **HTTP Client:** httpx (for making asynchronous requests to the AI service)  
* **FHIR Validation:** fhirpy (for structural validation of FHIR resources)  
* **Dependency Management:** pip with a requirements.txt file

### 3\. Project Structure

A clear and modular project structure is essential for maintainability.

/interoperability\_system/  
│  
├── .env                  \# Environment variables (API keys, endpoints)  
├── requirements.txt      \# Project dependencies  
│  
└── app/  
    │  
    ├── \_\_init\_\_.py  
    ├── main.py             \# FastAPI application entry point  
    ├── models.py           \# Pydantic models for API data structures  
    │  
    └── services/  
        ├── \_\_init\_\_.py  
        ├── ai\_service.py       \# Logic for communicating with the AI model  
        ├── translation\_tools.py\# The actual translation functions (tools)  
        └── validation\_service.py \# Logic for validating translated data

### 4\. Environment Configuration (.env)

Sensitive information and configurations should be stored in a .env file and loaded by the application.

\# .env

\# AI Service Configuration  
AI\_API\_ENDPOINT="http://localhost:1234/v1/chat/completions"  
AI\_API\_KEY="12345"  
AI\_MODEL\_NAME="localmodel123"

### 5\. Core Components \- Detailed Breakdown

#### a. API Models (app/models.py)

Using Pydantic, we define the expected structure of our API requests and responses.

\# app/models.py  
from pydantic import BaseModel, Field  
from typing import Dict, Any

class TranslationRequest(BaseModel):  
    source\_format: str \= Field(..., example="hl7")  
    target\_format: str \= Field(..., example="fhir")  
    data: Dict\[str, Any\] \= Field(..., example={"patientId": "C123", "lastName": "Dela Cruz"})

class TranslationResponse(BaseModel):  
    status: str  
    translated\_data: Dict\[str, Any\] | None \= None  
    error\_message: str | None \= None

#### b. Translation Tools (app/services/translation\_tools.py)

This module contains the actual Python functions that the AI will be instructed to use.

\# app/services/translation\_tools.py

def convert\_hl7\_to\_fhir(hl7\_data: dict) \-\> dict:  
    """  
    Translates a simplified HL7-like dictionary to a FHIR Patient resource.  
    This is the "tool" the AI will execute.  
    """  
    try:  
        \# Mapping logic  
        fhir\_patient \= {  
            "resourceType": "Patient",  
            "identifier": \[{  
                "system": "urn:clinic:patient-id",  
                "value": hl7\_data.get("patientId")  
            }\],  
            "name": \[{  
                "family": hl7\_data.get("lastName"),  
                "given": \[hl7\_data.get("firstName")\]  
            }\],  
            \# Date format conversion  
            "birthDate": f"{hl7\_data\['dateOfBirth'\]\[0:4\]}-{hl7\_data\['dateOfBirth'\]\[4:6\]}-{hl7\_data\['dateOfBirth'\]\[6:8\]}"  
        }  
        return fhir\_patient  
    except (KeyError, IndexError) as e:  
        \# Handle cases where HL7 data is malformed  
        raise ValueError(f"Missing or malformed HL7 data: {e}")

\# In the future, you could add more tools here  
\# def convert\_cda\_to\_fhir(cda\_data: dict) \-\> dict:  
\#     ...

#### c. AI Service (app/services/ai\_service.py)

This service handles all communication with the local AI model.

\# app/services/ai\_service.py  
import os  
import httpx  
from typing import Dict, Any

\# Load from environment  
AI\_ENDPOINT \= os.getenv("AI\_API\_ENDPOINT")  
AI\_KEY \= os.getenv("AI\_API\_KEY")  
AI\_MODEL \= os.getenv("AI\_MODEL\_NAME")

async def get\_ai\_translation\_instruction(source\_data: Dict\[str, Any\]) \-\> Dict\[str, Any\]:  
    """  
    Calls the AI model to get instructions on which tool to use.  
    """  
    \# The prompt instructs the AI to use a specific tool  
    prompt \= f"""  
    You are a system controller. Your task is to determine the correct function to call  
    to translate the following data packet into a FHIR Patient resource.  
      
    Data:  
    {source\_data}  
      
    Based on the data, call the 'convert\_hl7\_to\_fhir' function.  
    """

    \# The tool definition is sent along with the prompt  
    tool\_definition \= {  
        "type": "function",  
        "function": {  
            "name": "convert\_hl7\_to\_fhir",  
            "description": "Translates a simplified HL7-like dictionary to a FHIR Patient resource.",  
            "parameters": {  
                "type": "object",  
                "properties": {  
                    "hl7\_data": {  
                        "type": "object",  
                        "description": "The HL7-like data object."  
                    }  
                },  
                "required": \["hl7\_data"\]  
            }  
        }  
    }  
      
    headers \= {  
        "Authorization": f"Bearer {AI\_KEY}",  
        "Content-Type": "application/json"  
    }  
      
    payload \= {  
        "model": AI\_MODEL,  
        "messages": \[{"role": "user", "content": prompt}\],  
        "tools": \[tool\_definition\],  
        "tool\_choice": "auto"  
    }

    async with httpx.AsyncClient() as client:  
        response \= await client.post(AI\_ENDPOINT, json=payload, headers=headers, timeout=30.0)  
        response.raise\_for\_status() \# Raise an exception for bad status codes  
          
        \# We expect the AI to respond with a tool\_calls object  
        return response.json()

#### d. Validation Service (app/services/validation\_service.py)

This service uses fhirpy to validate the structure of the translated FHIR data.

\# app/services/validation\_service.py  
from fhirpy.base.resource import Resource

def validate\_fhir\_patient(fhir\_data: dict) \-\> bool:  
    """  
    Validates the structure of a FHIR Patient resource.  
    Returns True if valid, False otherwise.  
    """  
    try:  
        \# fhirpy can validate a resource by attempting to create it.  
        \# It will raise an exception if the structure is invalid.  
        Patient \= Resource.from\_data(fhir\_data)  
        \# Add more specific checks if needed  
        assert Patient.resource\_type \== "Patient"  
        assert Patient.name\[0\].family is not None  
        return True  
    except Exception:  
        return False

#### e. Main Application (app/main.py)

This file ties everything together.

\# app/main.py  
from fastapi import FastAPI, HTTPException  
from dotenv import load\_dotenv

\# Load environment variables from .env file  
load\_dotenv()

from .models import TranslationRequest, TranslationResponse  
from .services import ai\_service, translation\_tools, validation\_service

app \= FastAPI(  
    title="Healthcare Interoperability System",  
    description="Translates healthcare data formats using an AI agent."  
)

\# A mapping of tool names to the actual Python functions  
AVAILABLE\_TOOLS \= {  
    "convert\_hl7\_to\_fhir": translation\_tools.convert\_hl7\_to\_fhir,  
}

@app.post("/api/translate", response\_model=TranslationResponse)  
async def translate\_data(request: TranslationRequest):  
    \# 1\. Get instruction from AI on which tool to use  
    try:  
        ai\_response \= await ai\_service.get\_ai\_translation\_instruction(request.data)  
        tool\_call \= ai\_response\["choices"\]\[0\]\["message"\]\["tool\_calls"\]\[0\]  
        tool\_name \= tool\_call\["function"\]\["name"\]  
    except Exception as e:  
        raise HTTPException(status\_code=500, detail=f"AI service error: {e}")

    \# 2\. Execute the specified tool  
    if tool\_name in AVAILABLE\_TOOLS:  
        function\_to\_call \= AVAILABLE\_TOOLS\[tool\_name\]  
        try:  
            \# For simplicity, we assume the AI passes the original data back.  
            \# A more robust solution would parse tool\_call\["function"\]\["arguments"\].  
            translated\_data \= function\_to\_call(request.data)  
        except ValueError as e:  
            raise HTTPException(status\_code=400, detail=f"Translation error: {e}")  
    else:  
        raise HTTPException(status\_code=400, detail=f"Unknown tool requested by AI: {tool\_name}")

    \# 3\. Validate the translated data  
    is\_valid \= validation\_service.validate\_fhir\_patient(translated\_data)  
    if not is\_valid:  
        raise HTTPException(status\_code=500, detail="Validation Failed: AI produced an invalid FHIR resource.")

    \# 4\. TODO: Implement routing logic to send data to the target system

    return TranslationResponse(  
        status="success",  
        translated\_data=translated\_data  
    )

