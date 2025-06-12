#!/usr/bin/env python3
import os
import json
import time
import sys
from datetime import datetime
from tabulate import tabulate
from fastapi import FastAPI, Request
import uvicorn
import threading

# Constants
RECEIVED_PATIENTS_FILE = os.path.join(os.path.dirname(__file__), "received_patients.json")
PENDING_QUEUE_FILE = os.path.join(os.path.dirname(__file__), "pending_queue.json")
API_HOST = "0.0.0.0"
API_PORT = 8001

# Create FastAPI app for receiving data
app = FastAPI(
    title="Memorial Hospital EMR",
    description="Hospital system that receives FHIR Patient records."
)

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_json_file(file_path, default=None):
    """Load data from a JSON file."""
    if default is None:
        default = []
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        return default
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return default

def save_json_file(file_path, data):
    """Save data to a JSON file."""
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
        return True
    except Exception as e:
        print(f"Error saving file {file_path}: {e}")
        return False

def display_header():
    """Display the hospital system header."""
    clear_screen()
    print("=" * 60)
    print(" " * 15 + "MEMORIAL HOSPITAL EMR SYSTEM")
    print("=" * 60)
    print()

def display_menu():
    """Display the main menu options."""
    print("\nMAIN MENU:")
    print("1. View All Patients")
    print("2. Check Pending Records")
    print("3. Process Pending Records")
    print("4. Search Patient")
    print("5. Exit")
    return input("\nSelect an option (1-5): ")

def extract_patient_details(fhir_data):
    """Extract patient details from FHIR data."""
    try:
        # Extract key information
        patient_id = "Unknown"
        for identifier in fhir_data.get("identifier", []):
            patient_id = identifier.get("value", "Unknown")
        
        name_data = fhir_data.get("name", [{}])[0]
        family_name = name_data.get("family", "Unknown")
        given_names = name_data.get("given", ["Unknown"])
        given_name = given_names[0] if given_names else "Unknown"
        
        birth_date = fhir_data.get("birthDate", "Unknown")
        gender = fhir_data.get("gender", "Unknown")
        
        # Create a display-friendly version
        return {
            "patient_id": patient_id,
            "given_name": given_name,
            "family_name": family_name,
            "full_name": f"{given_name} {family_name}",
            "birth_date": birth_date,
            "gender": gender,
            "original_fhir": fhir_data
        }
    except Exception as e:
        print(f"Error extracting patient details: {e}")
        return {
            "patient_id": "Error",
            "given_name": "Error",
            "family_name": "Error",
            "full_name": "Error processing patient data",
            "birth_date": "Unknown",
            "gender": "Unknown",
            "original_fhir": fhir_data
        }

def view_all_patients():
    """Display all patients in the hospital system."""
    display_header()
    print("\n--- PATIENT LIST ---\n")
    
    patients = load_json_file(RECEIVED_PATIENTS_FILE)
    
    if not patients:
        print("No patients found in the system.")
        input("\nPress Enter to continue...")
        return
    
    headers = ["#", "Patient ID", "Name", "Birth Date", "Gender", "Received Date"]
    table_data = []
    
    for i, patient in enumerate(patients):
        received_date = datetime.fromisoformat(patient["received_timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        table_data.append([
            i + 1,
            patient["details"]["patient_id"],
            patient["details"]["full_name"],
            patient["details"]["birth_date"],
            patient["details"]["gender"].capitalize(),
            received_date
        ])
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # View detailed information option
    choice = input("\nEnter patient number for details (0 to return): ")
    if choice.isdigit() and int(choice) > 0 and int(choice) <= len(patients):
        idx = int(choice) - 1
        patient = patients[idx]
        
        display_header()
        print("\n--- PATIENT DETAILS ---\n")
        
        print(f"Patient ID: {patient['details']['patient_id']}")
        print(f"Name: {patient['details']['full_name']}")
        print(f"Date of Birth: {patient['details']['birth_date']}")
        print(f"Gender: {patient['details']['gender'].capitalize()}")
        print(f"Received: {datetime.fromisoformat(patient['received_timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\nOriginal FHIR Data:")
        print(json.dumps(patient["details"]["original_fhir"], indent=2))
        
        input("\nPress Enter to continue...")
    
    elif choice != "0":
        print("Invalid selection.")
        time.sleep(1)

