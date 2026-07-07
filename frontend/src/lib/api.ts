// API client for Expiry Copilot

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

// Helper to get auth headers
export function getAuthHeaders() {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("expiry_copilot_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// Check if authenticated
export function isAuthenticated() {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("expiry_copilot_token");
}

// Clean fetch wrapper
async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...getAuthHeaders(),
    ...options.headers,
  };

  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
    
    if (res.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("expiry_copilot_token");
        localStorage.removeItem("expiry_copilot_user");
        window.location.reload();
      }
      throw new Error("Unauthorized");
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "API Error" }));
      throw new Error(err.detail || "API Request failed");
    }

    return await res.json();
  } catch (error) {
    console.error(`API Fetch Error [${endpoint}]:`, error);
    throw error;
  }
}

// Authentication API
export const authApi = {
  login: async (username: string, password: string) => {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(err.detail || "Authentication failed");
    }
    const data = await res.json();
    if (typeof window !== "undefined") {
      localStorage.setItem("expiry_copilot_token", data.access_token);
      localStorage.setItem("expiry_copilot_user", JSON.stringify(data.user));
    }
    return data;
  },
  googleLogin: async (credential: string) => {
    const res = await fetch(`${API_BASE_URL}/auth/google`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ credential }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Google login failed" }));
      throw new Error(err.detail || "Google authentication failed");
    }
    const data = await res.json();
    if (typeof window !== "undefined") {
      localStorage.setItem("expiry_copilot_token", data.access_token);
      localStorage.setItem("expiry_copilot_user", JSON.stringify(data.user));
    }
    return data;
  },
  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("expiry_copilot_token");
      localStorage.removeItem("expiry_copilot_user");
    }
  },
  me: async () => {
    return apiFetch("/auth/me");
  }
};

// Dashboard & Analytics
export const dashboardApi = {
  getStats: async () => apiFetch("/dashboard/stats"),
  getForecast: async () => apiFetch("/dashboard/forecast"),
};

// Products & Batches
export const productsApi = {
  list: async (category?: string, search?: string) => {
    let url = "/products";
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    if (search) params.append("search", search);
    const queryStr = params.toString();
    if (queryStr) url += `?${queryStr}`;
    return apiFetch(url);
  },
  get: async (id: number) => apiFetch(`/products/${id}`),
  create: async (productData: any) => apiFetch("/products", {
    method: "POST",
    body: JSON.stringify(productData),
  }),
  update: async (id: number, productData: any) => apiFetch(`/products/${id}`, {
    method: "PUT",
    body: JSON.stringify(productData),
  }),
  createBatch: async (batchData: any) => apiFetch("/batches", {
    method: "POST",
    body: JSON.stringify(batchData),
  }),
  listBatches: async () => apiFetch("/batches"),
  recordSale: async (saleData: any) => apiFetch("/sales", {
    method: "POST",
    body: JSON.stringify(saleData),
  }),
  listSales: async () => apiFetch("/sales"),
};

// Recommendations & Alerts
export const insightsApi = {
  listRecommendations: async (status: string = "pending") => apiFetch(`/recommendations?status=${status}`),
  applyRecommendation: async (id: number) => apiFetch(`/recommendations/${id}/apply`, { method: "POST" }),
  dismissRecommendation: async (id: number) => apiFetch(`/recommendations/${id}/dismiss`, { method: "POST" }),
  listAlerts: async (status: string = "active") => apiFetch(`/alerts?status=${status}`),
};

// Copilot AI Tools
export const copilotApi = {
  chat: async (query: string) => apiFetch("/copilot/chat", {
    method: "POST",
    body: JSON.stringify({ query }),
  }),
  textToSql: async (query: string) => apiFetch("/copilot/sql", {
    method: "POST",
    body: JSON.stringify({ query }),
  }),
  ocrScan: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    
    const token = localStorage.getItem("expiry_copilot_token");
    const headers: any = token ? { Authorization: `Bearer ${token}` } : {};

    const res = await fetch(`${API_BASE_URL}/copilot/ocr`, {
      method: "POST",
      headers,
      body: formData,
    });
    if (!res.ok) throw new Error("OCR Upload failed");
    return res.json();
  }
};

// Time Simulator
export const simulatorApi = {
  shift: async (days: number) => apiFetch("/simulation/shift", {
    method: "POST",
    body: JSON.stringify({ days }),
  }),
  status: async () => apiFetch("/simulation/status"),
  reset: async () => apiFetch("/simulation/reset", { method: "POST" }),
};

// Report Downloader
export const reportsApi = {
  download: async (type: string) => apiFetch(`/reports/download?type=${type}`),
};
