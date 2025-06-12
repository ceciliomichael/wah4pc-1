// DOM Elements
const menuToggle = document.getElementById('menu-toggle');
const appContainer = document.querySelector('.app-container');
const navItems = document.querySelectorAll('.sidebar-nav li');
const viewSections = document.querySelectorAll('.view-section');
const currentViewTitle = document.getElementById('current-view-title');
const quickSearchInput = document.getElementById('quick-search');
const processAllBtn = document.getElementById('process-all-btn');
const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const patientsSearchInput = document.getElementById('patients-search');
const confirmBtn = document.getElementById('confirm-btn');
const closeModalButtons = document.querySelectorAll('.close-modal');
const viewAllBtn = document.querySelector('.view-all-btn');

// Tables
const recentPatientsTable = document.getElementById('recent-patients-table').querySelector('tbody');
const allPatientsTable = document.getElementById('all-patients-table').querySelector('tbody');
const pendingPatientsTable = document.getElementById('pending-patients-table').querySelector('tbody');
const searchResultsTable = document.getElementById('search-results-table').querySelector('tbody');

// Modals
const patientDetailsModal = document.getElementById('patient-details-modal');
const confirmationModal = document.getElementById('confirmation-modal');
const confirmationMessage = document.getElementById('confirmation-message');

// Stats elements
const totalPatientsCount = document.querySelector('.total-patients-count');
const pendingPatientsCount = document.querySelector('.pending-patients-count');
const todayRecordsCount = document.querySelector('.today-records-count');
const pendingCount = document.querySelector('.pending-count');
const resultsCount = document.querySelector('.results-count');

// Current action to be performed when confirmation is clicked
let currentConfirmAction = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

// Initialize the application
async function initApp() {
  attachEventListeners();
  await loadDashboardData();
}

// Attach event listeners
function attachEventListeners() {
  // Menu toggle
  menuToggle.addEventListener('click', () => {
    appContainer.classList.toggle('sidebar-collapsed');
  });

  // Navigation
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const view = item.getAttribute('data-view');
      changeView(view);
    });
  });

  // View all button
  if (viewAllBtn) {
    viewAllBtn.addEventListener('click', () => {
      const view = viewAllBtn.getAttribute('data-view');
      changeView(view);
    });
  }

  // Process all button
  if (processAllBtn) {
    processAllBtn.addEventListener('click', () => {
      showConfirmationModal('Are you sure you want to process all pending records?', processPendingRecords);
    });
  }

  // Search functionality
  if (searchBtn) {
    searchBtn.addEventListener('click', () => {
      performSearch(searchInput.value);
    });

    searchInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        performSearch(searchInput.value);
      }
    });
  }

  // Quick search functionality
  if (quickSearchInput) {
    quickSearchInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        changeView('search');
        searchInput.value = quickSearchInput.value;
        performSearch(quickSearchInput.value);
        quickSearchInput.value = '';
      }
    });
  }

  // Patients table search
  if (patientsSearchInput) {
    patientsSearchInput.addEventListener('input', (e) => {
      filterPatientsTable(e.target.value);
    });
  }

  // Close modals
  closeModalButtons.forEach(button => {
    button.addEventListener('click', () => {
      patientDetailsModal.classList.remove('active');
      confirmationModal.classList.remove('active');
    });
  });

  // Confirm action
  if (confirmBtn) {
    confirmBtn.addEventListener('click', () => {
      if (currentConfirmAction) {
        currentConfirmAction();
        confirmationModal.classList.remove('active');
      }
    });
  }
}

// Change the current view
function changeView(view) {
  // Update navigation
  navItems.forEach(item => {
    item.classList.remove('active');
    if (item.getAttribute('data-view') === view) {
      item.classList.add('active');
    }
  });

  // Update view sections
  viewSections.forEach(section => {
    section.classList.remove('active');
    if (section.id === `${view}-view`) {
      section.classList.add('active');
    }
  });

  // Update view title
  updateViewTitle(view);

  // Load view-specific data
  loadViewData(view);
}

// Update the view title based on the current view
function updateViewTitle(view) {
  switch (view) {
    case 'dashboard':
      currentViewTitle.textContent = 'Dashboard';
      break;
    case 'patients':
      currentViewTitle.textContent = 'All Patients';
      break;
    case 'pending':
      currentViewTitle.textContent = 'Pending Records';
      break;
    case 'search':
      currentViewTitle.textContent = 'Search Patients';
      break;
    default:
      currentViewTitle.textContent = 'Dashboard';
  }
}

// Load view-specific data
async function loadViewData(view) {
  switch (view) {
    case 'dashboard':
      await loadDashboardData();
      break;
    case 'patients':
      await loadAllPatients();
      break;
    case 'pending':
      await loadPendingRecords();
      break;
    case 'search':
      // Search view doesn't need to load data initially
      break;
  }
}

