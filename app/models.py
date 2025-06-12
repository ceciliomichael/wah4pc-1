from pydantic import BaseModel, Field  
from typing import Dict, Any, Optional

class TranslationRequest(BaseModel):  
    source_format: str = Field(..., example="hl7")  
    target_format: str = Field(..., example="fhir")  
    data: Dict[str, Any] = Field(..., example={"patientId": "C123", "lastName": "Dela Cruz"})

class TranslationResponse(BaseModel):  
    status: str  
    translated_data: Optional[Dict[str, Any]] = None  
    error_message: Optional[str] = None 