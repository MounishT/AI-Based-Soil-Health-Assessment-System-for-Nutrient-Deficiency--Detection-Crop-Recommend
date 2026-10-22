/**
 * Centralized API configuration and utility functions.
 */

export const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

/**
 * Generic fetch wrapper to handle JSON errors automatically.
 * Attaches JWT token from localStorage if available.
 * @param {string} endpoint - API endpoint (e.g., "/analyze")
 * @param {object} options - Fetch options (method, headers, body)
 * @returns {Promise<any>}
 */
export const apiFetch = async (endpoint, options = {}) => {
  const url = `${API_URL}${endpoint}`;

  const headers = { ...options.headers };
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token && !headers["Authorization"]) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  try {
    const response = await fetch(url, { ...options, headers });

    // Check if the response has content
    const isJson = response.headers.get("content-type")?.includes("application/json");
    const data = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const errorMessage = data?.detail || data?.message || (typeof data === 'string' ? data : `API Error: ${response.status}`);
      throw new Error(errorMessage);
    }

    return data;
  } catch (error) {
    if (error instanceof TypeError && error.message === "Failed to fetch") {
      throw new Error("Backend is not running or unreachable. Please check server.");
    }
    throw error;
  }
};
