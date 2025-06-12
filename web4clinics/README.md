# Sunshine Clinic EMR System

A modern web-based Electronic Medical Record (EMR) system for clinics that allows managing patients and exchanging records with other healthcare facilities.

## Features

- **Patient Management**: Add and view patients in the system
- **Facility Registry**: View registered healthcare facilities 
- **Interoperability**: Send patient records to hospitals
- **Record Tracking**: Monitor status of sent records
- **Modern UI**: Clean, responsive interface for easy navigation

## Tech Stack

- **Backend**: Express.js server
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome

## Setup Instructions

### Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

### Installation

1. Clone this repository
```bash
git clone <repository-url>
cd web4clinics
```

2. Install dependencies
```bash
npm install
```

### Running the Application

1. Start the server
```bash
npm start
```

2. Access the application
Open your browser and navigate to: `http://localhost:3000`

## API Endpoints

- `GET /api/patients` - Get all patients
- `POST /api/patients` - Add a new patient
- `GET /api/facilities` - Get all registered healthcare facilities
- `GET /api/sent-records` - Get all sent records
- `POST /api/send-record` - Send patient record to a hospital

## Data Structure

The application uses the following JSON files for data storage:

- `wah4clinics/patients.json` - Patient records
- `wah4clinics/sent_records.json` - Records sent to hospitals
- `../facility_registry.json` - Registered healthcare facilities

## License

This project is licensed under the MIT License.

## Acknowledgments

This is a modern web implementation of the original CLI-based Sunshine Clinic EMR System. 