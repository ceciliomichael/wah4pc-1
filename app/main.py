import os
import httpx
import json
from fastapi import FastAPI, HTTPException  
from dotenv import load_dotenv
import pprint
from pydantic import BaseModel, Field
from typing import Dict, Any, List

# Load environment variables from .env file  
load_dotenv()

# --- Custom Pydantic Models for Metadata-driven Payload ---
class TranslationMetadata(BaseModel):
    source_facility_id: str
    target_facility_id: str
    source_format: str
    target_format: str

class InteropRequest(BaseModel):
    metadata: TranslationMetadata
    data: Dict[str, Any]

from .models import TranslationResponse  
from .services import ai_service, validation_service, translation_tools

# --- Facility Registry Loading ---
REGISTRY_FILE = "facility_registry.json"

def load_facility_registry():
    try:
        with open(REGISTRY_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"FATAL: Facility registry file not found at '{REGISTRY_FILE}'")
        return []
    except json.JSONDecodeError:
        print(f"FATAL: Could not parse facility registry file.")
        return []

FACILITY_REGISTRY = load_facility_registry()

# --- Dynamic Tool Definitions for the AI ---
# A mapping of tool names to the actual Python functions
AVAILABLE_FUNCTION_MAP = {
    "translate_hl7_v2_json_to_fhir_r4": translation_tools.translate_hl7_v2_json_to_fhir_r4,
    "translate_custom_clinic_format_v1_to_fhir_r4": translation_tools.translate_custom_clinic_format_v1_to_fhir_r4
}

# The full tool schemas that the AI will see
AI_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "translate_hl7_v2_json_to_fhir_r4",
            "description": "Translates a simplified HL7-like JSON dictionary to a FHIR R4 Patient resource.",
            "parameters": {
                "type": "object",
                "properties": { "hl7_data": { "type": "object", "description": "The HL7-like JSON data."}},
                "required": ["hl7_data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "translate_custom_clinic_format_v1_to_fhir_r4",
            "description": "Translates a proprietary Custom Clinic V1 format to a FHIR R4 Patient resource.",
            "parameters": {
                "type": "object",
                "properties": { "custom_data": { "type": "object", "description": "The Custom Clinic V1 data."}},
                "required": ["custom_data"]
            }
        }
    }
]

app = FastAPI(  
    title="Healthcare Interoperability System",  
    description="A metadata-driven service that translates healthcare data formats using an AI agent."  
)

def pretty_print_json(data, title=None):
    """
    Print formatted JSON data with a title if provided
    """
    if title:
        print(f"\n[{title}]")
    
    if isinstance(data, dict) or isinstance(data, list):
        formatted_json = json.dumps(data, indent=2, sort_keys=False)
        print(formatted_json)
    else:
        # Use pprint for non-JSON objects
        pp = pprint.PrettyPrinter(indent=2, width=100)
        pp.pprint(data)

async def route_to_target(target_facility_id: str, data: dict):
    """
    Forwards the translated data to the dynamically looked-up target system.
    """
    target_facility = next((f for f in FACILITY_REGISTRY if f["facility_id"] == target_facility_id), None)
    
    if not target_facility or not target_facility.get("api_endpoint"):
        msg = f"No API endpoint configured for target facility '{target_facility_id}'. Skipping routing."
        print(f"[WARNING] {msg}")
        # Not raising an exception, as the primary translation job is done.
        return

    target_endpoint = target_facility["api_endpoint"]
    try:
        print(f"\n[SYSTEM] Routing translated FHIR data to '{target_facility['facility_name']}' at {target_endpoint}")
        print("\n[SYSTEM] Data being sent:")
        pretty_print_json(data)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(target_endpoint, json=data, timeout=30.0)
            response.raise_for_status()
            print(f"[SYSTEM] Successfully routed data to target system")
            response_json = response.json()
            pretty_print_json(response_json, "TARGET RESPONSE")
    except httpx.RequestError as e:
        print(f"[ERROR] Failed to route data to target system: {e}")
        # Decide if this should be a fatal error for the transaction
        raise HTTPException(status_code=502, detail=f"Failed to route data to target system: {e}")


@app.post("/api/translate", response_model=TranslationResponse)  
async def translate_data(request: InteropRequest):  
    print("\n" + "="*80)
    print(" "*25 + "INTEROPERABILITY SYSTEM WORKFLOW")
    print("="*80)
    
    metadata = request.metadata
    print("\n[REQUEST] Received metadata-driven translation request:")
    pretty_print_json(metadata.dict(), "METADATA")
    
    print("\n[REQUEST] Source data:")
    pretty_print_json(request.data, "SOURCE DATA")
    
    # Display format information based on metadata
    print("\n[FORMAT INFO] Data Format Description:")
    print("-"*80)
    print(f"SOURCE FORMAT: {metadata.source_format}")
    print(f"TARGET FORMAT: {metadata.target_format}")
    print("-"*80)
    
    # 1. Get instruction from AI on which tool to use  
    try:  
        print("\n[STEP 1] Getting translation instructions from AI service...")
        ai_response = await ai_service.get_ai_translation_instruction(
            source_format=metadata.source_format,
            target_format=metadata.target_format,
            source_data=request.data,
            available_tools=AI_TOOL_DEFINITIONS
        )
        tool_call = ai_response["choices"][0]["message"]["tool_calls"][0]  
        tool_name = tool_call["function"]["name"]
        
        # The AI needs to return the arguments with the correct parameter name
        tool_args = json.loads(tool_call["function"]["arguments"])

        print(f"[SUCCESS] AI selected tool: {tool_name}")
        print("\n[AI TOOL ARGUMENTS]")
        pretty_print_json(tool_args)
    except Exception as e:  
        print(f"[ERROR] AI service error: {e}")
        raise HTTPException(status_code=500, detail=f"AI service error: {e}")

    # 2. Execute the specified tool  
    if tool_name in AVAILABLE_FUNCTION_MAP:  
        function_to_call = AVAILABLE_FUNCTION_MAP[tool_name]  
        try:  
            print(f"\n[STEP 2] Executing translation tool: {tool_name}...")
            # Pass the arguments object directly as kwargs
            translated_data = function_to_call(**tool_args)  
            print(f"[SUCCESS] Translation completed")
            print("\n[OUTPUT FORMAT] FHIR Patient resource:")
            pretty_print_json(translated_data, "FHIR RESOURCE")
        except (ValueError, TypeError) as e:  
            print(f"[ERROR] Translation tool execution error: {e}")
            raise HTTPException(status_code=400, detail=f"Translation error: {e}")  
    else:  
        print(f"[ERROR] Unknown tool requested by AI: {tool_name}")
        raise HTTPException(status_code=400, detail=f"Unknown tool requested by AI: {tool_name}")

    # 3. Validate the translated data  
    print(f"\n[STEP 3] Validating FHIR resource structure...")
    is_valid = validation_service.validate_fhir_patient(translated_data)  
    if not is_valid:  
        print(f"[ERROR] Validation failed: AI produced an invalid FHIR resource")
        raise HTTPException(status_code=500, detail="Validation Failed: AI produced an invalid FHIR resource.")
    print(f"[SUCCESS] FHIR validation passed")

    # 4. Route the validated data to the target system
    print(f"\n[STEP 4] Routing data to target hospital system...")
    await route_to_target(metadata.target_facility_id, translated_data)

    print("\n[COMPLETE] Translation and routing process successful!")
    print("="*80)

    return TranslationResponse(  
        status="success",  
        translated_data=translated_data  
    ) 