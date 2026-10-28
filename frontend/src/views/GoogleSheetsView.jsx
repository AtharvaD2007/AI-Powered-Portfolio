import React, { useState, useEffect } from 'react';
import {
  Table,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  RefreshCw,
  Share2,
  Database,
  ArrowRight,
  Layers,
  FileSpreadsheet
} from 'lucide-react';
import { api } from '../api/api';

export default function GoogleSheetsView({ showToast }) {
  const [status, setStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isTesting, setIsTesting] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [exportPreview, setExportPreview] = useState(null);
  const [selectedPreviewTab, setSelectedPreviewTab] = useState('Profile');

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    setIsLoading(true);
    try {
      const res = await api.getSheetsStatus();
      if (res.success && res.status) {
        setStatus(res.status);
      }
    } catch (_) {}
    finally {
      setIsLoading(false);
    }
  };

  const handleTestConnection = async () => {
    setIsTesting(true);
    try {
      const res = await api.testSheetsConnection();
      if (res.success) {
        showToast(res.message || 'Connected to Google Sheets!', 'success');
      } else {
        showToast(res.error || 'Connection test failed', 'error');
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setIsTesting(false);
    }
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const res = await api.exportToSheets();
      if (res.success) {
        showToast(res.message || 'Successfully exported portfolio tabs to Google Sheets!', 'success');
        loadStatus();
      } else if (res.is_dry_run) {
        setExportPreview(res.preview);
        showToast('Generated export preview. Configure Google credentials in .env to sync live.', 'info');
      } else {
        showToast(res.error || 'Export failed', 'error');
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setIsExporting(false);
    }
  };

  const tabNames = ['Profile', 'Education', 'Skills', 'Certifications', 'Projects', 'Experience', 'Achievements'];

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">Google Sheets Integration</h2>
          <p className="view-subtitle">
            Export your structured portfolio into 7 dedicated Google Sheet tabs for collaborative review, backup, or HR sharing.
          </p>
        </div>
        <div className="btn-group-sm">
          <button className="btn btn-outline" onClick={handleTestConnection} disabled={isTesting}>
            <RefreshCw size={15} className={isTesting ? 'spin' : ''} />
            <span>Test Connection</span>
          </button>
          <button className="btn btn-primary" onClick={handleExport} disabled={isExporting}>
            <FileSpreadsheet size={16} className={isExporting ? 'spin' : ''} />
            <span>{isExporting ? 'Syncing...' : 'Export to Google Sheets'}</span>
          </button>
        </div>
      </div>

      {/* Integration Status Card */}
      <div className="sheets-status-grid">
        <div className="status-metric-card">
          <div className="status-head">
            <span className="status-label">Primary Master Database</span>
            <span className="status-pill status-active">Active</span>
          </div>
          <h3 className="metric-title">SQLite (portfolio.db)</h3>
          <p className="metric-desc">
            All portfolio records are authored and managed locally in SQLite. Google Sheets serves as an export/synchronization destination.
          </p>
        </div>

        <div className="status-metric-card">
          <div className="status-head">
            <span className="status-label">Google Sheets API Status</span>
            <span className={`status-pill ${status?.configured ? 'status-active' : 'status-notice'}`}>
              {status?.configured ? 'Connected' : 'Pending Configuration'}
            </span>
          </div>
          <h3 className="metric-title">{status?.sheet_id ? `Sheet ID: ${status.sheet_id.slice(0, 14)}...` : 'No Sheet ID Set'}</h3>
          <div className="metric-service-account">
            Service Account: <code>{status?.service_account_email || 'Not Configured'}</code>
          </div>
          {status?.sheet_url && (
            <a href={status.sheet_url} target="_blank" rel="noopener noreferrer" className="sheet-link">
              <span>Open Google Sheet</span>
              <ExternalLink size={13} />
            </a>
          )}
        </div>
      </div>

      {/* 7 Tabs Architecture Card */}
      <div className="sheets-tabs-overview-card">
        <div className="card-top-bar">
          <div>
            <h3 className="card-heading">Exported Spreadsheet Tabs</h3>
            <p className="helper-text">When synchronized, our engine automatically formats and populates these 7 distinct worksheets:</p>
          </div>
          {status?.last_sync && (
            <div className="last-sync-badge">
              Last Synced: {status.last_sync.timestamp} ({status.last_sync.status})
            </div>
          )}
        </div>

        <div className="tabs-nav-bar">
          {tabNames.map((tab) => (
            <button
              key={tab}
              className={`sheet-tab-btn ${selectedPreviewTab === tab ? 'active' : ''}`}
              onClick={() => setSelectedPreviewTab(tab)}
            >
              <FileSpreadsheet size={14} />
              <span>{tab}</span>
            </button>
          ))}
        </div>

        {/* Tab Preview Data Table */}
        <div className="sheet-preview-pane">
          <div className="sheet-preview-header">
            <h4>Worksheet Preview: <code>{selectedPreviewTab}</code></h4>
            <span className="preview-tag">ATS Formatted Grid</span>
          </div>

          <div className="spreadsheet-mock-table-wrap">
            {exportPreview && exportPreview[selectedPreviewTab] ? (
              <table className="spreadsheet-table">
                <tbody>
                  {exportPreview[selectedPreviewTab].map((row, rIdx) => (
                    <tr key={rIdx} className={rIdx === 0 ? 'table-header-row' : ''}>
                      <td className="row-number-col">{rIdx + 1}</td>
                      {row.map((cell, cIdx) => (
                        <td key={cIdx}>{cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="spreadsheet-placeholder">
                <p>Click <strong>Export to Google Sheets</strong> to populate and review live worksheet rows.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Setup Guide Accordion */}
      <div className="setup-guide-card">
        <div className="setup-guide-header">
          <Share2 size={20} />
          <div>
            <h4 className="guide-title">Google Service Account & Sheet Sharing Instructions</h4>
            <p className="guide-sub">Follow these 4 steps to link your personal Google Drive spreadsheet with the app.</p>
          </div>
        </div>

        <div className="guide-steps-list">
          <div className="guide-step-item">
            <span className="step-num">1</span>
            <div className="step-body">
              <strong>Create Google Cloud Credentials:</strong>
              <p>Go to <a href="https://console.cloud.google.com" target="_blank" rel="noreferrer">Google Cloud Console</a>, create a project, and enable both the <strong>Google Sheets API</strong> and <strong>Google Drive API</strong>.</p>
            </div>
          </div>

          <div className="guide-step-item">
            <span className="step-num">2</span>
            <div className="step-body">
              <strong>Create a Service Account:</strong>
              <p>Under IAM & Admin &gt; Service Accounts, create a new service account and generate a <strong>JSON key file</strong>.</p>
            </div>
          </div>

          <div className="guide-step-item">
            <span className="step-num">3</span>
            <div className="step-body">
              <strong>Share Your Google Sheet (Critical):</strong>
              <p>Open your target Google Sheet, click <strong>Share</strong>, paste your Service Account's <code>client_email</code> address, and grant it <strong>Editor</strong> permissions.</p>
            </div>
          </div>

          <div className="guide-step-item">
            <span className="step-num">4</span>
            <div className="step-body">
              <strong>Configure Environment:</strong>
              <p>Add <code>GOOGLE_SHEETS_CREDENTIALS_JSON=backend/service_account.json</code> and <code>GOOGLE_SHEET_ID=your_id</code> in <code>backend/.env</code> or enter them in the Settings tab.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
