import React from 'react';
import {
  LayoutDashboard,
  Database,
  Sparkles,
  Target,
  FileText,
  Table,
  Settings,
  ShieldCheck
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'portfolio', label: 'Portfolio Database', icon: Database },
    { id: 'organizer', label: 'AI Organizer', icon: Sparkles, badge: 'AI' },
    { id: 'analyzer', label: 'Job Analyzer', icon: Target },
    { id: 'resume', label: 'Resume Studio', icon: FileText },
    { id: 'sheets', label: 'Google Sheets', icon: Table },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="app-sidebar">
      <div className="sidebar-brand">
        <div className="brand-logo">
          <Sparkles size={22} className="brand-icon" />
        </div>
        <div className="brand-text">
          <span className="brand-title">CareerMatrix</span>
          <span className="brand-subtitle">AI Portfolio & Resume</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={19} className="nav-icon" />
              <span className="nav-label">{item.label}</span>
              {item.badge && <span className="nav-badge">{item.badge}</span>}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="verified-badge-card">
          <ShieldCheck size={18} className="verified-icon" />
          <div className="verified-text">
            <strong>ATS Truth Engine</strong>
            <p>100% verified portfolio records. Zero hallucination guarantee.</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
