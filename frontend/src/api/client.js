import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper functions for common API tasks
const client = {
  get: async (url, config = {}) => {
    try {
      const response = await api.get(url, config);
      return response.data;
    } catch (error) {
      console.error(`API GET Error [${url}]:`, error);
      throw error;
    }
  },

  post: async (url, data = {}, config = {}) => {
    try {
      const response = await api.post(url, data, config);
      return response.data;
    } catch (error) {
      console.error(`API POST Error [${url}]:`, error);
      throw error;
    }
  },

  put: async (url, data = {}, config = {}) => {
    try {
      const response = await api.put(url, data, config);
      return response.data;
    } catch (error) {
      console.error(`API PUT Error [${url}]:`, error);
      throw error;
    }
  },

  delete: async (url, config = {}) => {
    try {
      const response = await api.delete(url, config);
      return response.data;
    } catch (error) {
      console.error(`API DELETE Error [${url}]:`, error);
      throw error;
    }
  },

  // Specific BigDaddy routes can be added here as methods
  getMonitorStats: () => client.get('/monitor/stats'),
  getAlerts: () => client.get('/alerts'),
  getScholarResults: (query) => client.get(`/scholar/scan?q=${query}`),
  updateSettings: (settings) => client.post('/settings/update', settings),
};

export default client;
