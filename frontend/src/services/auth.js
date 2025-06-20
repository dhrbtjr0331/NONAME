import { authAPI } from './api';

export const authService = {
  login: async (email, password) => {
    const response = await authAPI.post('/auth/login', {
      email,
      password
    });
    return response.data;
  },

  register: async (email, password, isManufacturer) => {
    const response = await authAPI.post('/auth/register', {
      email,
      password,
      is_manufacturer: isManufacturer
    });
    return response.data;
  },

  getCurrentUser: async (token) => {
    const response = await authAPI.get('/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  },

  refreshToken: async (refreshToken) => {
    const response = await authAPI.post('/auth/refresh', {}, {
      headers: {
        Authorization: `Bearer ${refreshToken}`
      }
    });
    return response.data;
  }
};