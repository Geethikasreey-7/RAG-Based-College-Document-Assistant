import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const documentAPI = {
  list: async () => {
    const response = await apiClient.get("/api/documents");
    return response.data;
  },

  upload: async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiClient.post("/api/documents/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress,
    });

    return response.data;
  },

  delete: async (filename) => {
    const response = await apiClient.delete(`/api/documents/${filename}`);
    return response.data;
  },
};

export const conversationAPI = {
  create: async (title) => {
    const response = await apiClient.post("/api/conversations", { title });
    return response.data;
  },

  list: async () => {
    const response = await apiClient.get("/api/conversations");
    return response.data;
  },

  get: async (conversationId) => {
    const response = await apiClient.get(`/api/conversations/${conversationId}`);
    return response.data;
  },

  addMessage: async (conversationId, role, content) => {
    const response = await apiClient.post(`/api/conversations/${conversationId}/messages`, {
      role,
      content,
    });
    return response.data;
  },

  delete: async (conversationId) => {
    const response = await apiClient.delete(`/api/conversations/${conversationId}`);
    return response.data;
  },
};

export const searchAPI = {
  search: async (query) => {
    const response = await apiClient.post("/api/search", { query });
    return response.data;
  },
};

export const chatAPI = {
  chat: async (question, conversationId = null) => {
    const response = await apiClient.post("/api/chat", {
      question,
      conversation_id: conversationId,
    });
    return response.data;
  },
};

export default apiClient;
