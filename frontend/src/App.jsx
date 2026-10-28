import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Toast from './components/Toast';
import DashboardView from './views/DashboardView';
import PortfolioView from './views/PortfolioView';
import AIOrganizerView from './views/AIOrganizerView';
import JobAnalyzerView from './views/JobAnalyzerView';
import ResumeStudioView from './views/ResumeStudioView';
import GoogleSheetsView from './views/GoogleSheetsView';
import SettingsView from './views/SettingsView';
import { api } from './api/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [portfolio, setPortfolio] = useState(null);
  const [health, setHealth] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isResetting, setIsResetting] = useState(false);
  
  // Navigation contexts
  const [preselectedJobId, setPreselectedJobId] = useState(null);
  const [resumeContext, setResumeContext] = useState(null);

  // Toast notification state
  const [toast, setToast] = useState({ message: '', type: 'info' });

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
  };

  const loadData = async () => {
    try {
      const [portRes, healthRes] = await Promise.all([
        api.getPortfolio(),
        api.getHealth()
      ]);
      if (portRes.success) {
        setPortfolio(portRes.data);
      }
      setHealth(healthRes);
    } catch (err) {
      console.error('Error fetching data:', err);
      showToast('Could not connect to backend server. Make sure Flask is running.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleResetSample = async () => {
    if (!window.confirm('Reset portfolio to the sample candidate (Alex Morgan)? Any unsaved additions will be overwritten.')) {
      return;
    }
    setIsResetting(true);
    try {
      const res = await api.resetToSample();
      if (res.success) {
        setPortfolio(res.data);
        showToast('Reset to sample candidate data successfully!', 'success');
      } else {
        showToast(res.error || 'Failed to reset', 'error');
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setIsResetting(false);
    }
  };

  const handleSelectSampleJob = (jobId) => {
    setPreselectedJobId(jobId);
    setActiveTab('analyzer');
  };

  const handleNavigateToResume = (context) => {
    setResumeContext(context);
    setActiveTab('resume');
  };

  return (
    <div className="app-layout">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="app-main-area">
        <Navbar
          health={health}
          onResetSample={handleResetSample}
          isResetting={isResetting}
        />

        <main className="app-content-body">
          {isLoading ? (
            <div className="app-loading-screen">
              <div className="spinner-large" />
              <h3>Loading CareerMatrix Portfolio Engine...</h3>
            </div>
          ) : (
            <>
              {activeTab === 'dashboard' && (
                <DashboardView
                  portfolio={portfolio}
                  onNavigate={setActiveTab}
                  onSelectSampleJob={handleSelectSampleJob}
                />
              )}

              {activeTab === 'portfolio' && (
                <PortfolioView
                  portfolio={portfolio}
                  onRefresh={loadData}
                  showToast={showToast}
                />
              )}

              {activeTab === 'organizer' && (
                <AIOrganizerView
                  onRefresh={loadData}
                  showToast={showToast}
                />
              )}

              {activeTab === 'analyzer' && (
                <JobAnalyzerView
                  preselectedJobId={preselectedJobId}
                  onNavigateToResume={handleNavigateToResume}
                  showToast={showToast}
                />
              )}

              {activeTab === 'resume' && (
                <ResumeStudioView
                  portfolio={portfolio}
                  resumeContext={resumeContext}
                  showToast={showToast}
                />
              )}

              {activeTab === 'sheets' && (
                <GoogleSheetsView
                  showToast={showToast}
                />
              )}

              {activeTab === 'settings' && (
                <SettingsView
                  onResetSample={handleResetSample}
                  isResetting={isResetting}
                  showToast={showToast}
                />
              )}
            </>
          )}
        </main>
      </div>

      {/* Global Toast */}
      {toast.message && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast({ message: '', type: 'info' })}
        />
      )}
    </div>
  );
}
