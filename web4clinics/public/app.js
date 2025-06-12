/**
 * Sunshine Clinic EMR System - Frontend JavaScript
 */

// Global state
const state = {
  patients: [],
  facilities: [],
  hospitals: [],
  sentRecords: [],
  activeView: 'patients-view'
};

// DOM Elements
const elements = {
  // Navigation tabs
  tabs: document.querySelectorAll('#main-nav .nav-link'),
  views: document.querySelectorAll('#views-container .view'),
  
  // Patient view
  patientsTableBody: document.getElementById('patients-table-body'),
  addPatientBtn: document.getElementById('add-patient-btn'),
  savePatientBtn: document.getElementById('save-patient-btn'),
  addPatientForm: document.getElementById('add-patient-form'),
  addPatientModal: new bootstrap.Modal(document.getElementById('add-patient-modal')),
  
  // Facilities view
  facilitiesTableBody: document.getElementById('facilities-table-body'),
  
  // Records view
  recordsTableBody: document.getElementById('records-table-body'),
  refreshRecordsBtn: document.getElementById('refresh-records-btn'),
  
  // Send to hospital
  sendToHospitalModal: new bootstrap.Modal(document.getElementById('send-to-hospital-modal')),
  hospitalSelect: document.getElementById('hospital-select'),
  sendPatientId: document.getElementById('send-patient-id'),
  sendPatientName: document.getElementById('send-patient-name'),
  confirmSendBtn: document.getElementById('confirm-send-btn'),
  
  // Toast notification
  toast: new bootstrap.Toast(document.getElementById('alert-toast'), { delay: 3000 }),
  toastMessage: document.getElementById('toast-message'),
  alertToast: document.getElementById('alert-toast')
};

// API Functions
const api = {
  async getPatients() {
    try {
      const response = await fetch('/api/patients');
      if (!response.ok) throw new Error('Failed to fetch patients');
      return await response.json();
    } catch (error) {
      showNotification('Error loading patients: ' + error.message, 'danger');
      return [];
    }
  },
  
  async addPatient(patientData) {
    try {
      const response = await fetch('/api/patients', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to add patient');
      }
      
      return await response.json();
    } catch (error) {
      showNotification('Error adding patient: ' + error.message, 'danger');
      return null;
    }
  },
  
  async getFacilities() {
    try {
      const response = await fetch('/api/facilities');
      if (!response.ok) throw new Error('Failed to fetch facilities');
      return await response.json();
    } catch (error) {
      showNotification('Error loading facilities: ' + error.message, 'danger');
      return [];
    }
  },
  
  async getSentRecords() {
    try {
      const response = await fetch('/api/sent-records');
      if (!response.ok) throw new Error('Failed to fetch sent records');
      return await response.json();
    } catch (error) {
      showNotification('Error loading sent records: ' + error.message, 'danger');
      return [];
    }
  },
  
  async sendPatientRecord(patientId, targetFacilityId) {
    try {
      const response = await fetch('/api/send-record', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patientId, targetFacilityId })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to send patient record');
      }
      
      return await response.json();
    } catch (error) {
      showNotification('Error sending record: ' + error.message, 'danger');
      return null;
    }
  }
};

// Helper Functions
function formatDateOfBirth(dob) {
  if (typeof dob === 'string' && dob.length === 8) {
    return `${dob.slice(0, 4)}-${dob.slice(4, 6)}-${dob.slice(6, 8)}`;
  }
  return dob;
}

function formatTimestamp(timestamp) {
  return new Date(timestamp).toLocaleString();
}

function showNotification(message, type = 'success') {
  elements.toastMessage.textContent = message;
  elements.alertToast.classList.remove('bg-success', 'bg-danger', 'bg-warning');
  elements.alertToast.classList.add(`bg-${type}`);
  elements.toast.show();
}

function clearForm(formElement) {
  formElement.reset();
}

