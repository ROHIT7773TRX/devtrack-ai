import React, { useState, useEffect } from 'react';

const ApplicationFormModal = ({ isOpen, onClose, onSubmit, initialData }) => {
  const [formData, setFormData] = useState({
    company_name: '',
    role: '',
    location: '',
    source: '',
    status: 'Applied',
    applied_date: new Date().toISOString().split('T')[0],
    salary_range: '',
    notes: '',
    job_url: ''
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        company_name: initialData.company_name || '',
        role: initialData.role || '',
        location: initialData.location || '',
        source: initialData.source || '',
        status: initialData.status || 'Applied',
        applied_date: initialData.applied_date || new Date().toISOString().split('T')[0],
        salary_range: initialData.salary_range || '',
        notes: initialData.notes || '',
        job_url: initialData.job_url || ''
      });
    } else {
      setFormData({
        company_name: '',
        role: '',
        location: '',
        source: '',
        status: 'Applied',
        applied_date: new Date().toISOString().split('T')[0],
        salary_range: '',
        notes: '',
        job_url: ''
      });
    }
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2 style={{ fontSize: '1.25rem', fontWeight: '700' }}>
            {initialData ? 'Edit Application' : 'New Job Application'}
          </h2>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', fontSize: '1.25rem', cursor: 'pointer' }}
          >
            ×
          </button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Company Name *</label>
            <input
              type="text"
              name="company_name"
              required
              className="form-input"
              value={formData.company_name}
              onChange={handleChange}
              placeholder="e.g. Google, Amazon, Startup Inc."
            />
          </div>

          <div className="form-group">
            <label className="form-label">Role / Job Title *</label>
            <input
              type="text"
              name="role"
              required
              className="form-input"
              value={formData.role}
              onChange={handleChange}
              placeholder="e.g. Software Engineer, DevOps Intern"
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Location</label>
              <input
                type="text"
                name="location"
                className="form-input"
                value={formData.location}
                onChange={handleChange}
                placeholder="e.g. Remote, Bangalore"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Status</label>
              <select
                name="status"
                className="form-select"
                value={formData.status}
                onChange={handleChange}
              >
                <option value="Applied">Applied</option>
                <option value="Screening">Screening</option>
                <option value="Interview">Interview</option>
                <option value="Offer">Offer</option>
                <option value="Rejected">Rejected</option>
                <option value="Withdrawn">Withdrawn</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Source</label>
              <input
                type="text"
                name="source"
                className="form-input"
                value={formData.source}
                onChange={handleChange}
                placeholder="e.g. LinkedIn, Referral"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Applied Date</label>
              <input
                type="date"
                name="applied_date"
                className="form-input"
                value={formData.applied_date}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Notes</label>
            <textarea
              name="notes"
              className="form-textarea"
              rows="3"
              value={formData.notes}
              onChange={handleChange}
              placeholder="Additional details, referral contact, notes..."
            />
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              {initialData ? 'Save Changes' : 'Create Application'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ApplicationFormModal;
