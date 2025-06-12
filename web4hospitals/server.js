const express = require('express');
const path = require('path');
const fs = require('fs/promises');
const { existsSync } = require('fs');
const morgan = require('morgan');
const cors = require('cors');

// Constants
const PORT = process.env.PORT || 8001;
const RECEIVED_PATIENTS_FILE = path.join(__dirname, 'data', 'received_patients.json');
const PENDING_QUEUE_FILE = path.join(__dirname, 'data', 'pending_queue.json');

// Initialize Express app
const app = express();

// Middleware
app.use(cors());
app.use(morgan('dev'));
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Create data directory and files if they don't exist
async function initializeDataFiles() {
  const dataDir = path.join(__dirname, 'data');
  
  try {
    if (!existsSync(dataDir)) {
      await fs.mkdir(dataDir, { recursive: true });
    }
    
    // Create received_patients.json if it doesn't exist
    if (!existsSync(RECEIVED_PATIENTS_FILE)) {
      await fs.writeFile(RECEIVED_PATIENTS_FILE, '[]');
    }
    
    // Create pending_queue.json if it doesn't exist
    if (!existsSync(PENDING_QUEUE_FILE)) {
      await fs.writeFile(PENDING_QUEUE_FILE, '[]');
    }
    
    console.log('Data files initialized successfully');
  } catch (error) {
    console.error('Error initializing data files:', error);
  }
}

// Helper functions
async function loadJsonFile(filePath) {
  try {
    const data = await fs.readFile(filePath, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error(`Error loading file ${filePath}:`, error);
    return [];
  }
}

async function saveJsonFile(filePath, data) {
  try {
    await fs.writeFile(filePath, JSON.stringify(data, null, 2));
    return true;
  } catch (error) {
    console.error(`Error saving file ${filePath}:`, error);
    return false;
  }
}

function extractPatientDetails(fhirData) {
  try {
    // Extract key information
    let patientId = "Unknown";
    if (fhirData.identifier && fhirData.identifier.length > 0) {
      patientId = fhirData.identifier[0].value || "Unknown";
    }
    
    const nameData = fhirData.name && fhirData.name.length > 0 ? fhirData.name[0] : {};
    const familyName = nameData.family || "Unknown";
    const givenNames = nameData.given || ["Unknown"];
    const givenName = givenNames[0] || "Unknown";
    
    const birthDate = fhirData.birthDate || "Unknown";
    const gender = fhirData.gender || "Unknown";
    
    // Create a display-friendly version
    return {
      patient_id: patientId,
      given_name: givenName,
      family_name: familyName,
      full_name: `${givenName} ${familyName}`,
      birth_date: birthDate,
      gender: gender,
      original_fhir: fhirData
    };
  } catch (error) {
    console.error('Error extracting patient details:', error);
    return {
      patient_id: "Error",
      given_name: "Error",
      family_name: "Error",
      full_name: "Error processing patient data",
      birth_date: "Unknown",
      gender: "Unknown",
      original_fhir: fhirData
    };
  }
}

// API Routes
// Get all patients
app.get('/api/patients', async (req, res) => {
  try {
    const patients = await loadJsonFile(RECEIVED_PATIENTS_FILE);
    res.json(patients);
  } catch (error) {
    res.status(500).json({ error: 'Failed to load patients' });
  }
});

// Get pending patients
app.get('/api/pending', async (req, res) => {
  try {
    const pendingPatients = await loadJsonFile(PENDING_QUEUE_FILE);
    res.json(pendingPatients);
  } catch (error) {
    res.status(500).json({ error: 'Failed to load pending patients' });
  }
});

// Process pending patients
app.post('/api/process-pending', async (req, res) => {
  try {
    const pendingPatients = await loadJsonFile(PENDING_QUEUE_FILE);
    const receivedPatients = await loadJsonFile(RECEIVED_PATIENTS_FILE);
    
    // Add all pending patients to received patients
    receivedPatients.push(...pendingPatients);
    
    // Save updated received patients
    await saveJsonFile(RECEIVED_PATIENTS_FILE, receivedPatients);
    
    // Clear pending queue
    await saveJsonFile(PENDING_QUEUE_FILE, []);
    
    res.json({ 
      success: true, 
      message: `${pendingPatients.length} records have been processed` 
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to process pending patients' });
  }
});

// Search for patients
app.get('/api/search', async (req, res) => {
  try {
    const { query } = req.query;
    if (!query) {
      return res.json([]);
    }
    
    const patients = await loadJsonFile(RECEIVED_PATIENTS_FILE);
    const searchTerm = query.toLowerCase();
    
    const results = patients.filter(patient => 
      patient.details.patient_id.toLowerCase().includes(searchTerm) || 
      patient.details.full_name.toLowerCase().includes(searchTerm)
    );
    
    res.json(results);
  } catch (error) {
    res.status(500).json({ error: 'Search failed' });
  }
});

// Receive FHIR patient data
app.post('/fhir/patient', async (req, res) => {
  try {
    const fhirData = req.body;
    
    // Extract patient details
    const patientDetails = extractPatientDetails(fhirData);
    
    // Create pending record
    const pendingRecord = {
      details: patientDetails,
      received_timestamp: new Date().toISOString(),
      status: 'pending'
    };
    
    // Add to pending queue
    const pendingQueue = await loadJsonFile(PENDING_QUEUE_FILE);
    pendingQueue.push(pendingRecord);
    await saveJsonFile(PENDING_QUEUE_FILE, pendingQueue);
    
    console.log(`New patient record received: ${patientDetails.full_name} (ID: ${patientDetails.patient_id})`);
    
    res.status(200).json({
      status: 'success',
      message: `Patient data for ${patientDetails.full_name} received and pending review.`
    });
  } catch (error) {
    console.error('Error processing patient data:', error);
    res.status(500).json({ error: 'Failed to process patient data' });
  }
});

// Start server
async function startServer() {
  await initializeDataFiles();
  
  app.listen(PORT, () => {
    console.log(`Memorial Hospital EMR Server running on port ${PORT}`);
    console.log(`Visit http://localhost:${PORT} to access the application`);
  });
}

startServer(); 