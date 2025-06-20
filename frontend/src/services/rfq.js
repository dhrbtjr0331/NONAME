import { quoteAPI } from './api';

export const rfqService = {
  // Manufacturer functions
  createRFQ: async (rfqData) => {
    const response = await quoteAPI.post('/rfqs/', rfqData);
    return response.data;
  },

  getMyRFQs: async (params = {}) => {
    const response = await quoteAPI.get('/rfqs/my-rfqs', { params });
    return response.data;
  },

  getRFQById: async (rfqId) => {
    const response = await quoteAPI.get(`/rfqs/${rfqId}`);
    return response.data;
  },

  updateRFQ: async (rfqId, updateData) => {
    const response = await quoteAPI.put(`/rfqs/${rfqId}`, updateData);
    return response.data;
  },

  closeRFQ: async (rfqId) => {
    const response = await quoteAPI.post(`/rfqs/${rfqId}/close`);
    return response.data;
  },

  getQuotesForRFQ: async (rfqId) => {
    const response = await quoteAPI.get(`/quotes/rfq/${rfqId}`);
    return response.data;
  },

  // Supplier functions
  getPublicRFQs: async (params = {}) => {
    const response = await quoteAPI.get('/rfqs/', { params });
    return response.data;
  }
};