// Load dashboard data
async function loadDashboardData() {
  try {
    // Load counts
    const [patients, pendingPatients] = await Promise.all([
      fetchPatients(),
      fetchPendingPatients()
    ]);

    // Update stats
    updateStats(patients, pendingPatients);

    // Update recent patients table (show only the most recent 5 patients)
    const recentPatients = patients.sort((a, b) => 
      new Date(b.received_timestamp) - new Date(a.received_timestamp)
    ).slice(0, 5);

    renderPatientsTable(recentPatientsTable, recentPatients, false);
  } catch (error) {
    showToast('Error loading dashboard data', 'error');
    console.error('Error loading dashboard data:', error);
  }
}

// Load all patients
async function loadAllPatients() {
  try {
    const patients = await fetchPatients();
    renderPatientsTable(allPatientsTable, patients, true);
  } catch (error) {
    showToast('Error loading patients', 'error');
    console.error('Error loading patients:', error);
  }
}

// Load pending records
async function loadPendingRecords() {
  try {
    const pendingPatients = await fetchPendingPatients();
    renderPendingTable(pendingPatientsTable, pendingPatients);
  } catch (error) {
    showToast('Error loading pending records', 'error');
    console.error('Error loading pending records:', error);
  }
}

// Render patients table
function renderPatientsTable(tableBody, patients, includeActions = false) {
  if (!patients.length) {
    tableBody.innerHTML = `
      <tr class="no-results-row">
        <td colspan="${includeActions ? 6 : 5}">No patients found</td>
      </tr>
    `;
    return;
  }

  tableBody.innerHTML = '';
  patients.forEach(patient => {
    const receivedDate = formatDate(patient.received_timestamp);
    const row = document.createElement('tr');
    
    row.innerHTML = `
      <td>${patient.details.patient_id}</td>
      <td>${patient.details.full_name}</td>
      <td>${patient.details.birth_date}</td>
      <td>${capitalizeFirstLetter(patient.details.gender)}</td>
      <td>${receivedDate}</td>
      ${includeActions ? `
        <td>
          <button class="table-action-btn view-details" data-patient-id="${patient.details.patient_id}">
            <i class="fas fa-eye"></i> View
          </button>
        </td>
      ` : ''}
    `;

    // Add click event for view details button
    if (includeActions) {
      const viewButton = row.querySelector('.view-details');
      viewButton.addEventListener('click', () => {
        showPatientDetails(patient);
      });
    }

    tableBody.appendChild(row);
  });
}

// Render pending patients table
function renderPendingTable(tableBody, patients) {
  if (!patients.length) {
    tableBody.innerHTML = `
      <tr class="no-results-row">
        <td colspan="4">No pending records found</td>
      </tr>
    `;
    return;
  }

  tableBody.innerHTML = '';
  patients.forEach(patient => {
    const receivedDate = formatDate(patient.received_timestamp);
    const row = document.createElement('tr');
    
    row.innerHTML = `
      <td>${patient.details.patient_id}</td>
      <td>${patient.details.full_name}</td>
      <td>${patient.details.birth_date}</td>
      <td>${receivedDate}</td>
    `;

    tableBody.appendChild(row);
  });
}

