import { coreAPI, aiAgentAPI } from './api';

export const rfqService = {
  // Manufacturer functions; CORE API
  createRFQ: async (rfqData) => {
    const response = await coreAPI.post('/rfqs/', rfqData);
    return response.data;
  },

  getMyRFQs: async (params = {}) => {
    const response = await coreAPI.get('/rfqs/my-rfqs', { params });
    return response.data;
  },

  getRFQById: async (rfqId) => {
    const response = await coreAPI.get(`/rfqs/${rfqId}`);
    return response.data;
  },

  updateRFQ: async (rfqId, updateData) => {
    const response = await coreAPI.put(`/rfqs/${rfqId}`, updateData);
    return response.data;
  },

  closeRFQ: async (rfqId) => {
    const response = await coreAPI.post(`/rfqs/${rfqId}/close`);
    return response.data;
  },

  getQuotesForRFQ: async (rfqId) => {
    const response = await coreAPI.get(`/quotes/rfq/${rfqId}`);
    return response.data;
  },

  // Manufacturer functions; AI AGENT API
  submitAiQuery: async () => {
    const response = await aiAgentAPI.post('/api/v1/rfq-assistant/rfq');
    return response.data;
  },

  // Supplier functions
  getPublicRFQs: async (params = {}) => {
    const response = await coreAPI.get('/rfqs/', { params });
    return response.data;
  }
};