import React, { useState } from 'react';
import {
  User,
  GraduationCap,
  Code2,
  Award,
  Layers,
  Briefcase,
  Trophy,
  Plus,
  Pencil,
  Trash2,
  ExternalLink,
  Search,
  Check
} from 'lucide-react';
import Modal from '../components/Modal';

export default function PortfolioView({ portfolio, onRefresh, showToast }) {
  const [activeSection, setActiveSection] = useState('profile');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState('add'); // 'add' or 'edit'
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({});

  const sections = [
    { id: 'profile', label: 'Profile', icon: User, count: 1 },
    { id: 'skills', label: 'Skills', icon: Code2, count: portfolio?.skills?.length || 0 },
    { id: 'projects', label: 'Projects', icon: Layers, count: portfolio?.projects?.length || 0 },
    { id: 'experiences', label: 'Experience', icon: Briefcase, count: portfolio?.experiences?.length || 0 },
    { id: 'education', label: 'Education', icon: GraduationCap, count: portfolio?.education?.length || 0 },
    { id: 'certifications', label: 'Certifications', icon: Award, count: portfolio?.certifications?.length || 0 },
    { id: 'achievements', label: 'Achievements', icon: Trophy, count: portfolio?.achievements?.length || 0 },
  ];

  // Open modal for add
  const handleOpenAdd = () => {
    setModalMode('add');
    setEditingItem(null);
    if (activeSection === 'skills') {
      setFormData({ name: '', category: 'Languages', proficiency: 'Intermediate', years_of_experience: 1.0 });
    } else if (activeSection === 'projects') {
      setFormData({ title: '', description: '', tech_stack: '', role: 'Developer', highlights: '', live_url: '', repo_url: '', start_date: '', end_date: '' });
    } else if (activeSection === 'experiences') {
      setFormData({ company: '', role: '', location: '', start_date: '', end_date: '', is_current: false, description: '', highlights: '' });
    } else if (activeSection === 'education') {
      setFormData({ institution: '', degree: '', field_of_study: '', start_date: '', end_date: '', gpa: '', description: '', order_index: 0 });
    } else if (activeSection === 'certifications') {
      setFormData({ name: '', issuing_organization: '', issue_date: '', expiration_date: '', credential_id: '', credential_url: '' });
    } else if (activeSection === 'achievements') {
      setFormData({ title: '', type: 'Achievement', issuer_or_publisher: '', date: '', description: '', url: '' });
    }
    setIsModalOpen(true);
  };

  // Open modal for edit
  const handleOpenEdit = (item) => {
    setModalMode('edit');
    setEditingItem(item);
    if (activeSection === 'profile') {
      setFormData({ ...(portfolio?.profile || {}) });
    } else {
      const copy = { ...item };
      if (Array.isArray(copy.tech_stack_list)) {
        copy.tech_stack = copy.tech_stack_list.join(', ');
      }
      if (Array.isArray(copy.highlights_list)) {
        copy.highlights = copy.highlights_list.join('\n');
      }
      setFormData(copy);
    }
    setIsModalOpen(true);
  };

  // Save (Create or Update)
  const handleSubmitForm = async (e) => {
    e.preventDefault();
    try {
      if (activeSection === 'profile') {
        const res = await fetch('/api/portfolio/profile', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });
        const d = await res.json();
        if (d.success) {
          showToast('Profile updated successfully!', 'success');
          setIsModalOpen(false);
          onRefresh();
        } else {
          showToast(d.error || 'Failed to update profile', 'error');
        }
        return;
      }

      // Format arrays for projects / experiences
      const payload = { ...formData };
      if (activeSection === 'projects') {
        if (typeof payload.tech_stack === 'string') {
          payload.tech_stack = payload.tech_stack.split(',').map(s => s.strip ? s.strip() : s.trim()).filter(Boolean);
        }
        if (typeof payload.highlights === 'string') {
          payload.highlights = payload.highlights.split('\n').map(s => s.trim()).filter(Boolean);
        }
      } else if (activeSection === 'experiences') {
        if (typeof payload.highlights === 'string') {
          payload.highlights = payload.highlights.split('\n').map(s => s.trim()).filter(Boolean);
        }
      }

      let url = `/api/portfolio/${activeSection}`;
      let method = 'POST';
      if (modalMode === 'edit' && editingItem) {
        url = `/api/portfolio/${activeSection}/${editingItem.id}`;
        method = 'PUT';
      }

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        showToast(data.message || 'Saved successfully!', 'success');
        setIsModalOpen(false);
        onRefresh();
      } else {
        showToast(data.error || 'Failed to save', 'error');
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  // Delete item
  const handleDeleteItem = async (id) => {
    if (!window.confirm('Are you sure you want to delete this record?')) return;
    try {
      const res = await fetch(`/api/portfolio/${activeSection}/${id}`, {
        method: 'DELETE'
      });
      const data = await res.json();
      if (data.success) {
        showToast('Record deleted.', 'success');
        onRefresh();
      } else {
        showToast(data.error || 'Failed to delete record', 'error');
      }
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h2 className="view-title">Portfolio Database Management</h2>
          <p className="view-subtitle">
            Master repository of all verified records stored safely in SQLite.
          </p>
        </div>
        {activeSection !== 'profile' && (
          <button className="btn btn-primary" onClick={handleOpenAdd}>
            <Plus size={16} />
            <span>Add {activeSection.slice(0, -1)}</span>
          </button>
        )}
      </div>

      {/* Tabs Bar */}
      <div className="portfolio-tabs">
        {sections.map((sec) => {
          const Icon = sec.icon;
          const isActive = activeSection === sec.id;
          return (
            <button
              key={sec.id}
              className={`portfolio-tab-btn ${isActive ? 'active' : ''}`}
              onClick={() => {
                setActiveSection(sec.id);
                setSearchTerm('');
              }}
            >
              <Icon size={16} />
              <span>{sec.label}</span>
              <span className="tab-badge">{sec.count}</span>
            </button>
          );
        })}
      </div>

      {/* Content Area */}
      <div className="portfolio-content-card">
        {/* Profile Section */}
        {activeSection === 'profile' && (
          <div className="profile-detail-pane">
            <div className="profile-header-row">
              <div>
                <h3 className="profile-name">{portfolio?.profile?.full_name || 'Candidate Name'}</h3>
                <span className="profile-headline">{portfolio?.profile?.headline}</span>
              </div>
              <button
                className="btn btn-secondary"
                onClick={() => handleOpenEdit(portfolio?.profile)}
              >
                <Pencil size={15} />
                <span>Edit Profile</span>
              </button>
            </div>

            <div className="profile-info-grid">
              <div className="info-item">
                <span className="info-label">Email</span>
                <span className="info-val">{portfolio?.profile?.email || '—'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Phone</span>
                <span className="info-val">{portfolio?.profile?.phone || '—'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Location</span>
                <span className="info-val">{portfolio?.profile?.location || '—'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">GitHub</span>
                <span className="info-val">{portfolio?.profile?.github_url || '—'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">LinkedIn</span>
                <span className="info-val">{portfolio?.profile?.linkedin_url || '—'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Portfolio URL</span>
                <span className="info-val">{portfolio?.profile?.portfolio_url || '—'}</span>
              </div>
            </div>

            <div className="profile-summary-box">
              <h4 className="box-title">Professional Summary</h4>
              <p>{portfolio?.profile?.summary || 'No summary set yet.'}</p>
            </div>
          </div>
        )}

        {/* Skills Section */}
        {activeSection === 'skills' && (
          <div className="items-list-pane">
            <div className="search-bar-row">
              <div className="search-input-wrap">
                <Search size={16} className="search-icon" />
                <input
                  type="text"
                  placeholder="Search skills..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-input"
                />
              </div>
            </div>

            <div className="skills-grid-view">
              {portfolio?.skills
                ?.filter(s => s.name.toLowerCase().includes(searchTerm.toLowerCase()) || s.category.toLowerCase().includes(searchTerm.toLowerCase()))
                ?.map((sk) => (
                  <div key={sk.id} className="skill-item-card">
                    <div className="skill-item-left">
                      <span className="skill-name">{sk.name}</span>
                      <span className="skill-cat-tag">{sk.category}</span>
                    </div>
                    <div className="skill-item-right">
                      <span className={`proficiency-badge ${sk.proficiency?.toLowerCase()}`}>{sk.proficiency}</span>
                      <div className="item-actions">
                        <button onClick={() => handleOpenEdit(sk)} className="icon-action-btn" title="Edit">
                          <Pencil size={14} />
                        </button>
                        <button onClick={() => handleDeleteItem(sk.id)} className="icon-action-btn delete" title="Delete">
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Projects Section */}
        {activeSection === 'projects' && (
          <div className="items-list-pane">
            <div className="projects-list-view">
              {portfolio?.projects?.map((proj) => (
                <div key={proj.id} className="record-item-card">
                  <div className="record-item-top">
                    <div>
                      <h4 className="record-title">{proj.title}</h4>
                      <span className="record-sub">{proj.role} {proj.start_date && `• ${proj.start_date} to ${proj.end_date || 'Present'}`}</span>
                    </div>
                    <div className="item-actions">
                      <button onClick={() => handleOpenEdit(proj)} className="icon-action-btn" title="Edit">
                        <Pencil size={15} />
                      </button>
                      <button onClick={() => handleDeleteItem(proj.id)} className="icon-action-btn delete" title="Delete">
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>

                  <p className="record-desc">{proj.description}</p>

                  {proj.tech_stack_list && proj.tech_stack_list.length > 0 && (
                    <div className="tags-row">
                      {proj.tech_stack_list.map((tech, i) => (
                        <span key={i} className="tech-badge">{tech}</span>
                      ))}
                    </div>
                  )}

                  {proj.highlights_list && proj.highlights_list.length > 0 && (
                    <ul className="record-bullets">
                      {proj.highlights_list.map((h, i) => (
                        <li key={i}>{h}</li>
                      ))}
                    </ul>
                  )}

                  {(proj.live_url || proj.repo_url) && (
                    <div className="record-links-row">
                      {proj.repo_url && (
                        <a href={proj.repo_url} target="_blank" rel="noopener noreferrer" className="link-chip">
                          <ExternalLink size={13} />
                          <span>Code Repository</span>
                        </a>
                      )}
                      {proj.live_url && (
                        <a href={proj.live_url} target="_blank" rel="noopener noreferrer" className="link-chip">
                          <ExternalLink size={13} />
                          <span>Live Demo</span>
                        </a>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Experience Section */}
        {activeSection === 'experiences' && (
          <div className="items-list-pane">
            <div className="experience-list-view">
              {portfolio?.experiences?.map((exp) => (
                <div key={exp.id} className="record-item-card">
                  <div className="record-item-top">
                    <div>
                      <h4 className="record-title">{exp.role}</h4>
                      <span className="record-sub">{exp.company} • {exp.location || 'Remote'} ({exp.start_date} – {exp.is_current ? 'Present' : exp.end_date})</span>
                    </div>
                    <div className="item-actions">
                      <button onClick={() => handleOpenEdit(exp)} className="icon-action-btn" title="Edit">
                        <Pencil size={15} />
                      </button>
                      <button onClick={() => handleDeleteItem(exp.id)} className="icon-action-btn delete" title="Delete">
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>

                  {exp.description && <p className="record-desc">{exp.description}</p>}

                  {exp.highlights_list && exp.highlights_list.length > 0 && (
                    <ul className="record-bullets">
                      {exp.highlights_list.map((h, i) => (
                        <li key={i}>{h}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Education Section */}
        {activeSection === 'education' && (
          <div className="items-list-pane">
            <div className="education-list-view">
              {portfolio?.education?.map((edu) => (
                <div key={edu.id} className="record-item-card">
                  <div className="record-item-top">
                    <div>
                      <h4 className="record-title">{edu.degree} in {edu.field_of_study}</h4>
                      <span className="record-sub">{edu.institution} ({edu.start_date} – {edu.end_date})</span>
                    </div>
                    <div className="item-actions">
                      <button onClick={() => handleOpenEdit(edu)} className="icon-action-btn" title="Edit">
                        <Pencil size={15} />
                      </button>
                      <button onClick={() => handleDeleteItem(edu.id)} className="icon-action-btn delete" title="Delete">
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>
                  {edu.gpa && <div className="gpa-pill">GPA: {edu.gpa}</div>}
                  {edu.description && <p className="record-desc">{edu.description}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Certifications Section */}
        {activeSection === 'certifications' && (
          <div className="items-list-pane">
            <div className="certs-list-view">
              {portfolio?.certifications?.map((c) => (
                <div key={c.id} className="record-item-card">
                  <div className="record-item-top">
                    <div>
                      <h4 className="record-title">{c.name}</h4>
                      <span className="record-sub">{c.issuing_organization} • Issued {c.issue_date}</span>
                    </div>
                    <div className="item-actions">
                      <button onClick={() => handleOpenEdit(c)} className="icon-action-btn" title="Edit">
                        <Pencil size={15} />
                      </button>
                      <button onClick={() => handleDeleteItem(c.id)} className="icon-action-btn delete" title="Delete">
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>
                  {c.credential_id && <p className="credential-id">Credential ID: <code>{c.credential_id}</code></p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Achievements Section */}
        {activeSection === 'achievements' && (
          <div className="items-list-pane">
            <div className="achievements-list-view">
              {portfolio?.achievements?.map((ach) => (
                <div key={ach.id} className="record-item-card">
                  <div className="record-item-top">
                    <div>
                      <h4 className="record-title">{ach.title}</h4>
                      <span className="record-sub">{ach.type} • {ach.issuer_or_publisher} ({ach.date})</span>
                    </div>
                    <div className="item-actions">
                      <button onClick={() => handleOpenEdit(ach)} className="icon-action-btn" title="Edit">
                        <Pencil size={15} />
                      </button>
                      <button onClick={() => handleDeleteItem(ach.id)} className="icon-action-btn delete" title="Delete">
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>
                  {ach.description && <p className="record-desc">{ach.description}</p>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* CRUD Modal adhering to native <dialog> */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={`${modalMode === 'add' ? 'Add' : 'Edit'} ${activeSection.slice(0, -1)}`}
      >
        <form onSubmit={handleSubmitForm} className="modal-form">
          {activeSection === 'profile' && (
            <>
              <div className="form-group">
                <label>Full Name *</label>
                <input
                  type="text"
                  required
                  value={formData.full_name || ''}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Headline / Target Role</label>
                <input
                  type="text"
                  value={formData.headline || ''}
                  onChange={(e) => setFormData({ ...formData, headline: e.target.value })}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Email *</label>
                  <input
                    type="email"
                    required
                    value={formData.email || ''}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Phone</label>
                  <input
                    type="text"
                    value={formData.phone || ''}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Location</label>
                <input
                  type="text"
                  value={formData.location || ''}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>GitHub URL</label>
                  <input
                    type="url"
                    value={formData.github_url || ''}
                    onChange={(e) => setFormData({ ...formData, github_url: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>LinkedIn URL</label>
                  <input
                    type="url"
                    value={formData.linkedin_url || ''}
                    onChange={(e) => setFormData({ ...formData, linkedin_url: e.target.value })}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Professional Summary</label>
                <textarea
                  rows={4}
                  value={formData.summary || ''}
                  onChange={(e) => setFormData({ ...formData, summary: e.target.value })}
                />
              </div>
            </>
          )}

          {activeSection === 'skills' && (
            <>
              <div className="form-group">
                <label>Skill Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Python, Docker, TCP/IP"
                  value={formData.name || ''}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Category *</label>
                <select
                  value={formData.category || 'Languages'}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                >
                  <option value="Languages">Languages</option>
                  <option value="Backend & APIs">Backend & APIs</option>
                  <option value="Databases">Databases</option>
                  <option value="Networking & Protocols">Networking & Protocols</option>
                  <option value="DevOps & Tools">DevOps & Tools</option>
                  <option value="Soft Skills">Soft Skills</option>
                </select>
              </div>
              <div className="form-group">
                <label>Proficiency</label>
                <select
                  value={formData.proficiency || 'Intermediate'}
                  onChange={(e) => setFormData({ ...formData, proficiency: e.target.value })}
                >
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                  <option value="Expert">Expert</option>
                </select>
              </div>
            </>
          )}

          {activeSection === 'projects' && (
            <>
              <div className="form-group">
                <label>Project Title *</label>
                <input
                  type="text"
                  required
                  value={formData.title || ''}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Role</label>
                <input
                  type="text"
                  value={formData.role || ''}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Tech Stack (Comma-separated)</label>
                <input
                  type="text"
                  placeholder="Python, Flask, Docker, PostgreSQL"
                  value={formData.tech_stack || ''}
                  onChange={(e) => setFormData({ ...formData, tech_stack: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Description *</label>
                <textarea
                  rows={2}
                  required
                  value={formData.description || ''}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Key Highlights / Bullet Points (One per line)</label>
                <textarea
                  rows={4}
                  placeholder="Architected RESTful endpoints handling 1,500+ req/sec&#10;Integrated Redis asynchronous job queues"
                  value={formData.highlights || ''}
                  onChange={(e) => setFormData({ ...formData, highlights: e.target.value })}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Repository URL</label>
                  <input
                    type="url"
                    value={formData.repo_url || ''}
                    onChange={(e) => setFormData({ ...formData, repo_url: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Live URL</label>
                  <input
                    type="url"
                    value={formData.live_url || ''}
                    onChange={(e) => setFormData({ ...formData, live_url: e.target.value })}
                  />
                </div>
              </div>
            </>
          )}

          {activeSection === 'experiences' && (
            <>
              <div className="form-row">
                <div className="form-group">
                  <label>Company *</label>
                  <input
                    type="text"
                    required
                    value={formData.company || ''}
                    onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Role *</label>
                  <input
                    type="text"
                    required
                    value={formData.role || ''}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Start Date</label>
                  <input
                    type="text"
                    placeholder="YYYY-MM"
                    value={formData.start_date || ''}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>End Date</label>
                  <input
                    type="text"
                    placeholder="YYYY-MM or Present"
                    value={formData.end_date || ''}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Bullet Points / Responsibilities (One per line)</label>
                <textarea
                  rows={4}
                  value={formData.highlights || ''}
                  onChange={(e) => setFormData({ ...formData, highlights: e.target.value })}
                />
              </div>
            </>
          )}

          {activeSection === 'education' && (
            <>
              <div className="form-group">
                <label>Institution *</label>
                <input
                  type="text"
                  required
                  value={formData.institution || ''}
                  onChange={(e) => setFormData({ ...formData, institution: e.target.value })}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Degree *</label>
                  <input
                    type="text"
                    required
                    value={formData.degree || ''}
                    onChange={(e) => setFormData({ ...formData, degree: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Field of Study</label>
                  <input
                    type="text"
                    value={formData.field_of_study || ''}
                    onChange={(e) => setFormData({ ...formData, field_of_study: e.target.value })}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>GPA</label>
                <input
                  type="text"
                  placeholder="3.8 / 4.0"
                  value={formData.gpa || ''}
                  onChange={(e) => setFormData({ ...formData, gpa: e.target.value })}
                />
              </div>
            </>
          )}

          {activeSection === 'certifications' && (
            <>
              <div className="form-group">
                <label>Certification Name *</label>
                <input
                  type="text"
                  required
                  value={formData.name || ''}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Issuing Organization *</label>
                <input
                  type="text"
                  required
                  value={formData.issuing_organization || ''}
                  onChange={(e) => setFormData({ ...formData, issuing_organization: e.target.value })}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Issue Date</label>
                  <input
                    type="text"
                    placeholder="YYYY-MM"
                    value={formData.issue_date || ''}
                    onChange={(e) => setFormData({ ...formData, issue_date: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Credential ID</label>
                  <input
                    type="text"
                    value={formData.credential_id || ''}
                    onChange={(e) => setFormData({ ...formData, credential_id: e.target.value })}
                  />
                </div>
              </div>
            </>
          )}

          {activeSection === 'achievements' && (
            <>
              <div className="form-group">
                <label>Title *</label>
                <input
                  type="text"
                  required
                  value={formData.title || ''}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Type</label>
                <select
                  value={formData.type || 'Achievement'}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                >
                  <option value="Achievement">Achievement</option>
                  <option value="Publication">Publication</option>
                  <option value="Award">Award</option>
                  <option value="Honor">Honor</option>
                </select>
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  rows={3}
                  value={formData.description || ''}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
            </>
          )}

          <div className="modal-actions">
            <button type="button" className="btn btn-outline" onClick={() => setIsModalOpen(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              <Check size={16} />
              <span>Save Record</span>
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
