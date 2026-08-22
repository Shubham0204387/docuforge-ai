// js/app.js

const API_BASE = 'http://localhost:8000/api';

// Helper for authenticated fetch
async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem('access_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };
  const response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
  if (!response.ok) {
    let errorDetail = 'API request failed';
    try {
      const error = await response.json();
      errorDetail = error.detail || error.message || errorDetail;
    } catch(e) {
      // If not JSON, use the status text
      errorDetail = `Error ${response.status}: ${response.statusText}`;
    }
    if (response.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = 'login.html';
    }
    throw new Error(errorDetail);
  }
  return response;
}

// Auth
async function login(email, password) {
  const formData = new URLSearchParams({ username: email, password });
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
  });
  if (!response.ok) throw new Error('Login failed');
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  const payload = JSON.parse(atob(data.access_token.split('.')[1]));
  localStorage.setItem('user_email', payload.sub);
  return data;
}

async function register(userData) {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  });
  if (!response.ok) throw new Error('Registration failed');
  return response.json();
}

async function getCurrentUser() {
  const res = await apiFetch('/auth/me');
  return res.json();
}

async function updateProfile(data) {
  const res = await apiFetch('/auth/me', { method: 'PUT', body: JSON.stringify(data) });
  return res.json();
}

function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_email');
  window.location.href = 'login.html';
}

// Projects
async function getProjects() {
  const res = await apiFetch('/projects');
  return res.json();
}

async function createProject(text) {
  const res = await apiFetch('/process-input', {
    method: 'POST',
    body: JSON.stringify({ text: text })
  });
  return res.json();
}

async function deleteProject(projectId) {
  const res = await apiFetch(`/projects/${projectId}`, { method: 'DELETE' });
  return res.ok;
}

async function getProjectRequirements(projectId) {
  const res = await apiFetch(`/projects/${projectId}/requirements`);
  return res.json();
}

async function updateRequirement(projectId, reqId, data) {
  const res = await apiFetch(`/projects/${projectId}/requirements/${reqId}`, { method: 'PUT', body: JSON.stringify(data) });
  return res.json();
}

async function deleteRequirement(projectId, reqId) {
  const res = await apiFetch(`/projects/${projectId}/requirements/${reqId}`, { method: 'DELETE' });
  return res.ok;
}

// Conflicts
async function getProjectConflicts(projectId, unresolvedOnly = true) {
  const res = await apiFetch(`/conflicts/${projectId}?unresolved_only=${unresolvedOnly}`);
  return res.json();
}

async function detectConflicts(projectId) {
  const res = await apiFetch(`/conflicts/detect/${projectId}`, { method: 'POST' });
  return res.json();
}

async function resolveConflict(conflictId, resolution) {
  const res = await apiFetch(`/conflicts/resolve/${conflictId}?resolution=${encodeURIComponent(resolution)}`, { method: 'POST' });
  return res.json();
}

async function batchResolveConflicts(conflictIds, resolution) {
  const res = await apiFetch(`/conflicts/batch-resolve`, { method: 'POST', body: JSON.stringify({ conflict_ids: conflictIds, resolution }) });
  return res.json();
}

// Quality, Impact, Priorities
async function getProjectQuality(projectId) {
  const res = await apiFetch(`/quality/${projectId}`, { method: 'POST' });
  return res.json();
}

async function getProjectImpact(projectId) {
  const res = await apiFetch(`/impact/${projectId}`, { method: 'POST' });
  return res.json();
}

async function getProjectPriorities(projectId) {
  const res = await apiFetch(`/prioritize/${projectId}`, { method: 'POST' });
  return res.json();
}

// UML
async function generateUML(projectId) {
  const res = await apiFetch(`/uml/generate/${projectId}`, { method: 'POST' });
  return res.json();
}

async function getProjectDiagrams(projectId) {
  const res = await apiFetch(`/uml/project/${projectId}/diagrams`);
  return res.json();
}

