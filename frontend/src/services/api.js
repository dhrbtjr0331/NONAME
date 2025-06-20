import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost';

// Service URLs
export const SERVICES = {
  AUTH: `${API_BASE_URL}:8001`,
  USER: `${API_BASE_URL}:8002`, 
  QUOTE: `${API_BASE_URL}:8003`,
  NOTIFICATION: `${API_BASE_URL}:8004`
};

// Create axios instances for each service
export const authAPI = axios.create({
  baseURL: SERVICES.AUTH,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const userAPI = axios.create({
  baseURL: SERVICES.USER,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const quoteAPI = axios.create({
  baseURL: SERVICES.QUOTE,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const notificationAPI = axios.create({
  baseURL: SERVICES.NOTIFICATION,
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

// Add interceptors to all APIs
[userAPI, quoteAPI, notificationAPI].forEach(api => {
  api.interceptors.request.use(addAuthToken);
  
  // Handle 401 responses
  api.interceptors.response.use(
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
});

export default {
  auth: authAPI,
  user: userAPI,
  quote: quoteAPI,
  notification: notificationAPI
};