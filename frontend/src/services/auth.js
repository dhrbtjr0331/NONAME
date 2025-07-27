import { aiAgentAPI, coreAPI } from './api';


export const authService = {
  login: async (email, password) => {
    const response = await coreAPI.post('/auth/login', {
      email,
      password
    });
    return response.data;
  },

  register: async (email, password, isManufacturer) => {
    const response = await coreAPI.post('/auth/register', {
      email,
      password,
      is_manufacturer: isManufacturer
    });
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await coreAPI.get('/auth/me');
    return response.data;
  },

  refreshToken: async (refreshToken) => {
    const response = await coreAPI.post('/auth/refresh', {}, {
      headers: {
        Authorization: `Bearer ${refreshToken}`
      }
    });
    return response.data;
  }
};