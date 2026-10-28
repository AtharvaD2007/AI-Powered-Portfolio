import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Check,
  RotateCcw,
  History,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  FileText
} from 'lucide-react';
import { api } from '../api/api';

const SAMPLE_RAW_TEXT = `Jordan Miller
jordan.m@example.com
(555) 345-6789
San Francisco, CA
https://github.com/jordanm-dev
https://linkedin.com/in/jordanm-tech

Summary: Full-stack engineer with 3 years building cloud-native applications and microservice backends.

Skills:
- Go
- Kubernetes
- GraphQL
- Redis
- Terraform
- Microservices Architecture

Education:
- UC Berkeley: B.S. in Electrical Engineering & Computer Science (2019 - 2023). GPA 3.75.

Projects:
- Distributed Event Streaming Pipeline: Engineered an event ingestion broker handling 25k msgs/sec using Go and Kafka. Implemented distributed tracing with OpenTelemetry.
- Cloud Container Provisioner: Automated container orchestration and health checks with Kubernetes API.

Experience:
- Stripe: Software Engineering Intern (May 2022 - Aug 2022). Optimized webhook retry backoff algorithms, reducing database deadlocks by 40%.`;

export default function AIOrganizerView({ onRefresh, showToast }) {
  const [rawText, setRawText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [proposedChanges, setProposedChanges] = useState(null);
  const [historyId, setHistoryId] = useState(null);
  const [parseMetadata, setParseMetadata] = useState(null);
  const [isApproving, setIsApproving] = useState(false);
  const [historyList, setHistoryList] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  // Fetch history
  const loadHistory = async () => {
    try {
      const res = await api.getOrganizerHistory();
      if (res.success) {
        setHistoryList(res.data || []);
      }
    } catch (_) {}
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleOrganize = async () => {
    if (!rawText.trim()) {
      showToast('Please paste or write some unstructured text first.', 'error');
      return;
    }
    setIsLoading(true);
    setProposedChanges(null);
    try {
      const res = await api.organizeText(rawText);
      if (res.success) {
        setProposedChanges(res.proposed_changes);
        setHistoryId(res.history_id);
        setParseMetadata({
          source: res.source,
          warning: res.warning,
          message: res.message
        });
        showToast('Text organized! Please review proposed items before saving.', 'success');
        loadHistory();
      } else {
        showToast(res.error || 'Failed to parse text', 'error');
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!proposedChanges) return;
    setIsApproving(true);
    try {
      const res = await api.approveChanges(historyId, proposedChanges);
      if (res.success) {
        showToast(res.message || 'Changes saved to your portfolio!', 'success');
        setProposedChanges(null);
        setRawText('');
        onRefresh();
        loadHistory();
      } else {
        showToast(res.error || 'Approval failed', 'error');
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setIsApproving(false);
    }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">AI Portfolio Organizer</h2>
          <p className="view-subtitle">
            Paste messy notes, LinkedIn text, or resume fragments. Gemini structures them into verified categories for your approval.
          </p>
        </div>
        <button
          className="btn btn-outline"
          onClick={() => setShowHistory(!showHistory)}
        >
          <History size={16} />
          <span>{showHistory ? 'Hide Submission History' : 'View Audit History'}</span>
        </button>
      </div>

      {showHistory && (
        <div className="history-pane-card">
          <h4 className="card-subhead">Preserved Raw Submissions & Audit Log</h4>
          <p className="helper-text">
            All original input is stored permanently in SQLite, guaranteeing that your raw notes and sources are preserved intact.
          </p>
          <div className="history-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Raw Input Excerpt</th>
                  <th>Status</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {historyList.length === 0 ? (
                  <tr><td colSpan={4} className="empty-cell">No prior submissions recorded yet.</td></tr>
                ) : (
                  historyList.map(item => (
                    <tr key={item.id}>
                      <td>#{item.id}</td>
                      <td className="table-code-cell">{item.raw_input.slice(0, 120)}...</td>
                      <td>
                        <span className={`status-pill ${item.status === 'approved' ? 'status-active' : 'status-notice'}`}>
                          {item.status}
                        </span>
                      </td>
                      <td>{item.created_at}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="organizer-split-grid">
        {/* Left: Input */}
        <div className="organizer-card">
          <div className="card-top-bar">
            <h3 className="card-heading">1. Unstructured Information</h3>
            <div className="btn-group-sm">
              <button
                type="button"
                className="btn btn-sm btn-outline"
                onClick={() => setRawText(SAMPLE_RAW_TEXT)}
              >
                Load Sample Text
              </button>
              <button
                type="button"
                className="btn btn-sm btn-outline"
                onClick={() => setRawText('')}
              >
                Clear
              </button>
            </div>
          </div>

          <textarea
            className="raw-textarea"
            rows={15}
            placeholder="Paste raw notes, unformatted bullet points, education, skills, or job duties here...&#10;&#10;Example:&#10;Alex Morgan&#10;Skills: Python, Flask, Redis, Docker, Wireshark, Subnetting&#10;Built an asynchronous task queue handling 1,500 req/s..."
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
          />

          <div className="card-footer-action">
            <button
              className="btn btn-primary btn-block"
              onClick={handleOrganize}
              disabled={isLoading || !rawText.trim()}
            >
              <Sparkles size={18} className={isLoading ? 'spin' : ''} />
              <span>{isLoading ? 'Organizing with Gemini AI...' : 'Organize with AI'}</span>
            </button>
          </div>
        </div>

        {/* Right: Proposal Review */}
        <div className="organizer-card">
          <div className="card-top-bar">
            <h3 className="card-heading">2. Proposed Structured Changes</h3>
            {proposedChanges && (
              <span className="badge-count">Ready for Review</span>
            )}
          </div>

          {!proposedChanges && !isLoading && (
            <div className="empty-state-box">
              <Sparkles size={36} className="empty-icon" />
              <h4>Awaiting Input</h4>
              <p>
                Paste unstructured text on the left and click <strong>Organize with AI</strong>.
                You can review every extracted category before saving it to your verified portfolio.
              </p>
            </div>
          )}

          {isLoading && (
            <div className="loading-state-box">
              <div className="spinner-large" />
              <h4>Gemini AI is analyzing your content...</h4>
              <p>Extracting profile, education, skills, projects, and work experiences.</p>
            </div>
          )}

          {proposedChanges && (
            <div className="proposal-review-wrap">
              {parseMetadata?.warning && (
                <div className="alert-banner warning">
                  <AlertCircle size={16} />
                  <span>{parseMetadata.warning}</span>
                </div>
              )}

              {/* Profile Changes */}
              {proposedChanges.profile && (
                <div className="proposal-section">
                  <h4 className="section-title">Profile & Contact</h4>
                  <div className="proposal-grid">
                    {Object.entries(proposedChanges.profile).map(([key, val]) => val ? (
                      <div key={key} className="prop-item">
                        <span className="prop-k">{key.replace('_', ' ')}:</span>
                        <span className="prop-v">{val}</span>
                      </div>
                    ) : null)}
                  </div>
                </div>
              )}

              {/* Skills Changes */}
              {proposedChanges.skills && proposedChanges.skills.length > 0 && (
                <div className="proposal-section">
                  <h4 className="section-title">Extracted Skills ({proposedChanges.skills.length})</h4>
                  <div className="tags-row">
                    {proposedChanges.skills.map((s, i) => (
                      <span key={i} className="skill-pill">
                        <strong>{s.name}</strong>
                        <small>{s.category}</small>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Projects Changes */}
              {proposedChanges.projects && proposedChanges.projects.length > 0 && (
                <div className="proposal-section">
                  <h4 className="section-title">Extracted Projects ({proposedChanges.projects.length})</h4>
                  {proposedChanges.projects.map((p, i) => (
                    <div key={i} className="prop-card">
                      <strong>{p.title}</strong>
                      <p>{p.description}</p>
                      {p.tech_stack && <span className="tech-badge">{p.tech_stack.join(', ')}</span>}
                    </div>
                  ))}
                </div>
              )}

              {/* Experience Changes */}
              {proposedChanges.experiences && proposedChanges.experiences.length > 0 && (
                <div className="proposal-section">
                  <h4 className="section-title">Extracted Experience ({proposedChanges.experiences.length})</h4>
                  {proposedChanges.experiences.map((exp, i) => (
                    <div key={i} className="prop-card">
                      <strong>{exp.role} @ {exp.company}</strong>
                      <p>{exp.description}</p>
                    </div>
                  ))}
                </div>
              )}

              <div className="proposal-actions-bar">
                <button
                  className="btn btn-outline"
                  onClick={() => setProposedChanges(null)}
                >
                  <RotateCcw size={15} />
                  <span>Discard</span>
                </button>
                <button
                  className="btn btn-primary"
                  onClick={handleApprove}
                  disabled={isApproving}
                >
                  <Check size={16} />
                  <span>{isApproving ? 'Saving...' : 'Approve & Save into Portfolio'}</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
