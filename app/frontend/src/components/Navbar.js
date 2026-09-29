import React from 'react';

const Navbar = ({ activeTab, setActiveTab }) => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        🚀 DevTrack AI
        <span className="navbar-badge">v1.0 Cloud Native</span>
      </div>
      <div className="nav-links">
        <button
          className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button
          className={`nav-btn ${activeTab === 'applications' ? 'active' : ''}`}
          onClick={() => setActiveTab('applications')}
        >
          Job Applications
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