async function renderDiagram(diagramId, format = 'png') {
  const res = await apiFetch(`/uml/render/${diagramId}?format=${format}`);
  return res.json();
}

// Documents
async function generateDocuments(projectId) {
  const res = await apiFetch(`/documents/generate/${projectId}`, { method: 'POST' });
  return res.json();
}

async function downloadDocument(projectId, docType, format) {
  const token = localStorage.getItem('access_token');
  const url = `${API_BASE}/documents/download/${projectId}/${docType}/${format}`;
  const response = await fetch(url, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  if (!response.ok) throw new Error('Download failed');
  const blob = await response.blob();
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${docType}_${projectId}.${format}`;
  link.click();
  URL.revokeObjectURL(link.href);
}

// Export
async function exportProjectZip(projectId) {
  const token = localStorage.getItem('access_token');
  const url = `${API_BASE}/export/zip/${projectId}`;
  const response = await fetch(url, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  if (!response.ok) throw new Error('Export failed');
  const blob = await response.blob();
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${projectId}_export.zip`;
  link.click();
  URL.revokeObjectURL(link.href);
}

// NEW: Expand project requirements using inference engine (Module 4)
async function expandProject(projectId) {
  const res = await apiFetch(`/expand-project/${projectId}`, { method: 'POST' });
  return res.json();
}

// Settings
async function getSettings() {
  const res = await apiFetch('/settings');
  return res.json();
}

async function updateSettings(settings) {
  const res = await apiFetch('/settings', {
    method: 'PUT',
    body: JSON.stringify(settings)
  });
  return res.json();
}

// Live UML Editor
async function getDiagramCode(diagramId) {
  const res = await apiFetch(`/uml/render/${diagramId}?format=png`); // We just need code from DB really
  // Actually let's add a proper endpoint for code if needed, but getProjectDiagrams returns partial.
  // UMLService has get_diagram_plantuml but we don't have a route.
  // Let's add the route to main.py later if missing.
  const all = await apiFetch(`/uml/render/${diagramId}`); // Reusing render for now or add get-code
  return res.json();
}

async function updateDiagramCode(diagramId, code) {
  const res = await apiFetch(`/uml/diagrams/${diagramId}`, {
    method: 'PUT',
    body: JSON.stringify({ plantuml_code: code })
  });
  return res.json();
}

async function askChat(projectId, message) {
  const res = await apiFetch(`/chat/${projectId}`, {
    method: 'POST',
    body: JSON.stringify({ message: message })
  });
  return res.json();
}

// Integrations
async function getIntegrationStatus() {
  const res = await apiFetch('/export/status');
  return res.json();
}

async function pushToJira(projectId) {
  const res = await apiFetch(`/integrations/jira/${projectId}`, { method: 'POST' });
  return res.json();
}

async function pushToGit(projectId) {
  const res = await apiFetch(`/integrations/git/${projectId}`, { method: 'POST' });
  return res.json();
}

async function sendSlackNotification(projectId, message) {
  const res = await apiFetch(`/integrations/slack/${projectId}?message=${encodeURIComponent(message)}`, { method: 'POST' });
  return res.json();
}

// Global expose for Alpine.js
window.api = {
  login, register, logout, getCurrentUser, updateProfile,
  getProjects, createProject, deleteProject,
  getProjectRequirements, updateRequirement, deleteRequirement,
  getProjectConflicts, detectConflicts, resolveConflict, batchResolveConflicts,
  getProjectQuality, getProjectImpact, getProjectPriorities,
  generateUML, getProjectDiagrams, renderDiagram,
  updateDiagramCode, // <-- NEW
  generateDocuments, downloadDocument,
  exportProjectZip,
  expandProject,
  askChat, // <-- NEW
  getIntegrationStatus, pushToJira, pushToGit, sendSlackNotification,
  getSettings, updateSettings, // <-- NEW
};