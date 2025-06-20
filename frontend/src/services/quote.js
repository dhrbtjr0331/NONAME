import { quoteAPI } from './api';

export const quoteService = {
  createQuote: async (quoteData) => {
    const response = await quoteAPI.post('/quotes/', quoteData);
    return response.data;
  },

  getMyQuotes: async (params = {}) => {
    const response = await quoteAPI.get('/quotes/my-quotes', { params });
    return response.data;
  },

  getQuoteById: async (quoteId) => {
    const response = await quoteAPI.get(`/quotes/${quoteId}`);
    return response.data;
  },

  updateQuote: async (quoteId, updateData) => {
    const response = await quoteAPI.put(`/quotes/${quoteId}`, updateData);
    return response.data;
  },

  submitQuote: async (quoteId) => {
    const response = await quoteAPI.post(`/quotes/${quoteId}/submit`);
    return response.data;
  },

  withdrawQuote: async (quoteId) => {
    const response = await quoteAPI.post(`/quotes/${quoteId}/withdraw`);
    return response.data;
  },

  acceptQuote: async (quoteId) => {
    const response = await quoteAPI.post(`/quotes/${quoteId}/accept`);
    return response.data;
  }
};