// Process pending records
async function processPendingRecords() {
  try {
    const response = await fetch('/api/process-pending', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();
    
    if (response.ok) {
      showToast(data.message, 'success');
      
      // Reload dashboard and pending data
      await Promise.all([
        loadDashboardData(),
        loadPendingRecords()
      ]);
    } else {
      showToast(data.error || 'Failed to process records', 'error');
    }
  } catch (error) {
    showToast('Error processing records', 'error');
    console.error('Error processing records:', error);
  }
}

// Filter the patients table based on search input
function filterPatientsTable(searchTerm) {
  const rows = allPatientsTable.querySelectorAll('tr:not(.no-results-row):not(.loading-row)');
  const term = searchTerm.toLowerCase();
  let hasResults = false;

  rows.forEach(row => {
    const patientId = row.cells[0].textContent.toLowerCase();
    const name = row.cells[1].textContent.toLowerCase();
    const birthDate = row.cells[2].textContent.toLowerCase();
    
    if (patientId.includes(term) || name.includes(term) || birthDate.includes(term)) {
      row.style.display = '';
      hasResults = true;
    } else {
      row.style.display = 'none';
    }
  });

  // Show no results message if needed
  if (!hasResults && rows.length > 0) {
    // Remove any existing no-results-row
    const existingNoResults = allPatientsTable.querySelector('.no-results-row');
    if (existingNoResults) {
      existingNoResults.remove();
    }
    
    const noResultsRow = document.createElement('tr');
    noResultsRow.className = 'no-results-row';
    noResultsRow.innerHTML = `<td colspan="6">No patients matching '${searchTerm}'</td>`;
    allPatientsTable.appendChild(noResultsRow);
  } else {
    // Remove any existing no-results-row
    const existingNoResults = allPatientsTable.querySelector('.no-results-row');
    if (existingNoResults) {
      existingNoResults.remove();
    }
  }
}

// Perform search
async function performSearch(query) {
  if (!query.trim()) {
    searchResultsTable.innerHTML = `
      <tr class="no-results-row">
        <td colspan="5">Enter a search term above</td>
      </tr>
    `;
    resultsCount.textContent = '0 results found';
    return;
  }

  searchResultsTable.innerHTML = `
    <tr class="loading-row">
      <td colspan="5">Searching...</td>
    </tr>
  `;

  try {
    const response = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
    const results = await response.json();

    resultsCount.textContent = `${results.length} results found`;

    if (results.length === 0) {
      searchResultsTable.innerHTML = `
        <tr class="no-results-row">
          <td colspan="5">No patients found matching '${query}'</td>
        </tr>
      `;
      return;
    }

    searchResultsTable.innerHTML = '';
    results.forEach(patient => {
      const row = document.createElement('tr');
      
      row.innerHTML = `
        <td>${patient.details.patient_id}</td>
        <td>${patient.details.full_name}</td>
        <td>${patient.details.birth_date}</td>
        <td>${capitalizeFirstLetter(patient.details.gender)}</td>
        <td>
          <button class="table-action-btn view-details" data-patient-id="${patient.details.patient_id}">
            <i class="fas fa-eye"></i> View
          </button>
        </td>
      `;

      // Add click event for view details button
      const viewButton = row.querySelector('.view-details');
      viewButton.addEventListener('click', () => {
        showPatientDetails(patient);
      });

      searchResultsTable.appendChild(row);
    });
  } catch (error) {
    showToast('Error performing search', 'error');
    console.error('Error performing search:', error);
    searchResultsTable.innerHTML = `
      <tr class="no-results-row">
        <td colspan="5">Error occurred while searching</td>
      </tr>
    `;
  }
}

// Show patient details modal
function showPatientDetails(patient) {
  // Populate modal fields
  document.getElementById('modal-patient-id').textContent = patient.details.patient_id;
  document.getElementById('modal-patient-name').textContent = patient.details.full_name;
  document.getElementById('modal-patient-dob').textContent = patient.details.birth_date;
  document.getElementById('modal-patient-gender').textContent = capitalizeFirstLetter(patient.details.gender);
  document.getElementById('modal-received-date').textContent = formatDate(patient.received_timestamp);
  
  // Format and set FHIR data
  const fhirDataElement = document.getElementById('modal-fhir-data');
  fhirDataElement.textContent = JSON.stringify(patient.details.original_fhir, null, 2);
  
  // Show the modal
  patientDetailsModal.classList.add('active');
}

// Show confirmation modal
function showConfirmationModal(message, confirmAction) {
  confirmationMessage.textContent = message;
  currentConfirmAction = confirmAction;
  confirmationModal.classList.add('active');
}

// Update stats
function updateStats(patients, pendingPatients) {
  // Total patients count
  totalPatientsCount.textContent = patients.length;
  
  // Pending patients count
  pendingPatientsCount.textContent = pendingPatients.length;
  pendingCount.textContent = pendingPatients.length;
  
  // Today's records count
  const today = new Date().toISOString().split('T')[0];
  const todayPatients = patients.filter(patient => 
    patient.received_timestamp.split('T')[0] === today
  );
  todayRecordsCount.textContent = todayPatients.length;
}

// Show toast notification
function showToast(message, type = 'info') {
  const toastContainer = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  toast.innerHTML = `
    <div class="toast-header">
      <span class="toast-title">${getToastTitle(type)}</span>
      <button class="toast-close">&times;</button>
    </div>
    <div class="toast-body">${message}</div>
  `;
  
  // Add close event
  const closeButton = toast.querySelector('.toast-close');
  closeButton.addEventListener('click', () => {
    toast.remove();
  });
  
  // Auto remove after 5 seconds
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 300);
  }, 5000);
}

// Get toast title based on type
function getToastTitle(type) {
  switch (type) {
    case 'success':
      return 'Success';
    case 'error':
      return 'Error';
    case 'warning':
      return 'Warning';
    default:
      return 'Information';
  }
}

// API Functions
async function fetchPatients() {
  const response = await fetch('/api/patients');
  if (!response.ok) {
    throw new Error('Failed to fetch patients');
  }
  return response.json();
}

async function fetchPendingPatients() {
  const response = await fetch('/api/pending');
  if (!response.ok) {
    throw new Error('Failed to fetch pending patients');
  }
  return response.json();
}

// Utility Functions
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleString();
}

function capitalizeFirstLetter(string) {
  if (!string) return '';
  return string.charAt(0).toUpperCase() + string.slice(1);
} 