def check_pending_records():
    """Check and display records pending processing."""
    display_header()
    print("\n--- PENDING RECORDS ---\n")
    
    pending = load_json_file(PENDING_QUEUE_FILE)
    
    if not pending:
        print("No pending records found.")
        input("\nPress Enter to continue...")
        return
    
    headers = ["#", "Patient ID", "Name", "Birth Date", "Received"]
    table_data = []
    
    for i, record in enumerate(pending):
        table_data.append([
            i + 1,
            record["details"]["patient_id"],
            record["details"]["full_name"],
            record["details"]["birth_date"],
            datetime.fromisoformat(record["received_timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        ])
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print(f"\nTotal pending records: {len(pending)}")
    input("\nPress Enter to continue...")

def process_pending_records():
    """Process and acknowledge pending records."""
    display_header()
    print("\n--- PROCESS PENDING RECORDS ---\n")
    
    pending = load_json_file(PENDING_QUEUE_FILE)
    received = load_json_file(RECEIVED_PATIENTS_FILE)
    
    if not pending:
        print("No pending records to process.")
        input("\nPress Enter to continue...")
        return
    
    print(f"You have {len(pending)} pending records.")
    choice = input("\nProcess all pending records? (y/n): ")
    
    if choice.lower() != "y":
        return
    
    print("\nProcessing records...")
    
    # Move all pending records to received patients
    for record in pending:
        received.append(record)
    
    save_json_file(RECEIVED_PATIENTS_FILE, received)
    save_json_file(PENDING_QUEUE_FILE, [])  # Clear pending queue
    
    print(f"\n{len(pending)} records have been processed and added to the patient database.")
    input("\nPress Enter to continue...")

def search_patient():
    """Search for a patient by ID or name."""
    display_header()
    print("\n--- SEARCH PATIENT ---\n")
    
    patients = load_json_file(RECEIVED_PATIENTS_FILE)
    
    if not patients:
        print("No patients in the system to search.")
        input("\nPress Enter to continue...")
        return
    
    search_term = input("Enter patient ID or name: ")
    
    if not search_term:
        return
    
    search_term = search_term.lower()
    results = []
    
    for patient in patients:
        if (search_term in patient["details"]["patient_id"].lower() or
            search_term in patient["details"]["full_name"].lower()):
            results.append(patient)
    
    if not results:
        print("\nNo matching patients found.")
        input("\nPress Enter to continue...")
        return
    
    print(f"\nFound {len(results)} matching patients:\n")
    
    headers = ["#", "Patient ID", "Name", "Birth Date", "Gender"]
    table_data = []
    
    for i, patient in enumerate(results):
        table_data.append([
            i + 1,
            patient["details"]["patient_id"],
            patient["details"]["full_name"],
            patient["details"]["birth_date"],
            patient["details"]["gender"].capitalize()
        ])
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    input("\nPress Enter to continue...")

# FastAPI endpoint to receive patient data
@app.post("/fhir/patient")
async def receive_patient_data(request: Request):
    fhir_data = await request.json()
    
    # Extract useful information for display
    patient_details = extract_patient_details(fhir_data)
    
    # Create a record for the incoming patient
    pending_record = {
        "details": patient_details,
        "received_timestamp": datetime.now().isoformat(),
        "status": "pending"
    }
    
    # Add to pending queue
    pending_queue = load_json_file(PENDING_QUEUE_FILE)
    pending_queue.append(pending_record)
    save_json_file(PENDING_QUEUE_FILE, pending_queue)
    
    print("\n--- New patient record received! ---")
    print(f"Patient: {patient_details['full_name']} (ID: {patient_details['patient_id']})")
    print("Added to pending queue for processing.")
    
    return {
        "status": "success",
        "message": f"Patient data for {patient_details['full_name']} received and pending review."
    }

def start_api_server():
    """Start the FastAPI server in a separate thread."""
    uvicorn.run(app, host=API_HOST, port=API_PORT)

def main():
    """Main function to run the hospital system."""
    # Start the API server in a separate thread
    server_thread = threading.Thread(target=start_api_server, daemon=True)
    server_thread.start()
    
    print(f"Hospital API server starting at http://{API_HOST}:{API_PORT}")
    time.sleep(1)  # Give server time to start
    
    while True:
        display_header()
        print(f"API Server running at http://{API_HOST}:{API_PORT}")
        choice = display_menu()
        
        if choice == '1':
            view_all_patients()
        elif choice == '2':
            check_pending_records()
        elif choice == '3':
            process_pending_records()
        elif choice == '4':
            search_patient()
        elif choice == '5':
            display_header()
            print("\nThank you for using Memorial Hospital EMR System!")
            print("\nExiting...\n")
            sys.exit(0)
        else:
            print("\nInvalid option. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    main() 