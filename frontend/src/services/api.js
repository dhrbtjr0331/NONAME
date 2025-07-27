import axios from 'axios';

const CORE_API_SERVICE_BASE_URL = process.env.CORE_API_SERVICE_BASE_URL || 'http://localhost:8000';
const AI_AGENT_API_SERVICE_BASE_URL = process.env.AI_AGENT_API_SERVICE_BASE_URL || 'http://localhost:8002';

// CORE API instance
export const coreAPI = axios.create({
  baseURL: CORE_API_SERVICE_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// AI AGENT API instance
export const aiAgentAPI = axios.create({
  baseURL: AI_AGENT_API_SERVICE_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});
// Add auth token to requests
const addAuthToken = (config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

// Add interceptors
coreAPI.interceptors.request.use(addAuthToken);
aiAgentAPI.interceptors.request.use(addAuthToken);

// Handle 401 responses
coreAPI.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default {coreAPI, aiAgentAPI};