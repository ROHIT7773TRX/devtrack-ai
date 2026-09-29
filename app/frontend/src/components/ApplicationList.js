import React from 'react';

const ApplicationList = ({
  applications,
  loading,
  statusFilter,
  setStatusFilter,
  onNewApplication,
  onEditApplication,
  onDeleteApplication
}) => {
  const statuses = ['All', 'Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn'];

  return (
    <div>
      <div className="section-header">
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: '700' }}>Job Applications</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Track and manage all your ongoing job applications</p>
        </div>
        <button className="btn-primary" onClick={onNewApplication}>
          + Add Application
        </button>
      </div>

      {/* Filter Toolbar */}
      <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        {statuses.map((status) => (
          <button
            key={status}
            className={`btn-secondary ${
              (statusFilter === null && status === 'All') || statusFilter === status
                ? 'btn-primary'
                : ''
            }`}
            style={{ fontSize: '0.85rem', padding: '0.4rem 0.85rem' }}
            onClick={() => setStatusFilter(status === 'All' ? null : status)}
          >
            {status}
          </button>
        ))}
      </div>

      <div className="card">
        <div className="table-container">
          <table className="app-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Role</th>
                <th>Location</th>
                <th>Source</th>
                <th>Status</th>
                <th>Applied Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '2rem' }}>
                    Loading applications...
                  </td>
                </tr>
              ) : applications.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                    No job applications match the selected filter.
                  </td>
                </tr>
              ) : (
                applications.map((app) => (
                  <tr key={app.id}>
                    <td style={{ fontWeight: '600' }}>{app.company_name}</td>
                    <td>{app.role}</td>
                    <td>{app.location || '—'}</td>
                    <td>{app.source || '—'}</td>
                    <td>
                      <span className={`badge badge-${app.status.toLowerCase()}`}>
                        {app.status}
                      </span>
                    </td>
                    <td>{app.applied_date || '—'}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                          className="btn-secondary"
                          style={{ padding: '0.25rem 0.6rem', fontSize: '0.8rem' }}
                          onClick={() => onEditApplication(app)}
                        >
                          Edit
                        </button>
                        <button
                          className="btn-danger"
                          onClick={() => onDeleteApplication(app.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ApplicationList;
