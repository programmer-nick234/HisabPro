import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        if (typeof window !== 'undefined') {
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
              refresh: refreshToken,
            });

            const { access } = response.data;
            localStorage.setItem('access_token', access);

            originalRequest.headers.Authorization = `Bearer ${access}`;
            return api(originalRequest);
          }
        }
      } catch (refreshError) {
        // Refresh token failed, redirect to login
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data: any) => api.post('/auth/register/', data),
  login: (data: any) => api.post('/auth/login/', data),
  logout: (data: any) => api.post('/auth/logout/', data),
  getUser: () => api.get('/auth/user/'),
  updateProfile: (data: any) => api.put('/auth/profile/', data),
  changePassword: (data: any) => api.post('/auth/change-password/', data),
};

// Invoice API
export const invoiceAPI = {
  getInvoices: (params?: any) => api.get('/invoices/', { params }),
  getInvoice: (id: string) => api.get(`/invoices/${id}/`),
  createInvoice: (data: any) => api.post('/invoices/', data),
  updateInvoice: (id: string, data: any) => api.put(`/invoices/${id}/`, data),
  deleteInvoice: (id: string) => api.delete(`/invoices/${id}/`),
  getSummary: () => api.get('/invoices/summary/'),
  getRecent: () => api.get('/invoices/recent/'),
  generateRazorpayLink: (id: string) => api.post(`/invoices/${id}/razorpay-link/`),
  downloadPDF: (id: string) => api.get(`/invoices/${id}/pdf/`, { responseType: 'blob' }),
  sendReminder: (id: string, data?: any) => api.post(`/invoices/${id}/send-reminder/`, data),
  markAsPaid: (id: string) => api.post(`/invoices/${id}/mark-paid/`),
};

export default api;