// Render Functions
function renderPatients() {
  if (!state.patients || state.patients.length === 0) {
    elements.patientsTableBody.innerHTML = `
      <tr>
        <td colspan="6" class="text-center py-4">
          <i class="fas fa-info-circle me-2 text-primary"></i>
          No patients found in the database.
        </td>
      </tr>
    `;
    return;
  }
  
  elements.patientsTableBody.innerHTML = state.patients.map(patient => `
    <tr data-id="${patient.patientId}">
      <td>${patient.patientId}</td>
      <td>${patient.firstName} ${patient.lastName}</td>
      <td>${formatDateOfBirth(patient.dateOfBirth)}</td>
      <td>${patient.gender.charAt(0).toUpperCase() + patient.gender.slice(1)}</td>
      <td>
        ${patient.sent_to_hospital 
          ? '<span class="badge bg-success">Sent to Hospital</span>' 
          : '<span class="badge bg-warning text-dark">Not Sent</span>'}
      </td>
      <td>
        ${!patient.sent_to_hospital 
          ? `<button class="btn btn-sm btn-outline-primary send-record-btn" data-patient-id="${patient.patientId}" data-patient-name="${patient.firstName} ${patient.lastName}">
              <i class="fas fa-paper-plane me-1"></i> Send to Hospital
             </button>` 
          : `<button class="btn btn-sm btn-outline-secondary" disabled>
              <i class="fas fa-check me-1"></i> Already Sent
             </button>`}
      </td>
    </tr>
  `).join('');
  
  // Add event listeners to the send record buttons
  document.querySelectorAll('.send-record-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const patientId = this.getAttribute('data-patient-id');
      const patientName = this.getAttribute('data-patient-name');
      openSendToHospitalModal(patientId, patientName);
    });
  });
}

function renderFacilities() {
  if (!state.facilities || state.facilities.length === 0) {
    elements.facilitiesTableBody.innerHTML = `
      <tr>
        <td colspan="5" class="text-center py-4">
          <i class="fas fa-info-circle me-2 text-primary"></i>
          No facilities found in the database.
        </td>
      </tr>
    `;
    return;
  }
  
  elements.facilitiesTableBody.innerHTML = state.facilities.map(facility => `
    <tr>
      <td>${facility.facility_id}</td>
      <td>${facility.facility_name}</td>
      <td>${facility.type.charAt(0).toUpperCase() + facility.type.slice(1)}</td>
      <td>${facility.supported_formats ? facility.supported_formats.join(', ') : 'N/A'}</td>
      <td>${facility.api_endpoint || 'N/A'}</td>
    </tr>
  `).join('');
}

function renderSentRecords() {
  if (!state.sentRecords || state.sentRecords.length === 0) {
    elements.recordsTableBody.innerHTML = `
      <tr>
        <td colspan="5" class="text-center py-4">
          <i class="fas fa-info-circle me-2 text-primary"></i>
          No records have been sent yet.
        </td>
      </tr>
    `;
    return;
  }
  
  elements.recordsTableBody.innerHTML = state.sentRecords.map(record => `
    <tr>
      <td>${record.patientId}</td>
      <td>${record.patientName}</td>
      <td>${record.sent_to || 'N/A'}</td>
      <td>${formatTimestamp(record.sent_timestamp)}</td>
      <td>
        <span class="badge ${getStatusBadgeClass(record.status)}">
          ${record.status.charAt(0).toUpperCase() + record.status.slice(1)}
        </span>
      </td>
    </tr>
  `).join('');
}

function getStatusBadgeClass(status) {
  switch(status.toLowerCase()) {
    case 'sent':
      return 'bg-success';
    case 'pending':
      return 'bg-warning text-dark';
    case 'failed':
      return 'bg-danger';
    default:
      return 'bg-secondary';
  }
}

function populateHospitalSelect() {
  elements.hospitalSelect.innerHTML = `<option value="" selected disabled>Choose a hospital...</option>`;
  
  if (state.hospitals && state.hospitals.length > 0) {
    state.hospitals.forEach(hospital => {
      elements.hospitalSelect.innerHTML += `
        <option value="${hospital.facility_id}">${hospital.facility_name}</option>
      `;
    });
  } else {
    elements.hospitalSelect.innerHTML += `
      <option value="" disabled>No hospitals available</option>
    `;
  }
}

// Event Handlers
function openSendToHospitalModal(patientId, patientName) {
  elements.sendPatientId.value = patientId;
  elements.sendPatientName.textContent = patientName;
  elements.sendToHospitalModal.show();
}

