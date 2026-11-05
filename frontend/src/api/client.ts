import axios from 'axios';

const customUrl = typeof window !== 'undefined' ? localStorage.getItem('custom_api_url') : null;
const rawEnv = (import.meta as any).env?.VITE_API_URL;
let API_BASE = '/api';

if (customUrl) {
  const trimmed = customUrl.trim().replace(/\/$/, '');
  API_BASE = trimmed.startsWith('http://') || trimmed.startsWith('https://') 
    ? `${trimmed}/api` 
    : `https://${trimmed}/api`;
} else if (rawEnv && rawEnv !== 'undefined') {
  const trimmed = String(rawEnv).trim().replace(/\/$/, '');
  API_BASE = trimmed.startsWith('http://') || trimmed.startsWith('https://') 
    ? `${trimmed}/api` 
    : `https://${trimmed}/api`;
}

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register' && window.location.pathname !== '/') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;

