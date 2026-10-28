import React, { useState, useEffect } from 'react';
import {
  Settings,
  Key,
  Database,
  Table,
  Sparkles,
  Check,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
  Cpu
} from 'lucide-react';
import { api } from '../api/api';

export default function SettingsView({ onResetSample, isResetting, showToast }) {
  const [settings, setSettings] = useState(null);
  const [geminiKeyInput, setGeminiKeyInput] = useState('');
  const [geminiModelInput, setGeminiModelInput] = useState('gemini-2.5-flash');
  const [sheetIdInput, setSheetIdInput] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const res = await api.getSettingsStatus();
      if (res.success) {
        setSettings(res);
        if (res.gemini?.model) setGeminiModelInput(res.gemini.model);
        if (res.google_sheets?.sheet_id) setSheetIdInput(res.google_sheets.sheet_id);
      }
    } catch (_) {}
  };

  const handleSaveRuntimeSettings = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      const payload = {
        gemini_model: geminiModelInput
      };
      if (geminiKeyInput.trim()) {
        payload.gemini_api_key = geminiKeyInput.trim();
      }
      if (sheetIdInput.trim()) {
        payload.google_sheet_id = sheetIdInput.trim();
      }

      const res = await api.updateSettings(payload);
      if (res.success) {
        showToast('Settings saved for this session!', 'success');
        setGeminiKeyInput('');
        loadSettings();
      } else {
        showToast(res.error || 'Failed to save settings', 'error');
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">System Settings & Configuration</h2>
          <p className="view-subtitle">
            Configure external API keys, inspect service health, and manage SQLite database states.
          </p>
        </div>
      </div>

      <div className="settings-cards-grid">
        {/* Gemini AI Config */}
        <div className="settings-card">
          <div className="card-top-bar">
            <div className="card-title-group">
              <Sparkles size={18} className="settings-icon ai" />
              <h3 className="card-heading">Google Gemini AI Engine</h3>
            </div>
            <span className={`status-pill ${settings?.gemini?.configured ? 'status-active' : 'status-notice'}`}>
              {settings?.gemini?.configured ? 'Connected' : 'Fallback Heuristic'}
            </span>
          </div>

          <p className="helper-text">
            Powers the AI Portfolio Organizer and Job Description Analyzer using the official Google GenAI Python SDK.
            When an API key is not configured, a smart deterministic NLP heuristic engine handles parsing transparently.
          </p>

          <form onSubmit={handleSaveRuntimeSettings} className="settings-form">
            <div className="form-group">
              <label>Gemini API Key</label>
              <input
                type="password"
                placeholder={settings?.gemini?.masked_key ? `Current: ${settings.gemini.masked_key}` : 'Paste AI Studio API key...'}
                value={geminiKeyInput}
                onChange={(e) => setGeminiKeyInput(e.target.value)}
              />
              <small className="field-hint">
                Get your free API key at <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer">Google AI Studio</a>.
              </small>
            </div>

            <div className="form-group">
              <label>Gemini Model</label>
              <select
                value={geminiModelInput}
                onChange={(e) => setGeminiModelInput(e.target.value)}
              >
                <option value="gemini-2.5-flash">gemini-2.5-flash (Recommended, Fast & Accurate)</option>
                <option value="gemini-1.5-flash">gemini-1.5-flash</option>
                <option value="gemini-1.5-pro">gemini-1.5-pro (Deep reasoning)</option>
              </select>
            </div>

            <div className="form-group">
              <label>Target Google Sheet ID</label>
              <input
                type="text"
                placeholder="e.g. 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
                value={sheetIdInput}
                onChange={(e) => setSheetIdInput(e.target.value)}
              />
              <small className="field-hint">
                Extracted from your sheet URL: <code>https://docs.google.com/spreadsheets/d/&lt;SHEET_ID&gt;/edit</code>
              </small>
            </div>

            <button type="submit" className="btn btn-primary" disabled={isSaving}>
              <Check size={16} />
              <span>{isSaving ? 'Updating...' : 'Save Settings'}</span>
            </button>
          </form>
        </div>

        {/* Database & Sample Data Management */}
        <div className="settings-card">
          <div className="card-top-bar">
            <div className="card-title-group">
              <Database size={18} className="settings-icon db" />
              <h3 className="card-heading">SQLite Primary Database</h3>
            </div>
            <span className="status-pill status-active">Operational</span>
          </div>

          <p className="helper-text">
            CareerMatrix stores all candidate information in a local, relational SQLite database (<code>backend/data/portfolio.db</code>).
            No data is modified during resume generation.
          </p>

          <div className="db-info-box">
            <div className="db-info-row">
              <span className="db-k">Database Engine:</span>
              <span className="db-v">SQLite 3 (Row Factory, Parameterized Queries)</span>
            </div>
            <div className="db-info-row">
              <span className="db-k">Database Path:</span>
              <span className="db-v"><code>{settings?.database?.path || 'backend/data/portfolio.db'}</code></span>
            </div>
            <div className="db-info-row">
              <span className="db-k">Sample Candidate:</span>
              <span className="db-v">Alex Morgan (Software Development + Networking)</span>
            </div>
          </div>

          <div className="danger-zone-box">
            <h4 className="danger-zone-title">Reset to Clean Sample Candidate</h4>
            <p className="danger-zone-desc">
              Resetting will restore the full dual-track portfolio of Alex Morgan (Junior Backend Developer & Network Support Specialist) along with the two sample job descriptions.
            </p>
            <button
              className="btn btn-secondary btn-block"
              onClick={onResetSample}
              disabled={isResetting}
            >
              <RefreshCw size={15} className={isResetting ? 'spin' : ''} />
              <span>{isResetting ? 'Restoring Sample Data...' : 'Reset to Sample Data'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
