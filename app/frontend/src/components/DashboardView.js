import React from 'react';

const DashboardView = ({ stats, loading, onNewApplication }) => {
  if (loading) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading metrics & dashboard...</div>;
  }

  if (!stats) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Unable to load dashboard data. Ensure backend is running.</div>;
  }

  return (
    <div>
      <div className="section-header">
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: '700' }}>Career Overview & Analytics</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Real-time statistics of your job search workflow</p>
        </div>
        <button className="btn-primary" onClick={onNewApplication}>
          + Add Application
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-title">Total Applications</div>
          <div className="stat-value">{stats.total_applications}</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">Active Applications</div>
          <div className="stat-value" style={{ color: '#2563eb' }}>{stats.active_applications}</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">Offers Received</div>
          <div className="stat-value" style={{ color: '#16a34a' }}>{stats.offers_received}</div>
        </div>
        <div className="stat-card">
          <div className="stat-title">Rejection Rate</div>
          <div className="stat-value" style={{ color: stats.rejection_rate > 50 ? '#dc2626' : '#475569' }}>
            {stats.rejection_rate}%
          </div>
        </div>
      </div>

      <div className="card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Status Breakdown</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
          {stats.status_breakdown && stats.status_breakdown.length > 0 ? (
            stats.status_breakdown.map((item, idx) => (
              <div
                key={idx}
                style={{
                  background: '#f1f5f9',
                  padding: '0.75rem 1.25rem',
                  borderRadius: '0.5rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem'
                }}
              >
                <span className={`badge badge-${item.status.toLowerCase()}`}>{item.status}</span>
                <span style={{ fontWeight: '700', fontSize: '1.1rem' }}>{item.count}</span>
              </div>
            ))
          ) : (
            <p style={{ color: 'var(--text-muted)' }}>No applications logged yet.</p>
          )}
        </div>
      </div>

      <div className="card">
        <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border)' }}>
          <h3 style={{ fontSize: '1.1rem' }}>Recent Activity</h3>
        </div>
        <div className="table-container">
          <table className="app-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Role</th>
                <th>Status</th>
                <th>Date Applied</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_applications && stats.recent_applications.length > 0 ? (
                stats.recent_applications.map((app) => (
                  <tr key={app.id}>
                    <td style={{ fontWeight: '600' }}>{app.company_name}</td>
                    <td>{app.role}</td>
                    <td>
                      <span className={`badge badge-${app.status.toLowerCase()}`}>
                        {app.status}
                      </span>
                    </td>
                    <td>{app.applied_date || 'N/A'}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                    No recent applications found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DashboardView;
