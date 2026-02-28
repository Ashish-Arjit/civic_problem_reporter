const API_BASE = 'http://localhost:5050';

// DOM Elements
const complaintForm = document.getElementById('complaint-form');
const backendStatus = document.getElementById('backend-status');
const statusText = document.getElementById('status-text');
const complaintsList = document.getElementById('complaints-list');
const complaintCount = document.getElementById('complaint-count');
const refreshBtn = document.getElementById('refresh-btn');
const forceEscalationBtn = document.getElementById('force-escalation-btn');
const checkPendingBtn = document.getElementById('check-pending-btn');
const simulationLog = document.getElementById('simulation-log');
const submitBtn = document.getElementById('submit-btn');

// State
let complaints = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    fetchComplaints();
    // Refresh dashboard every 30 seconds
    setInterval(fetchComplaints, 30000);
});

// Utility: Check Backend Health
async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE}/health`);
        if (res.ok) {
            backendStatus.className = 'status-indicator online';
            statusText.innerText = 'Backend Online';
        } else {
            throw new Error();
        }
    } catch (err) {
        backendStatus.className = 'status-indicator offline';
        statusText.innerText = 'Backend Offline';
        showToast('Cannot connect to backend server.', 'error');
    }
}

// Fetch all complaints (Note: backend doesn't have a /complaints endpoint yet, 
// but for the demo we'll assume it returns all if we can't find specific ones. 
// Standard demo practice: Mock if missing or use existing ones if possible).
// Actually, let's look at the backend - it has /check_pending which returns overdue ones.
// I'll add a quick route to app.py if needed, or just depend on simulated data for dashboard.
// Looking at app.py, it doesn't have a 'get all' endpoint. I should add one for the dashboard.
async function fetchComplaints() {
    try {
        // Since backend is missing /complaints, let's try to get pending ones at least
        // or just show a message. For a demo, I'll update app.py briefly in the next step
        // to support getting all complaints.
        const res = await fetch(`${API_BASE}/get_all_complaints`);
        if (res.ok) {
            const data = await res.json();
            complaints = data;
            renderComplaints();
        }
    } catch (err) {
        console.error('Failed to fetch complaints:', err);
    }
}

function renderComplaints() {
    complaintCount.innerText = complaints.length;
    if (complaints.length === 0) {
        complaintsList.innerHTML = `
            <div class="empty-state">
                <div class="icon">📁</div>
                <p>No complaints submitted yet.</p>
            </div>`;
        return;
    }

    complaintsList.innerHTML = complaints.map(c => `
        <div class="complaint-card animate-in">
            <div class="comp-header">
                <span class="comp-id">#${c.id}</span>
                <span class="status-pill status-${c.status}">${c.status.replace('_', ' ')}</span>
            </div>
            <div class="comp-content">
                <p>${c.username} reported an issue.</p>
            </div>
            <div class="comp-meta">
                <span>📍 ${c.latitude.toFixed(4)}, ${c.longitude.toFixed(4)}</span>
                <span>🔥 ${c.priority}</span>
                <span>📱 ${c.preferred_platform}</span>
            </div>
            ${c.status !== 'Resolved' ? `
                <button class="resolve-btn" onclick="resolveComplaint(${c.id})">Mark Resolved</button>
            ` : ''}
        </div>
    `).join('');
}

// Form Submission
complaintForm.onsubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData();
    formData.append('username', document.getElementById('username').value);
    formData.append('phone', document.getElementById('phone').value);
    formData.append('priority', document.getElementById('priority').value);
    formData.append('preferred_platform', document.getElementById('preferred_platform').value);

    // Mock GPS (Somewhere in a city)
    formData.append('latitude', (28.6139 + (Math.random() - 0.5) * 0.1).toFixed(6));
    formData.append('longitude', (77.2090 + (Math.random() - 0.5) * 0.1).toFixed(6));

    const imageFile = document.getElementById('image').files[0];
    if (imageFile) {
        formData.append('image', imageFile);
    }

    try {
        const res = await fetch(`${API_BASE}/submit`, {
            method: 'POST',
            body: formData
        });

        const data = await res.json();
        if (data.success) {
            showToast('Complaint submitted successfully!');
            complaintForm.reset();
            fetchComplaints();
        } else {
            showToast(data.error || 'Submission failed', 'error');
        }
    } catch (err) {
        showToast('Network error during submission', 'error');
    } finally {
        setLoading(false);
    }
};

// Simulation Controls
forceEscalationBtn.onclick = async () => {
    addLog('System', 'Backdating all pending issues by 50 hours...');
    try {
        const res = await fetch(`${API_BASE}/force_escalation`, { method: 'POST' });
        const data = await res.json();
        addLog('System', data.message || 'Operation complete.');
        fetchComplaints();
    } catch (err) {
        addLog('Error', 'Failed to reach backend.');
    }
};

checkPendingBtn.onclick = async () => {
    addLog('System', 'Initiating automated escalation check...');
    try {
        const res = await fetch(`${API_BASE}/check_pending`);
        const data = await res.json();
        if (data.posted > 0) {
            addLog('Social', `Critical! Simulated ${data.posted} public posts for overdue tasks.`);
            showToast(`Social escalation triggered for ${data.posted} issues!`, 'warning');
        } else {
            addLog('System', 'No overdue complaints found. Everything within SLAs.');
        }
        fetchComplaints();
    } catch (err) {
        addLog('Error', 'Failed to run analysis.');
    }
};

async function resolveComplaint(id) {
    try {
        const res = await fetch(`${API_BASE}/mark_resolved/${id}`, { method: 'POST' });
        if (res.ok) {
            showToast(`Complaint #${id} resolved.`);
            fetchComplaints();
        }
    } catch (err) {
        showToast('Failed to resolve', 'error');
    }
}

// Helpers
function setLoading(loading) {
    submitBtn.disabled = loading;
    submitBtn.querySelector('.btn-text').classList.toggle('hidden', loading);
    submitBtn.querySelector('.loader-dots').classList.toggle('hidden', !loading);
}

function addLog(type, message) {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type.toLowerCase()}`;
    entry.innerText = `[${new Date().toLocaleTimeString()}] ${message}`;
    simulationLog.prepend(entry);
}

function showToast(msg, type = 'success') {
    const toast = document.createElement('div');
    toast.className = 'toast animate-in';
    if (type === 'error') toast.style.borderLeftColor = 'var(--error)';
    if (type === 'warning') toast.style.borderLeftColor = 'var(--accent)';
    toast.innerText = msg;
    document.getElementById('toast-container').appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

refreshBtn.onclick = fetchComplaints;
window.resolveComplaint = resolveComplaint;