async function sendPatientRecordToHospital() {
  const patientId = elements.sendPatientId.value;
  const targetFacilityId = elements.hospitalSelect.value;
  
  if (!patientId || !targetFacilityId) {
    showNotification('Please select a hospital', 'warning');
    return;
  }
  
  const result = await api.sendPatientRecord(patientId, targetFacilityId);
  
  if (result && result.success) {
    // Update UI
    elements.sendToHospitalModal.hide();
    showNotification(result.message);
    
    // Refresh data
    await loadAllData();
  }
}

// Tab Navigation
function setupTabs() {
  elements.tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      // Remove active class from all tabs
      elements.tabs.forEach(t => t.classList.remove('active'));
      // Add active class to clicked tab
      this.classList.add('active');
      
      // Get the target view
      const target = this.getAttribute('data-target');
      state.activeView = target;
      
      // Hide all views
      elements.views.forEach(view => view.classList.remove('active'));
      // Show target view
      document.getElementById(target).classList.add('active');
    });
  });
}

// Update loading indicators
function setLoading(element, isLoading) {
  if (isLoading) {
    element.innerHTML = `
      <tr>
        <td colspan="${element === elements.patientsTableBody ? '6' : '5'}" class="text-center">
          <div class="py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 mb-0">Loading data...</p>
          </div>
        </td>
      </tr>
    `;
  }
}

// Data loading functions
async function loadAllData() {
  // Set loading states
  setLoading(elements.patientsTableBody, true);
  setLoading(elements.facilitiesTableBody, true);
  setLoading(elements.recordsTableBody, true);
  
  // Load patients
  state.patients = await api.getPatients();
  renderPatients();
  
  // Load facilities
  state.facilities = await api.getFacilities();
  renderFacilities();
  
  // Filter hospitals from facilities
  state.hospitals = state.facilities.filter(facility => facility.type === 'hospital');
  populateHospitalSelect();
  
  // Load sent records
  state.sentRecords = await api.getSentRecords();
  renderSentRecords();
}

// Initialize the application
async function initApp() {
  // Setup tabs
  setupTabs();
  
  // Load all data from JSON files via API
  await loadAllData();
  
  // Setup event listeners
  elements.addPatientBtn.addEventListener('click', () => {
    clearForm(elements.addPatientForm);
    elements.addPatientModal.show();
  });
  
  elements.savePatientBtn.addEventListener('click', async () => {
    // Get form data
    const formData = new FormData(elements.addPatientForm);
    const patientData = Object.fromEntries(formData.entries());
    
    // Validate form data
    if (!patientData.firstName || !patientData.lastName || !patientData.dateOfBirth || !patientData.gender) {
      showNotification('Please fill in all required fields', 'warning');
      return;
    }
    
    // Validate date format
    if (!/^\d{8}$/.test(patientData.dateOfBirth)) {
      showNotification('Date of birth must be in YYYYMMDD format', 'warning');
      return;
    }
    
    // Add patient
    const newPatient = await api.addPatient(patientData);
    
    if (newPatient) {
      // Hide modal
      elements.addPatientModal.hide();
      
      // Show notification
      showNotification(`Patient ${newPatient.firstName} ${newPatient.lastName} added successfully`);
      
      // Refresh patients list
      state.patients = await api.getPatients();
      renderPatients();
    }
  });
  
  elements.refreshRecordsBtn.addEventListener('click', async () => {
    // Show loading indicator
    elements.refreshRecordsBtn.innerHTML = `<i class="fas fa-sync-alt me-2 spin"></i>Refreshing...`;
    elements.refreshRecordsBtn.disabled = true;
    
    // Refresh sent records
    state.sentRecords = await api.getSentRecords();
    renderSentRecords();
    
    // Restore button
    setTimeout(() => {
      elements.refreshRecordsBtn.innerHTML = `<i class="fas fa-sync-alt me-2"></i>Refresh Status`;
      elements.refreshRecordsBtn.disabled = false;
      showNotification('Records refreshed successfully');
    }, 1000);
  });
  
  elements.confirmSendBtn.addEventListener('click', sendPatientRecordToHospital);
}

// Initialize when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', initApp); 