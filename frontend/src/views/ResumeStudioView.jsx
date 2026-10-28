import React, { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  Save,
  Sparkles,
  Check,
  Eye,
  CheckSquare,
  Square,
  History,
  ShieldCheck,
  Cpu,
  Network,
  ExternalLink,
  Layers,
  Briefcase,
  GraduationCap,
  Award
} from 'lucide-react';
import { api } from '../api/api';

export default function ResumeStudioView({ portfolio, resumeContext, showToast }) {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [targetRole, setTargetRole] = useState(resumeContext?.jobTitle || 'Junior Backend Developer');
  const [resumeTitle, setResumeTitle] = useState('Junior Backend Developer - Tailored Resume');
  const [customSummary, setCustomSummary] = useState(portfolio?.profile?.summary || '');
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [savedResumes, setSavedResumes] = useState([]);
  const [showSavedModal, setShowSavedModal] = useState(false);

  // Checkbox selections for verified records
  const [selectedSkills, setSelectedSkills] = useState(new Set());
  const [selectedProjects, setSelectedProjects] = useState(new Set());
  const [selectedExperiences, setSelectedExperiences] = useState(new Set());
  const [selectedEducation, setSelectedEducation] = useState(new Set());
  const [selectedCerts, setSelectedCerts] = useState(new Set());
  const [selectedAchievements, setSelectedAchievements] = useState(new Set());

  // Load jobs and saved resumes on mount
  useEffect(() => {
    loadJobs();
    loadSavedResumes();
  }, []);

  // Update selections when portfolio loads or resumeContext changes
  useEffect(() => {
    if (!portfolio) return;

    if (resumeContext?.jobTitle) {
      setTargetRole(resumeContext.jobTitle);
      setResumeTitle(`${resumeContext.jobTitle} - Tailored Resume`);
      autoSelectForRole(resumeContext.jobTitle, resumeContext.recommendedProjectIds);
    } else {
      // Default to Backend Developer track initially
      autoSelectForRole('Junior Backend Developer');
    }
  }, [portfolio, resumeContext]);

  const loadJobs = async () => {
    try {
      const res = await api.getJobs();
      if (res.success && res.data) {
        setJobs(res.data);
        if (resumeContext?.jobId) {
          const matched = res.data.find(j => j.id === resumeContext.jobId);
          if (matched) setSelectedJob(matched);
        } else if (res.data.length > 0) {
          setSelectedJob(res.data[0]);
        }
      }
    } catch (_) {}
  };

  const loadSavedResumes = async () => {
    try {
      const res = await api.getResumes();
      if (res.success && res.data) {
        setSavedResumes(res.data);
      }
    } catch (_) {}
  };

  const autoSelectForRole = (roleTitle, recommendedProjectIds = []) => {
    if (!portfolio) return;

    const lowerRole = roleTitle.toLowerCase();
    const isNetworking = lowerRole.includes('network');

    // Skills auto-selection
    const skillIds = new Set();
    portfolio.skills?.forEach(s => {
      const cat = s.category.toLowerCase();
      if (isNetworking) {
        if (cat.includes('networking') || cat.includes('tools') || s.name.includes('Python') || s.name.includes('Bash')) {
          skillIds.add(s.id);
        }
      } else {
        // Backend
        if (cat.includes('backend') || cat.includes('language') || cat.includes('database') || cat.includes('devops')) {
          skillIds.add(s.id);
        }
      }
    });
    setSelectedSkills(skillIds);

    // Projects auto-selection
    const projIds = new Set();
    if (recommendedProjectIds && recommendedProjectIds.length > 0) {
      recommendedProjectIds.forEach(id => projIds.add(id));
    } else {
      portfolio.projects?.forEach(p => {
        const text = `${p.title} ${p.tech_stack} ${p.description}`.toLowerCase();
        if (isNetworking && (text.includes('network') || text.includes('vlan') || text.includes('packet') || text.includes('cisco'))) {
          projIds.add(p.id);
        } else if (!isNetworking && (text.includes('queue') || text.includes('api') || text.includes('microservice') || text.includes('flask'))) {
          projIds.add(p.id);
        }
      });
    }
    setSelectedProjects(projIds);

    // Experiences auto-selection
    const expIds = new Set();
    portfolio.experiences?.forEach(e => {
      const text = `${e.role} ${e.company} ${e.description}`.toLowerCase();
      if (isNetworking && text.includes('network')) {
        expIds.add(e.id);
      } else if (!isNetworking && text.includes('backend')) {
        expIds.add(e.id);
      } else {
        // Default include both if small list
        expIds.add(e.id);
      }
    });
    setSelectedExperiences(expIds);

    // Education, Certifications & Achievements default to all verified
    setSelectedEducation(new Set(portfolio.education?.map(e => e.id) || []));
    
    // Select relevant certifications
    const certIds = new Set();
    portfolio.certifications?.forEach(c => {
      if (isNetworking && c.name.includes('CCNA')) {
        certIds.add(c.id);
      } else if (!isNetworking && (c.name.includes('Python') || c.name.includes('AWS'))) {
        certIds.add(c.id);
      } else {
        certIds.add(c.id);
      }
    });
    setSelectedCerts(certIds);
    setSelectedAchievements(new Set(portfolio.achievements?.map(a => a.id) || []));
  };

  const handleSwitchJobPreset = (job) => {
    setSelectedJob(job);
    setTargetRole(job.target_role || job.title);
    setResumeTitle(`${job.target_role || job.title} - Tailored Resume`);
    autoSelectForRole(job.target_role || job.title);
  };

  const toggleItem = (setFunc, currentSet, id) => {
    const updated = new Set(currentSet);
    if (updated.has(id)) {
      updated.delete(id);
    } else {
      updated.add(id);
    }
    setFunc(updated);
  };

  const toggleAll = (setFunc, allIds, currentSet) => {
    if (currentSet.size === allIds.length) {
      setFunc(new Set());
    } else {
      setFunc(new Set(allIds));
    }
  };

  // Generate Tailored Summary
  const handleGenerateSummary = async () => {
    setIsGeneratingSummary(true);
    try {
      const selectedItemsPayload = {
        education_ids: Array.from(selectedEducation),
        skill_ids: Array.from(selectedSkills),
        project_ids: Array.from(selectedProjects),
        experience_ids: Array.from(selectedExperiences),
        certification_ids: Array.from(selectedCerts),
        achievement_ids: Array.from(selectedAchievements)
      };

      const res = await api.generateSummary({
        target_role: targetRole,
        job_description: selectedJob?.raw_text || '',
        selected_items: selectedItemsPayload
      });

      if (res.success && res.summary) {
        setCustomSummary(res.summary);
        showToast('Tailored summary generated using verified portfolio data!', 'success');
      } else {
        showToast('Failed to generate summary', 'error');
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setIsGeneratingSummary(false);
    }
  };

  // Download PDF
  const handleDownloadPdf = async () => {
    setIsDownloading(true);
    try {
      const payload = {
        target_role: targetRole,
        custom_summary: customSummary,
        selected_items: {
          education_ids: Array.from(selectedEducation),
          skill_ids: Array.from(selectedSkills),
          project_ids: Array.from(selectedProjects),
          experience_ids: Array.from(selectedExperiences),
          certification_ids: Array.from(selectedCerts),
          achievement_ids: Array.from(selectedAchievements)
        }
      };

      const blob = await api.downloadResumePdf(payload);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const candidateName = (portfolio?.profile?.full_name || 'Resume').replace(/\s+/g, '_');
      const roleSlug = targetRole.replace(/\s+/g, '_');
      link.download = `${candidateName}_${roleSlug}_Resume.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      showToast('ATS-optimized PDF downloaded!', 'success');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setIsDownloading(false);
    }
  };

  // Save Resume Version
  const handleSaveResume = async () => {
    setIsSaving(true);
    try {
      const payload = {
        title: resumeTitle,
        target_role: targetRole,
        job_description_id: selectedJob?.id || null,
        custom_summary: customSummary,
        selected_items: {
          education_ids: Array.from(selectedEducation),
          skill_ids: Array.from(selectedSkills),
          project_ids: Array.from(selectedProjects),
          experience_ids: Array.from(selectedExperiences),
          certification_ids: Array.from(selectedCerts),
          achievement_ids: Array.from(selectedAchievements)
        }
      };

      const res = await api.saveResume(payload);
      if (res.success) {
        showToast('Resume version saved to database!', 'success');
        loadSavedResumes();
      } else {
        showToast(res.error || 'Failed to save', 'error');
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setIsSaving(false);
    }
  };

  // Computed live filtered records for preview
  const previewSkills = portfolio?.skills?.filter(s => selectedSkills.has(s.id)) || [];
  const previewProjects = portfolio?.projects?.filter(p => selectedProjects.has(p.id)) || [];
  const previewExperiences = portfolio?.experiences?.filter(e => selectedExperiences.has(e.id)) || [];
  const previewEducation = portfolio?.education?.filter(e => selectedEducation.has(e.id)) || [];
  const previewCerts = portfolio?.certifications?.filter(c => selectedCerts.has(c.id)) || [];
  const previewAchievements = portfolio?.achievements?.filter(a => selectedAchievements.has(a.id)) || [];

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">Dynamic Resume Studio</h2>
          <p className="view-subtitle">
            Tailor high-impact, ATS-optimized resumes by selecting verified portfolio records. Download as clean ReportLab PDF.
          </p>
        </div>
        <div className="btn-group-sm">
          <button className="btn btn-outline" onClick={() => setShowSavedModal(!showSavedModal)}>
            <History size={16} />
            <span>Saved Versions ({savedResumes.length})</span>
          </button>
          <button className="btn btn-secondary" onClick={handleSaveResume} disabled={isSaving}>
            <Save size={16} />
            <span>{isSaving ? 'Saving...' : 'Save Version'}</span>
          </button>
          <button className="btn btn-primary" onClick={handleDownloadPdf} disabled={isDownloading}>
            <Download size={16} className={isDownloading ? 'spin' : ''} />
            <span>{isDownloading ? 'Generating PDF...' : 'Download ATS PDF'}</span>
          </button>
        </div>
      </div>

      {/* Target Preset Selector */}
      <div className="sample-jobs-bar">
        <span className="bar-label">Tailor For Target Role:</span>
        <div className="sample-job-buttons">
          {jobs.map((job) => (
            <button
              key={job.id}
              className={`sample-job-btn ${selectedJob?.id === job.id ? 'active' : ''}`}
              onClick={() => handleSwitchJobPreset(job)}
            >
              {job.title.includes('Backend') ? <Cpu size={14} /> : <Network size={14} />}
              <span>{job.title}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="resume-layout-grid">
        {/* Left: Customization Controls & Item Selection */}
        <div className="resume-controls-pane">
          {/* Metadata & Title */}
          <div className="control-section-card">
            <h4 className="control-card-title">Resume Metadata</h4>
            <div className="form-group">
              <label>Target Role Title on Resume</label>
              <input
                type="text"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Resume Version Name</label>
              <input
                type="text"
                value={resumeTitle}
                onChange={(e) => setResumeTitle(e.target.value)}
              />
            </div>
          </div>

          {/* Professional Summary */}
          <div className="control-section-card">
            <div className="card-top-bar">
              <h4 className="control-card-title">Professional Summary</h4>
              <button
                className="btn btn-sm btn-outline ai-pill-btn"
                onClick={handleGenerateSummary}
                disabled={isGeneratingSummary}
                title="Generates concise summary using verified portfolio data"
              >
                <Sparkles size={13} className={isGeneratingSummary ? 'spin' : ''} />
                <span>AI Tailor</span>
              </button>
            </div>
            <textarea
              rows={4}
              value={customSummary}
              onChange={(e) => setCustomSummary(e.target.value)}
              placeholder="Write or generate a tailored summary..."
            />
          </div>

          {/* Skills Selection */}
          <div className="control-section-card">
            <div className="card-top-bar">
              <h4 className="control-card-title">
                Technical Skills ({selectedSkills.size} / {portfolio?.skills?.length || 0})
              </h4>
              <button
                className="link-btn"
                onClick={() => toggleAll(setSelectedSkills, portfolio?.skills?.map(s => s.id) || [], selectedSkills)}
              >
                {selectedSkills.size === (portfolio?.skills?.length || 0) ? 'Deselect All' : 'Select All'}
              </button>
            </div>
            <div className="checkboxes-scroll-box">
              {portfolio?.skills?.map((sk) => {
                const isChecked = selectedSkills.has(sk.id);
                return (
                  <label key={sk.id} className={`checkbox-item ${isChecked ? 'checked' : ''}`}>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggleItem(setSelectedSkills, selectedSkills, sk.id)}
                    />
                    <span className="item-label-text">
                      <strong>{sk.name}</strong>
                      <small>({sk.category})</small>
                    </span>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Projects Selection */}
          <div className="control-section-card">
            <div className="card-top-bar">
              <h4 className="control-card-title">
                Projects ({selectedProjects.size} / {portfolio?.projects?.length || 0})
              </h4>
              <button
                className="link-btn"
                onClick={() => toggleAll(setSelectedProjects, portfolio?.projects?.map(p => p.id) || [], selectedProjects)}
              >
                {selectedProjects.size === (portfolio?.projects?.length || 0) ? 'Deselect All' : 'Select All'}
              </button>
            </div>
            <div className="checkboxes-scroll-box">
              {portfolio?.projects?.map((proj) => {
                const isChecked = selectedProjects.has(proj.id);
                return (
                  <label key={proj.id} className={`checkbox-item ${isChecked ? 'checked' : ''}`}>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggleItem(setSelectedProjects, selectedProjects, proj.id)}
                    />
                    <span className="item-label-text">
                      <strong>{proj.title}</strong>
                      <small>{proj.role}</small>
                    </span>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Experience Selection */}
          <div className="control-section-card">
            <div className="card-top-bar">
              <h4 className="control-card-title">
                Work Experience ({selectedExperiences.size} / {portfolio?.experiences?.length || 0})
              </h4>
              <button
                className="link-btn"
                onClick={() => toggleAll(setSelectedExperiences, portfolio?.experiences?.map(e => e.id) || [], selectedExperiences)}
              >
                {selectedExperiences.size === (portfolio?.experiences?.length || 0) ? 'Deselect All' : 'Select All'}
              </button>
            </div>
            <div className="checkboxes-scroll-box">
              {portfolio?.experiences?.map((exp) => {
                const isChecked = selectedExperiences.has(exp.id);
                return (
                  <label key={exp.id} className={`checkbox-item ${isChecked ? 'checked' : ''}`}>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggleItem(setSelectedExperiences, selectedExperiences, exp.id)}
                    />
                    <span className="item-label-text">
                      <strong>{exp.role}</strong>
                      <small>{exp.company}</small>
                    </span>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Certifications Selection */}
          <div className="control-section-card">
            <div className="card-top-bar">
              <h4 className="control-card-title">
                Certifications ({selectedCerts.size} / {portfolio?.certifications?.length || 0})
              </h4>
              <button
                className="link-btn"
                onClick={() => toggleAll(setSelectedCerts, portfolio?.certifications?.map(c => c.id) || [], selectedCerts)}
              >
                {selectedCerts.size === (portfolio?.certifications?.length || 0) ? 'Deselect All' : 'Select All'}
              </button>
            </div>
            <div className="checkboxes-scroll-box">
              {portfolio?.certifications?.map((c) => {
                const isChecked = selectedCerts.has(c.id);
                return (
                  <label key={c.id} className={`checkbox-item ${isChecked ? 'checked' : ''}`}>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggleItem(setSelectedCerts, selectedCerts, c.id)}
                    />
                    <span className="item-label-text">
                      <strong>{c.name}</strong>
                      <small>{c.issuing_organization}</small>
                    </span>
                  </label>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right: ATS Live Resume Preview */}
        <div className="resume-preview-pane">
          <div className="preview-top-toolbar">
            <div className="preview-indicator">
              <Eye size={15} />
              <span>ATS Paper Preview (Letter / 1-Page Layout)</span>
            </div>
            <button
              className="btn btn-sm btn-primary"
              onClick={handleDownloadPdf}
              disabled={isDownloading}
            >
              <Download size={14} />
              <span>Download PDF</span>
            </button>
          </div>

          {/* Physical Document Simulator */}
          <div className="ats-document-sheet">
            {/* Header */}
            <div className="doc-header">
              <h1 className="doc-name">{portfolio?.profile?.full_name || 'Candidate Name'}</h1>
              <div className="doc-headline">{targetRole || portfolio?.profile?.headline}</div>
              <div className="doc-contact-bar">
                {portfolio?.profile?.email && <span>{portfolio.profile.email}</span>}
                {portfolio?.profile?.phone && <span>• {portfolio.profile.phone}</span>}
                {portfolio?.profile?.location && <span>• {portfolio.profile.location}</span>}
                {portfolio?.profile?.linkedin_url && (
                  <span>• {portfolio.profile.linkedin_url.replace('https://', '')}</span>
                )}
                {portfolio?.profile?.github_url && (
                  <span>• {portfolio.profile.github_url.replace('https://', '')}</span>
                )}
              </div>
            </div>

            {/* Summary */}
            {customSummary && (
              <div className="doc-section">
                <h3 className="doc-section-title">Professional Summary</h3>
                <div className="doc-divider" />
                <p className="doc-body-text">{customSummary}</p>
              </div>
            )}

            {/* Technical Skills */}
            {previewSkills.length > 0 && (
              <div className="doc-section">
                <h3 className="doc-section-title">Technical Skills</h3>
                <div className="doc-divider" />
                <div className="doc-skills-list">
                  {/* Group skills by category */}
                  {Object.entries(
                    previewSkills.reduce((acc, s) => {
                      acc[s.category] = acc[s.category] || [];
                      acc[s.category].push(s.name);
                      return acc;
                    }, {})
                  ).map(([cat, names]) => (
                    <div key={cat} className="doc-skill-line">
                      <strong>{cat}:</strong> <span>{names.join(', ')}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Work Experience */}
            {previewExperiences.length > 0 && (
              <div className="doc-section">
                <h3 className="doc-section-title">Work Experience</h3>
                <div className="doc-divider" />
                {previewExperiences.map((exp) => (
                  <div key={exp.id} className="doc-item-entry">
                    <div className="doc-entry-row">
                      <span className="doc-entry-role">
                        <strong>{exp.role}</strong> | {exp.company}
                      </span>
                      <span className="doc-entry-date">
                        {exp.start_date} – {exp.is_current ? 'Present' : exp.end_date}
                      </span>
                    </div>
                    {exp.location && <div className="doc-entry-loc">{exp.location}</div>}
                    {exp.description && !exp.highlights_list?.length && (
                      <p className="doc-body-text">{exp.description}</p>
                    )}
                    {exp.highlights_list && exp.highlights_list.length > 0 && (
                      <ul className="doc-bullet-list">
                        {exp.highlights_list.map((h, i) => (
                          <li key={i}>{h}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Technical Projects */}
            {previewProjects.length > 0 && (
              <div className="doc-section">
                <h3 className="doc-section-title">Technical Projects</h3>
                <div className="doc-divider" />
                {previewProjects.map((p) => (
                  <div key={p.id} className="doc-item-entry">
                    <div className="doc-entry-row">
                      <span className="doc-entry-role">
                        <strong>{p.title}</strong>
                        {p.tech_stack_list?.length > 0 && (
                          <small className="doc-tech-inline"> ({p.tech_stack_list.join(', ')})</small>
                        )}
                      </span>
                      <span className="doc-entry-date">
                        {p.start_date} – {p.end_date || 'Present'}
                      </span>
                    </div>
                    {p.description && <p className="doc-body-text">{p.description}</p>}
                    {p.highlights_list && p.highlights_list.length > 0 && (
                      <ul className="doc-bullet-list">
                        {p.highlights_list.map((h, i) => (
                          <li key={i}>{h}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Education */}
            {previewEducation.length > 0 && (
              <div className="doc-section">
                <h3 className="doc-section-title">Education</h3>
                <div className="doc-divider" />
                {previewEducation.map((edu) => (
                  <div key={edu.id} className="doc-item-entry">
                    <div className="doc-entry-row">
                      <strong>{edu.institution}</strong>
                      <span className="doc-entry-date">{edu.start_date} – {edu.end_date}</span>
                    </div>
                    <div className="doc-sub-text">
                      {edu.degree} in {edu.field_of_study} {edu.gpa && `(GPA: ${edu.gpa})`}
                    </div>
                    {edu.description && <p className="doc-body-text">{edu.description}</p>}
                  </div>
                ))}
              </div>
            )}

            {/* Certifications */}
            {previewCerts.length > 0 && (
              <div className="doc-section">
                <h3 className="doc-section-title">Certifications</h3>
                <div className="doc-divider" />
                {previewCerts.map((c) => (
                  <div key={c.id} className="doc-cert-line">
                    <div className="doc-entry-row">
                      <span><strong>{c.name}</strong> – {c.issuing_organization}</span>
                      <span className="doc-entry-date">{c.issue_date}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Achievements */}
            {previewAchievements.length > 0 && (
              <div className="doc-section">
                <h3 className="doc-section-title">Achievements & Publications</h3>
                <div className="doc-divider" />
                {previewAchievements.map((a) => (
                  <div key={a.id} className="doc-cert-line">
                    <div className="doc-entry-row">
                      <span><strong>{a.title}</strong> {a.issuer_or_publisher && `| ${a.issuer_or_publisher}`}</span>
                      <span className="doc-entry-date">{a.date}</span>
                    </div>
                    {a.description && <p className="doc-body-text">{a.description}</p>}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
