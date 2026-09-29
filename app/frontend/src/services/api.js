// ============================================================
// services/api.js
// Axios HTTP client module for backend API communication.
//
// API base URL defaults to http://localhost:8000 (FastAPI default)
// In production / Docker / K8s, it can be set via REACT_APP_API_URL.
// ============================================================

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getDashboardStats = async () => {
  const response = await api.get('/dashboard/');
  return response.data;
};

export const getApplications = async (statusFilter = null) => {
  const params = statusFilter ? { status: statusFilter } : {};
  const response = await api.get('/applications/', { params });
  return response.data;
};

export const getApplicationById = async (id) => {
  const response = await api.get(`/applications/${id}`);
  return response.data;
};

export const createApplication = async (applicationData) => {
  const response = await api.post('/applications/', applicationData);
  return response.data;
};

export const updateApplication = async (id, updateData) => {
  const response = await api.patch(`/applications/${id}`, updateData);
  return response.data;
};

export const deleteApplication = async (id) => {
  const response = await api.delete(`/applications/${id}`);
  return response.data;
};

export const addInterviewRound = async (applicationId, roundData) => {
  const response = await api.post(`/applications/${applicationId}/interviews`, roundData);
  return response.data;
};

export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
