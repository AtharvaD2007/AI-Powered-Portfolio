import React from 'react';
import { Sparkles, Database, FileText, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';

export default function Navbar({ health, onResetSample, isResetting }) {
  const isAiReady = health?.gemini_configured;

  return (
    <header className="app-navbar">
      <div className="navbar-left">
        <h1 className="navbar-page-title">Candidate Portfolio & Career Command Center</h1>
      </div>

      <div className="navbar-right">
        <div className={`status-pill ${isAiReady ? 'status-active' : 'status-notice'}`}>
          <Sparkles size={14} />
          <span>{isAiReady ? 'Gemini AI Active' : 'Heuristic Mode (No API Key)'}</span>
        </div>

        <div className="status-pill status-db">
          <Database size={14} />
          <span>SQLite Primary</span>
        </div>

        <button
          className="btn btn-outline btn-sm reset-btn"
          onClick={onResetSample}
          disabled={isResetting}
          title="Reset database to rich sample candidate with dual Software & Networking projects"
        >
          <RefreshCw size={14} className={isResetting ? 'spin' : ''} />
          <span>{isResetting ? 'Resetting...' : 'Reset Sample Data'}</span>
        </button>
      </div>
    </header>
  );
}
