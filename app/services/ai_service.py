import os  
import httpx
import json
from typing import Dict, Any, List

# Load from environment  
AI_ENDPOINT = os.getenv("AI_API_ENDPOINT")  
AI_KEY = os.getenv("AI_API_KEY")  
AI_MODEL = os.getenv("AI_MODEL_NAME")

async def get_ai_translation_instruction(
    source_format: str, 
    target_format: str,
    source_data: Dict[str, Any],
    available_tools: List[Dict]
) -> Dict[str, Any]:  
    """  
    Calls the AI model to get instructions on which tool to use, based on dynamic formats.
    """  
    formatted_source_data = json.dumps(source_data, indent=2)
    
    # The prompt is now dynamic based on the metadata from the request
    prompt = f"""
You are a data format translation controller in a healthcare interoperability system.
Your task is to select the correct Python function to call to translate the following data packet.

- Source Format: {source_format}
- Target Format: {target_format}

Data Packet:
{formatted_source_data}

Based on the source and target formats, determine the appropriate function to call from the available tools.
    """.strip()

    headers = {  
        "Authorization": f"Bearer {AI_KEY}",  
        "Content-Type": "application/json"  
    }  
      
    payload = {  
        "model": AI_MODEL,  
        "messages": [{"role": "user", "content": prompt}],  
        "tools": available_tools,  # Pass the list of available tools
        "tool_choice": "auto"  
    }

    # Display the AI translation process in the terminal
    print("\n" + "="*80)
    print(" "*30 + "AI TRANSLATION PROCESS")
    print("="*80)
    
    print(f"\n[SYSTEM] Source Format: {source_format} -> Target Format: {target_format}")
    
    print("\n[SYSTEM] Prompting AI with dynamic prompt:")
    print("-"*80)
    print(prompt)
    print("-"*80)
    
    print(f"\n[SYSTEM] Requesting translation from AI model: {AI_MODEL}")
    
    async with httpx.AsyncClient() as client:  
        response = await client.post(AI_ENDPOINT, json=payload, headers=headers, timeout=30.0)  
        response.raise_for_status()
        
        response_data = response.json()
        print("\n[SYSTEM] AI Response received!")
        
        print("\n[AI FULL RESPONSE]")
        print("="*80)
        print(json.dumps(response_data, indent=2))
        print("="*80)
        
        try:
            tool_call = response_data["choices"][0]["message"]["tool_calls"][0]
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])
            
            print(f"\n[AI DECISION] AI decided to use tool: {tool_name}")
            print("\n[AI TOOL ARGUMENTS] Arguments to be passed to the function:")
            print(json.dumps(tool_args, indent=2))
            
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"\n[ERROR] Could not extract tool call information from AI response: {e}")
        
        return response_data 