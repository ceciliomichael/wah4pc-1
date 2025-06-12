#!/usr/bin/env python3
import os
import json
import requests
import time
import sys
from datetime import datetime
from tabulate import tabulate

# Constants
PATIENTS_FILE = os.path.join(os.path.dirname(__file__), "patients.json")
SENT_RECORDS_FILE = os.path.join(os.path.dirname(__file__), "sent_records.json")
REGISTRY_FILE = os.path.join(os.path.dirname(__file__), "..", "facility_registry.json")
INTEROP_API_URL = "http://localhost:8000/api/translate"
CLINIC_ID = "sunshine_clinic"

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
    """Display the clinic system header."""
    clear_screen()
    print("=" * 60)
    print(" " * 15 + "SUNSHINE CLINIC EMR SYSTEM")
    print("=" * 60)
    print()

def display_menu():
    """Display the main menu options."""
    print("\nMAIN MENU:")
    print("1. View All Patients")
    print("2. Add New Patient")
    print("3. View Registered Facilities")
    print("4. Send Patient Record to Hospital")
    print("5. View Sent Records Status")
    print("6. Exit")
    return input("\nSelect an option (1-6): ")

def format_patient_record(patient, index=None):
    """Format a patient record for display."""
    if index is not None:
        return [
            index, 
            patient["patientId"],
            f"{patient['firstName']} {patient['lastName']}",
            format_dob(patient["dateOfBirth"]),
            patient["gender"].capitalize(),
            patient.get("sent_to_hospital", False)
        ]
    else:
        return [
            patient["patientId"],
            f"{patient['firstName']} {patient['lastName']}",
            format_dob(patient["dateOfBirth"]),
            patient["gender"].capitalize(),
            patient.get("sent_to_hospital", False)
        ]

def format_dob(dob_string):
    """Format date of birth from YYYYMMDD to YYYY-MM-DD."""
    if len(dob_string) == 8:
        return f"{dob_string[0:4]}-{dob_string[4:6]}-{dob_string[6:8]}"
    return dob_string

def view_all_patients():
    """Display all patients in the system."""
    display_header()
    patients = load_json_file(PATIENTS_FILE)
    
    if not patients:
        print("\nNo patients found in the system.")
        input("\nPress Enter to continue...")
        return
    
    print("\n--- PATIENT LIST ---\n")
    
    headers = ["#", "Patient ID", "Name", "Date of Birth", "Gender", "Sent to Hospital"]
    table_data = [format_patient_record(patient, i+1) for i, patient in enumerate(patients)]
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    input("\nPress Enter to continue...")

def add_new_patient():
    """Add a new patient to the system."""
    display_header()
    print("\n--- ADD NEW PATIENT ---\n")
    
    patients = load_json_file(PATIENTS_FILE)
    
    # Generate a new patient ID
    last_id = 0
    for patient in patients:
        try:
            id_num = int(patient["patientId"].replace("C", ""))
            if id_num > last_id:
                last_id = id_num
        except:
            pass
    
    new_id = f"C{last_id + 1:03d}"
    
    # Collect patient information
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    
    dob = input("Date of Birth (YYYYMMDD): ")
    while len(dob) != 8 or not dob.isdigit():
        print("Invalid format. Please enter date in YYYYMMDD format.")
        dob = input("Date of Birth (YYYYMMDD): ")
    
    gender = input("Gender (male/female): ").lower()
    while gender not in ["male", "female"]:
        print("Please enter 'male' or 'female'.")
        gender = input("Gender (male/female): ").lower()
    
    address = input("Address: ")
    phone = input("Phone Number: ")
    insurance = input("Insurance Number: ")
    
    # Create the new patient record
    new_patient = {
        "patientId": new_id,
        "firstName": first_name,
        "lastName": last_name,
        "dateOfBirth": dob,
        "gender": gender,
        "address": address,
        "phoneNumber": phone,
        "insuranceNumber": insurance,
        "sent_to_hospital": False
    }
    
    # Add to the patients list and save
    patients.append(new_patient)
    if save_json_file(PATIENTS_FILE, patients):
        print(f"\nPatient {new_id} ({first_name} {last_name}) added successfully!")
    else:
        print("\nFailed to save the new patient record.")
    
    input("\nPress Enter to continue...")

def view_registered_facilities():
    """Display all registered facilities from the registry."""
    display_header()
    print("\n--- REGISTERED HEALTHCARE FACILITIES ---\n")
    
    facilities = load_json_file(REGISTRY_FILE)
    if not facilities:
        print("Could not load facility registry.")
        input("\nPress Enter to continue...")
        return
        
    headers = ["ID", "Name", "Type", "Supported Formats", "API Endpoint"]
    table_data = []
    
    for facility in facilities:
        table_data.append([
            facility["facility_id"],
            facility["facility_name"],
            facility["type"].capitalize(),
            ", ".join(facility["supported_formats"]),
            facility.get("api_endpoint", "N/A")
        ])
        
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    input("\nPress Enter to continue...")

