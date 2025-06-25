import axios from "axios";

const API_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
});

// Function to set the authorization token
export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
};

// --- API Calls ---

export const login = (username, password) => {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);
  return api.post("/token", formData, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
};

export const signup = (name, username, password) => {
  return api.post("/users/signup", { name, username, password });
};

export const getCurrentUser = () => {
  return api.get("/users/me");
};

export const getHistory = () => {
  return api.get("/history");
};

export const getConversation = (conversationId) => {
  return api.get(`/history/${conversationId}`);
};

export const postChatMessage = (message, conversationId) => {
  return api.post("/chat", {
    user_message: message,
    conversation_id: conversationId,
  });
};

export default api;
