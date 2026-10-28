import React, { useState, useEffect } from 'react';
import {
  Target,
  Sparkles,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Layers,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Network,
  HelpCircle
} from 'lucide-react';
import { api } from '../api/api';

export default function JobAnalyzerView({ preselectedJobId, onNavigateToResume, showToast }) {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(preselectedJobId || null);
  const [jobTitle, setJobTitle] = useState('');
  const [jobCompany, setJobCompany] = useState('');
  const [jobText, setJobText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);

  // Load sample/saved jobs
  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const res = await api.getJobs();
      if (res.success && res.data) {
        setJobs(res.data);
        if (preselectedJobId) {
          const match = res.data.find(j => j.id === preselectedJobId);
          if (match) {
            handleSelectJob(match);
          }
        } else if (res.data.length > 0 && !selectedJobId) {
          handleSelectJob(res.data[0]);
        }
      }
    } catch (_) {}
  };

  const handleSelectJob = (job) => {
    setSelectedJobId(job.id);
    setJobTitle(job.title);
    setJobCompany(job.company || '');
    setJobText(job.raw_text);
    setAnalysis(null);
  };

  const handleRunAnalysis = async () => {
    if (!jobText.trim()) {
      showToast('Please provide a job description to analyze.', 'error');
      return;
    }
    setIsAnalyzing(true);
    setAnalysis(null);
    try {
      const res = await api.matchJob({
        job_id: selectedJobId,
        title: jobTitle,
        raw_text: jobText
      });
      if (res.success && res.analysis) {
        setAnalysis(res.analysis);
        showToast('Job analysis complete!', 'success');
      } else {
        showToast(res.error || 'Analysis failed', 'error');
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">Job Description Analyzer</h2>
          <p className="view-subtitle">
            Evaluate job postings against your verified portfolio. Get transparent match scores, discover missing skills, and receive project recommendations.
          </p>
        </div>
      </div>

      {/* Sample Job Presets Bar */}
      <div className="sample-jobs-bar">
        <span className="bar-label">1-Click Demonstrations:</span>
        <div className="sample-job-buttons">
          {jobs.map((job) => (
            <button
              key={job.id}
              className={`sample-job-btn ${selectedJobId === job.id ? 'active' : ''}`}
              onClick={() => handleSelectJob(job)}
            >
              {job.title.includes('Backend') ? <Cpu size={15} /> : <Network size={15} />}
              <span>{job.title}</span>
              <small>({job.company})</small>
            </button>
          ))}
          <button
            className={`sample-job-btn ${selectedJobId === 'custom' ? 'active' : ''}`}
            onClick={() => {
              setSelectedJobId('custom');
              setJobTitle('');
              setJobCompany('');
              setJobText('');
              setAnalysis(null);
            }}
          >
            <Target size={15} />
            <span>+ Custom Job Posting</span>
          </button>
        </div>
      </div>

      <div className="analyzer-layout-grid">
        {/* Left: Job Input */}
        <div className="analyzer-input-card">
          <div className="card-top-bar">
            <h3 className="card-heading">Target Job Posting</h3>
          </div>

          <div className="form-group">
            <label>Role Title</label>
            <input
              type="text"
              placeholder="e.g. Junior Backend Developer"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Company / Organization</label>
            <input
              type="text"
              placeholder="e.g. TechCorp"
              value={jobCompany}
              onChange={(e) => setJobCompany(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Job Description Requirements & Duties *</label>
            <textarea
              rows={16}
              className="job-textarea"
              placeholder="Paste full job description requirements here..."
              value={jobText}
              onChange={(e) => setJobText(e.target.value)}
            />
          </div>

          <button
            className="btn btn-primary btn-block"
            onClick={handleRunAnalysis}
            disabled={isAnalyzing || !jobText.trim()}
          >
            <Sparkles size={18} className={isAnalyzing ? 'spin' : ''} />
            <span>{isAnalyzing ? 'Analyzing Alignment...' : 'Analyze Job Alignment'}</span>
          </button>
        </div>

        {/* Right: Analysis Results */}
        <div className="analyzer-result-card">
          {!analysis && !isAnalyzing && (
            <div className="empty-state-box">
              <Target size={42} className="empty-icon" />
              <h4>Ready for Analysis</h4>
              <p>
                Select one of the sample jobs above or paste a custom description, then click <strong>Analyze Job Alignment</strong>.
              </p>
            </div>
          )}

          {isAnalyzing && (
            <div className="loading-state-box">
              <div className="spinner-large" />
              <h4>Matching against your verified portfolio...</h4>
              <p>Evaluating required skills, cross-referencing project tech stacks, and scoring alignment.</p>
            </div>
          )}

          {analysis && (
            <div className="analysis-content-wrap">
              {/* Score Header */}
              <div className="score-summary-banner">
                <div className="score-circle-box">
                  <div className="score-number">{analysis.overall_score}%</div>
                  <div className="score-label">Match Score</div>
                </div>
                <div className="score-details-right">
                  <div className="score-role-badge">Target Role: {analysis.target_role}</div>
                  <h4 className="score-title">
                    {analysis.overall_score >= 80 ? 'Exceptional Fit' : analysis.overall_score >= 60 ? 'Strong Potential' : 'Moderate Fit'}
                  </h4>
                  <p className="score-expl">{analysis.score_breakdown?.explanation}</p>
                  
                  {/* Score breakdown metrics */}
                  <div className="breakdown-mini-row">
                    <span className="breakdown-chip">
                      Required Skills: <strong>{analysis.score_breakdown?.required_skills_earned} / {analysis.score_breakdown?.required_skills_weight} pts</strong>
                    </span>
                    <span className="breakdown-chip">
                      Bonus Tech: <strong>{analysis.score_breakdown?.preferred_skills_earned} / {analysis.score_breakdown?.preferred_skills_weight} pts</strong>
                    </span>
                    <span className="breakdown-chip">
                      Project Relevance: <strong>{analysis.score_breakdown?.experience_alignment_earned} / {analysis.score_breakdown?.experience_alignment_weight} pts</strong>
                    </span>
                  </div>
                </div>
              </div>

              {/* Ethical Notice Banner */}
              <div className="ethical-badge-banner">
                <ShieldCheck size={18} />
                <span>{analysis.ethical_notice}</span>
              </div>

              {/* Skills Analysis Split */}
              <div className="skills-match-grid">
                {/* Matched Required Skills */}
                <div className="match-column matched">
                  <div className="column-head">
                    <CheckCircle2 size={16} />
                    <span>Verified Matched Skills ({analysis.skills_analysis?.matched_required?.length || 0})</span>
                  </div>
                  <div className="match-pills-list">
                    {analysis.skills_analysis?.matched_required?.map((m, idx) => (
                      <div key={idx} className="match-item-pill verified">
                        <span className="pill-name">{m.job_skill}</span>
                        {m.matched_with && m.matched_with.toLowerCase() !== m.job_skill.toLowerCase() && (
                          <small className="pill-alias">via {m.matched_with}</small>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Missing Skills */}
                <div className="match-column missing">
                  <div className="column-head">
                    <XCircle size={16} />
                    <span>Missing from Verified Portfolio ({analysis.skills_analysis?.missing_required?.length || 0})</span>
                  </div>
                  <div className="match-pills-list">
                    {analysis.skills_analysis?.missing_required?.length === 0 ? (
                      <p className="clean-match-note">All essential requirements are satisfied by your portfolio!</p>
                    ) : (
                      analysis.skills_analysis?.missing_required?.map((sk, idx) => (
                        <div key={idx} className="match-item-pill missing">
                          <span className="pill-name">{sk}</span>
                          <span className="pill-status">Unverified</span>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>

              {/* Recommended Projects */}
              <div className="analysis-section-block">
                <div className="block-header">
                  <Layers size={18} />
                  <h4>Recommended Portfolio Projects to Feature</h4>
                </div>
                <div className="recommended-projects-list">
                  {analysis.recommended_projects?.slice(0, 3).map((rec, i) => (
                    <div key={i} className="rec-project-card">
                      <div className="rec-project-top">
                        <span className="rec-rank">#{i + 1} Best Match</span>
                        <h5 className="rec-title">{rec.title}</h5>
                      </div>
                      <p className="rec-reason">{rec.recommendation_reason}</p>
                      {rec.tech_stack && (
                        <div className="tags-row">
                          {rec.tech_stack.map((t, ti) => (
                            <span key={ti} className="tech-badge">{t}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Call to action: Generate Tailored Resume */}
              <div className="resume-cta-box">
                <div>
                  <h4>Ready to tailor your resume for this position?</h4>
                  <p>Our Resume Studio will pre-select your matching skills and recommended projects.</p>
                </div>
                <button
                  className="btn btn-primary"
                  onClick={() => onNavigateToResume({
                    jobId: selectedJobId,
                    jobTitle: analysis.target_role,
                    jobText: jobText,
                    recommendedProjectIds: analysis.recommended_projects?.map(p => p.project_id) || []
                  })}
                >
                  <span>Build Tailored Resume</span>
                  <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
