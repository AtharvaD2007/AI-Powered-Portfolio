/**
 * Centralized API client for AI Portfolio & Resume Generator.
 */

const BASE_URL = '/api';

async function handleResponse(response) {
  if (!response.ok) {
    let errorMsg = `Server responded with status ${response.status}`;
    try {
      const data = await response.json();
      if (data && data.error) {
        errorMsg = data.error;
      }
    } catch (_) {}
    throw new Error(errorMsg);
  }
  return response.json();
}

export const api = {
  // Health
  async getHealth() {
    const res = await fetch(`${BASE_URL}/health`);
    return handleResponse(res);
  },

  // Portfolio
  async getPortfolio() {
    const res = await fetch(`${BASE_URL}/portfolio`);
    return handleResponse(res);
  },

  async resetToSample() {
    const res = await fetch(`${BASE_URL}/portfolio/reset-sample`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    return handleResponse(res);
  },

  async updateProfile(profileData) {
    const res = await fetch(`${BASE_URL}/portfolio/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profileData)
    });
    return handleResponse(res);
  },

  // Category generic helpers: 'education', 'skills', 'certifications', 'projects', 'experiences', 'achievements'
  async addItem(category, itemData) {
    const res = await fetch(`${BASE_URL}/portfolio/${category}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(itemData)
    });
    return handleResponse(res);
  },

  async updateItem(category, itemId, itemData) {
    const res = await fetch(`${BASE_URL}/portfolio/${category}/${itemId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(itemData)
    });
    return handleResponse(res);
  },

  async deleteItem(category, itemId) {
    const res = await fetch(`${BASE_URL}/portfolio/${category}/${itemId}`, {
      method: 'DELETE'
    });
    return handleResponse(res);
  },

  // AI Organizer
  async organizeText(text) {
    const res = await fetch(`${BASE_URL}/ai/organize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    return handleResponse(res);
  },

  async approveChanges(historyId, approvedData) {
    const res = await fetch(`${BASE_URL}/ai/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ history_id: historyId, approved_data: approvedData })
    });
    return handleResponse(res);
  },

  async getOrganizerHistory() {
    const res = await fetch(`${BASE_URL}/ai/history`);
    return handleResponse(res);
  },

  // Job Analyzer
  async getJobs() {
    const res = await fetch(`${BASE_URL}/analyzer/jobs`);
    return handleResponse(res);
  },

  async saveJob(jobData) {
    const res = await fetch(`${BASE_URL}/analyzer/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(jobData)
    });
    return handleResponse(res);
  },

  async matchJob(jobPayload) {
    const res = await fetch(`${BASE_URL}/analyzer/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(jobPayload)
    });
    return handleResponse(res);
  },

  // Resumes
  async getResumes() {
    const res = await fetch(`${BASE_URL}/resumes`);
    return handleResponse(res);
  },

  async getResume(id) {
    const res = await fetch(`${BASE_URL}/resumes/${id}`);
    return handleResponse(res);
  },

  async generateSummary(payload) {
    const res = await fetch(`${BASE_URL}/resumes/generate-summary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  async previewResume(payload) {
    const res = await fetch(`${BASE_URL}/resumes/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  async saveResume(payload) {
    const res = await fetch(`${BASE_URL}/resumes/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  async downloadResumePdf(payload) {
    const res = await fetch(`${BASE_URL}/resumes/download-pdf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      throw new Error(`Failed to generate PDF (${res.status})`);
    }
    const blob = await res.blob();
    return blob;
  },

  // Google Sheets
  async getSheetsStatus() {
    const res = await fetch(`${BASE_URL}/sheets/status`);
    return handleResponse(res);
  },

  async testSheetsConnection() {
    const res = await fetch(`${BASE_URL}/sheets/test`, {
      method: 'POST'
    });
    return handleResponse(res);
  },

  async exportToSheets() {
    const res = await fetch(`${BASE_URL}/sheets/export`, {
      method: 'POST'
    });
    return handleResponse(res);
  },

  // Settings
  async getSettingsStatus() {
    const res = await fetch(`${BASE_URL}/settings/status`);
    return handleResponse(res);
  },

  async updateSettings(settings) {
    const res = await fetch(`${BASE_URL}/settings/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    });
    return handleResponse(res);
  }
};
