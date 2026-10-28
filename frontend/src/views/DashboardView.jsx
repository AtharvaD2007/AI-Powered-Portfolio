import React from 'react';
import {
  Briefcase,
  Code2,
  GraduationCap,
  Award,
  Layers,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Network,
  FileCheck
} from 'lucide-react';

export default function DashboardView({ portfolio, onNavigate, onSelectSampleJob }) {
  const profile = portfolio?.profile || {};
  const skillsCount = portfolio?.skills?.length || 0;
  const projectsCount = portfolio?.projects?.length || 0;
  const expCount = portfolio?.experiences?.length || 0;
  const certsCount = portfolio?.certifications?.length || 0;
  const achCount = portfolio?.achievements?.length || 0;

  return (
    <div className="view-container">
      {/* Hero Welcome Card */}
      <div className="dashboard-hero">
        <div className="hero-content">
          <div className="hero-badge">
            <ShieldCheck size={16} />
            <span>Dual-Discipline Engineering Portfolio</span>
          </div>
          <h2 className="hero-title">{profile.full_name || 'Candidate Portfolio'}</h2>
          <p className="hero-headline">{profile.headline}</p>
          <p className="hero-summary">{profile.summary}</p>
          
          <div className="hero-actions">
            <button className="btn btn-primary" onClick={() => onNavigate('analyzer')}>
              <Sparkles size={16} />
              <span>Analyze Job Description</span>
            </button>
            <button className="btn btn-secondary" onClick={() => onNavigate('resume')}>
              <FileCheck size={16} />
              <span>Open Resume Studio</span>
            </button>
            <button className="btn btn-outline" onClick={() => onNavigate('organizer')}>
              <span>AI Organizer</span>
              <ArrowRight size={15} />
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="metrics-grid">
        <div className="metric-card" onClick={() => onNavigate('portfolio')}>
          <div className="metric-icon-box blue">
            <Code2 size={24} />
          </div>
          <div className="metric-info">
            <span className="metric-value">{skillsCount}</span>
            <span className="metric-label">Verified Skills</span>
          </div>
        </div>

        <div className="metric-card" onClick={() => onNavigate('portfolio')}>
          <div className="metric-icon-box purple">
            <Layers size={24} />
          </div>
          <div className="metric-info">
            <span className="metric-value">{projectsCount}</span>
            <span className="metric-label">Technical Projects</span>
          </div>
        </div>

        <div className="metric-card" onClick={() => onNavigate('portfolio')}>
          <div className="metric-icon-box green">
            <Briefcase size={24} />
          </div>
          <div className="metric-info">
            <span className="metric-value">{expCount}</span>
            <span className="metric-label">Work Experiences</span>
          </div>
        </div>

        <div className="metric-card" onClick={() => onNavigate('portfolio')}>
          <div className="metric-icon-box amber">
            <Award size={24} />
          </div>
          <div className="metric-info">
            <span className="metric-value">{certsCount}</span>
            <span className="metric-label">Certifications</span>
          </div>
        </div>
      </div>

      {/* Demonstration Feature Spotlight: Dual Track Resumes */}
      <div className="demo-spotlight-card">
        <div className="spotlight-header">
          <div>
            <span className="spotlight-tag">Demonstration Showcase</span>
            <h3 className="spotlight-title">1 Portfolio → 2 Distinct Target Careers</h3>
          </div>
          <p className="spotlight-desc">
            This candidate has verified projects and experience in both <strong>Backend Software Development</strong> and <strong>Enterprise Networking</strong>.
            Select either target role below to see how our engine automatically adapts the resume without altering the underlying master portfolio.
          </p>
        </div>

        <div className="dual-tracks-grid">
          {/* Track 1: Backend Developer */}
          <div className="track-card">
            <div className="track-header">
              <div className="track-icon-wrapper backend">
                <Cpu size={22} />
              </div>
              <div>
                <h4 className="track-title">Junior Backend Developer</h4>
                <span className="track-company">PayFlow FinTech Systems</span>
              </div>
            </div>
            <p className="track-summary">
              Requires <strong>Python, REST APIs, SQL, PostgreSQL, Docker, Git</strong>. Matches the candidate's Distributed Task Queue project and TechNova internship.
            </p>
            <div className="track-tags">
              <span className="tag">Python</span>
              <span className="tag">REST APIs</span>
              <span className="tag">PostgreSQL</span>
              <span className="tag">Redis</span>
            </div>
            <button
              className="btn btn-outline btn-block"
              onClick={() => {
                onSelectSampleJob(1);
                onNavigate('analyzer');
              }}
            >
              <span>Analyze Backend Job</span>
              <ArrowRight size={15} />
            </button>
          </div>

          {/* Track 2: Network Support Engineer */}
          <div className="track-card">
            <div className="track-header">
              <div className="track-icon-wrapper networking">
                <Network size={22} />
              </div>
              <div>
                <h4 className="track-title">Network Support Engineer</h4>
                <span className="track-company">GlobalNet Infrastructure Solutions</span>
              </div>
            </div>
            <p className="track-summary">
              Requires <strong>TCP/IP, Subnetting, VLANs, OSPF, Routing, Wireshark, CCNA</strong>. Matches the candidate's Campus Network Topology project and Campus IT role.
            </p>
            <div className="track-tags">
              <span className="tag">TCP/IP</span>
              <span className="tag">VLANs</span>
              <span className="tag">Subnetting</span>
              <span className="tag">CCNA</span>
            </div>
            <button
              className="btn btn-outline btn-block"
              onClick={() => {
                onSelectSampleJob(2);
                onNavigate('analyzer');
              }}
            >
              <span>Analyze Networking Job</span>
              <ArrowRight size={15} />
            </button>
          </div>
        </div>
      </div>

      {/* Quick Summary Grid */}
      <div className="dashboard-sections-grid">
        <div className="dash-box">
          <div className="dash-box-header">
            <h4>Verified Skills Overview</h4>
            <button className="link-btn" onClick={() => onNavigate('portfolio')}>View all</button>
          </div>
          <div className="skill-pills-wrap">
            {portfolio?.skills?.slice(0, 16).map((sk) => (
              <span key={sk.id} className="skill-pill">
                <strong>{sk.name}</strong>
                <small>{sk.category}</small>
              </span>
            ))}
          </div>
        </div>

        <div className="dash-box">
          <div className="dash-box-header">
            <h4>Featured Projects</h4>
            <button className="link-btn" onClick={() => onNavigate('portfolio')}>View all</button>
          </div>
          <div className="mini-project-list">
            {portfolio?.projects?.slice(0, 3).map((p) => (
              <div key={p.id} className="mini-project-item">
                <div className="mini-project-top">
                  <strong>{p.title}</strong>
                  <span className="mini-project-role">{p.role}</span>
                </div>
                <p className="mini-project-desc">{p.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
