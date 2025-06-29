import coreAPI from './api';

export const userService = {
  // Profile management
  createProfile: async (profileData) => {
    const response = await coreAPI.post('/users/profile', profileData);
    return response.data;
  },

  getMyProfile: async () => {
    const response = await coreAPI.get('/users/profile');
    return response.data;
  },

  updateProfile: async (updateData) => {
    const response = await coreAPI.put('/users/profile', updateData);
    return response.data;
  },

  getUserProfile: async (userId) => {
    const response = await coreAPI.get(`/users/profile/${userId}`);
    return response.data;
  },

  // Company management
  createCompany: async (companyData) => {
    const response = await coreAPI.post('/companies/', companyData);
    return response.data;
  },

  getMyCompany: async () => {
    const response = await coreAPI.get('/companies/my-company');
    return response.data;
  },

  updateCompany: async (updateData) => {
    const response = await coreAPI.put('/companies/my-company', updateData);
    return response.data;
  },

  getCompanyById: async (companyId) => {
    const response = await coreAPI.get(`/companies/${companyId}`);
    return response.data;
  },

  listCompanies: async (params = {}) => {
    const response = await coreAPI.get('/companies/', { params });
    return response.data;
  }
};