def send_patient_to_hospital():
    """Send a patient record to a selected hospital via the interoperability system."""
    display_header()
    print("\n--- SEND PATIENT RECORD TO HOSPITAL ---\n")
    
    # Load facilities and patients
    facilities = load_json_file(REGISTRY_FILE)
    patients = load_json_file(PATIENTS_FILE)
    
    # Filter for available hospitals
    hospitals = [f for f in facilities if f["type"] == "hospital"]
    if not hospitals:
        print("No hospitals found in the facility registry.")
        input("\nPress Enter to continue...")
        return
        
    # Display target hospitals
    print("Select a target hospital:")
    headers = ["#", "ID", "Name", "Preferred Format"]
    table_data = [[i+1, h["facility_id"], h["facility_name"], h.get("preferred_format", "N/A")] for i, h in enumerate(hospitals)]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    try:
        selection = int(input("\nEnter hospital number (0 to cancel): "))
        if selection == 0: return
        selected_hospital = hospitals[selection - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        input("\nPress Enter to continue...")
        return

    # Display available patients to send
    available_patients = [p for p in patients if not p.get("sent_to_hospital", False)]
    if not available_patients:
        print("\nAll patient records have already been sent.")
        input("\nPress Enter to continue...")
        return
        
    print("\nSelect a patient to send:")
    headers = ["#", "Patient ID", "Name"]
    table_data = [[i+1, p["patientId"], f"{p['firstName']} {p['lastName']}"] for i, p in enumerate(available_patients)]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    try:
        selection = int(input("\nEnter patient number (0 to cancel): "))
        if selection == 0: return
        selected_patient = available_patients[selection - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        input("\nPress Enter to continue...")
        return
    
    print(f"\nSending patient {selected_patient['patientId']} to {selected_hospital['facility_name']}...")
    
    # --- This is the new metadata-driven payload ---
    payload = {
        "metadata": {
            "source_facility_id": CLINIC_ID,
            "target_facility_id": selected_hospital["facility_id"],
            "source_format": "hl7_v2_json", # This clinic uses this format
            "target_format": selected_hospital["preferred_format"]
        },
        "data": selected_patient
    }
    
    try:
        response = requests.post(INTEROP_API_URL, json=payload)
        response.raise_for_status()
        response_data = response.json()
        
        if response_data.get("status") == "success":
            # Mark patient as sent
            for patient in patients:
                if patient["patientId"] == selected_patient["patientId"]:
                    patient["sent_to_hospital"] = True
                    save_json_file(PATIENTS_FILE, patients)
                    break
            
            # Update sent records
            sent_records = load_json_file(SENT_RECORDS_FILE)
            sent_record = {
                "patientId": selected_patient["patientId"],
                "patientName": f"{selected_patient['firstName']} {selected_patient['lastName']}",
                "sent_to": selected_hospital["facility_id"],
                "sent_timestamp": datetime.now().isoformat(),
                "status": "sent"
            }
            sent_records.append(sent_record)
            save_json_file(SENT_RECORDS_FILE, sent_records)
            
            print(f"\nPatient record successfully sent to {selected_hospital['facility_name']}!")
        else:
            print(f"\nError from Interop Service: {response_data.get('error_message', 'Unknown error')}")
    
    except requests.exceptions.RequestException as e:
        print(f"\nError connecting to interoperability service: {e}")
    
    input("\nPress Enter to continue...")

def view_sent_records():
    """View status of records sent to the hospital."""
    display_header()
    print("\n--- SENT RECORDS STATUS ---\n")
    
    sent_records = load_json_file(SENT_RECORDS_FILE)
    
    if not sent_records:
        print("No records have been sent to the hospital yet.")
        input("\nPress Enter to continue...")
        return
    
    headers = ["Patient ID", "Patient Name", "Sent To", "Sent Date", "Status"]
    table_data = []
    
    for record in sent_records:
        sent_time = datetime.fromisoformat(record["sent_timestamp"])
        sent_date = sent_time.strftime("%Y-%m-%d %H:%M:%S")
        table_data.append([
            record["patientId"],
            record["patientName"],
            record.get("sent_to", "N/A"),
            sent_date,
            record["status"].capitalize()
        ])
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Option to refresh the status
    choice = input("\nWould you like to refresh the status? (y/n): ")
    if choice.lower() == 'y':
        print("\nRefreshing status...")
        # In a real system, this would query the hospital for updates
        # For now, just simulate a check
        time.sleep(1)
        print("Status up to date!")
    
    input("\nPress Enter to continue...")

def main():
    """Main function to run the clinic system."""
    while True:
        display_header()
        choice = display_menu()
        
        if choice == '1':
            view_all_patients()
        elif choice == '2':
            add_new_patient()
        elif choice == '3':
            view_registered_facilities()
        elif choice == '4':
            send_patient_to_hospital()
        elif choice == '5':
            view_sent_records()
        elif choice == '6':
            display_header()
            print("\nThank you for using Sunshine Clinic EMR System!")
            print("\nExiting...\n")
            sys.exit(0)
        else:
            print("\nInvalid option. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    main() 