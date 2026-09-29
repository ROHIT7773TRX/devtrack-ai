import React, { useState, useEffect } from 'react';
import './App.css';
import Navbar from './components/Navbar';
import DashboardView from './components/DashboardView';
import ApplicationList from './components/ApplicationList';
import ApplicationFormModal from './components/ApplicationFormModal';
import {
  getDashboardStats,
  getApplications,
  createApplication,
  updateApplication,
  deleteApplication
} from './services/api';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingApp, setEditingApp] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const statsData = await getDashboardStats();
      setStats(statsData);

      const appsData = await getApplications(statusFilter);
      setApplications(appsData);
    } catch (err) {
      console.error('Error fetching data from backend:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [statusFilter]);

  const handleOpenNewModal = () => {
    setEditingApp(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (app) => {
    setEditingApp(app);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingApp(null);
  };

  const handleSubmitForm = async (formData) => {
    try {
      if (editingApp) {
        await updateApplication(editingApp.id, formData);
      } else {
        await createApplication(formData);
      }
      handleCloseModal();
      await fetchData();
    } catch (err) {
      console.error('Failed to submit application form:', err);
      alert('Error saving application. Check console or backend service.');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this job application?')) {
      try {
        await deleteApplication(id);
        await fetchData();
      } catch (err) {
        console.error('Failed to delete application:', err);
        alert('Error deleting application.');
      }
    }
  };

  return (
    <div className="app-container">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="main-content">
        {activeTab === 'dashboard' ? (
          <DashboardView
            stats={stats}
            loading={loading}
            onNewApplication={handleOpenNewModal}
          />
        ) : (
          <ApplicationList
            applications={applications}
            loading={loading}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            onNewApplication={handleOpenNewModal}
            onEditApplication={handleOpenEditModal}
            onDeleteApplication={handleDelete}
          />
        )}
      </main>

      <ApplicationFormModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSubmit={handleSubmitForm}
        initialData={editingApp}
      />

      <footer className="footer">
        <p>DevTrack AI — Cloud Native Academic DevOps Project | LPU</p>
      </footer>
    </div>
  );
}

export default App;
