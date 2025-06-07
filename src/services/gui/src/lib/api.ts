import axios from "axios";

const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8002";

export const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error);
    if (error.response?.status === 404) {
      throw new Error("Service not available");
    }
    if (error.response?.status >= 500) {
      throw new Error("Server error occurred");
    }
    throw error;
  }
);
