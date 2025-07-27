import { aiAgentAPI } from './api';

export const rfqAssistantService = {
  async sendMessage(message, sessionId, userId) {
    try {
      const response = await aiAgentAPI.post('/api/v1/rfq-assistant/rfq', {
        message,
        session_id: sessionId,
        user_id: userId
      });
      return response.data;
    } catch (error) {
      console.error('Error sending message to RFQ Assistant:', error);
      throw error;
    }
  }
};