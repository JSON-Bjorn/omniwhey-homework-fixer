import axios from 'axios';

// Create an axios instance with base URL and default headers
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// When in browser, replace backend:8000 with localhost:8000
const finalApiUrl = API_URL.replace('backend:8000', 'localhost:8000');

const api = axios.create({
    baseURL: finalApiUrl,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add request interceptor to attach auth token to requests
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Add response interceptor to handle common errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle 401 Unauthorized - redirect to login
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('auth_token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    login: (email: string, password: string) => {
        // Use URLSearchParams for proper x-www-form-urlencoded formatting
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);

        return api.post('/token', params, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });
    },

    register: (email: string, password: string, full_name: string) => {
        return api.post('/api/users', { email, password, full_name });
    },

    getCurrentUser: () => api.get('/users/me'),
};

// Templates API
export const templatesAPI = {
    getTemplates: () => api.get('/api/templates'),

    getTemplate: (id: number) => api.get(`/api/templates/${id}`),

    createTemplate: (data: { title: string, description?: string, structure: string, is_public: boolean }) =>
        api.post('/api/templates', data),

    updateTemplate: (id: number, data: { title?: string, description?: string, structure?: string, is_public?: boolean }) =>
        api.put(`/api/templates/${id}`, data),

    deleteTemplate: (id: number) => api.delete(`/api/templates/${id}`),
};

// PRDs API
export const prdsAPI = {
    getPRDs: () => api.get('/api/prds'),

    getPRD: (id: number) => api.get(`/api/prds/${id}`),

    createPRD: (data: { title: string, content: string, template_id?: number }) =>
        api.post('/api/prds', data),

    updatePRD: (id: number, data: { title?: string, content?: string }) =>
        api.put(`/api/prds/${id}`, data),

    deletePRD: (id: number) => api.delete(`/api/prds/${id}`),
};

// Collaborations API
export const collaborationsAPI = {
    getCollaborators: (prdId: number) =>
        api.get(`/api/collaborations/prd/${prdId}`),

    addCollaborator: (prdId: number, userId: number, permission: string) =>
        api.post('/api/collaborations', { prd_id: prdId, user_id: userId, permission }),

    updateCollaborator: (id: number, permission: string) =>
        api.put(`/api/collaborations/${id}`, { permission }),

    removeCollaborator: (id: number) =>
        api.delete(`/api/collaborations/${id}`),
};

// Submissions API
export const submissionsAPI = {
    getSubmissions: (status?: string) => {
        const params = status ? { status } : {};
        return api.get('/api/submissions', { params });
    },

    getSubmission: (id: number) =>
        api.get(`/api/submissions/${id}`),

    createSubmission: (formData: FormData) =>
        api.post('/api/submissions', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        }),

    updateSubmission: (id: number, data: { title?: string, description?: string, status?: string }) =>
        api.put(`/api/submissions/${id}`, data),

    deleteSubmission: (id: number) =>
        api.delete(`/api/submissions/${id}`),

    downloadSubmission: (id: number) =>
        api.get(`/api/submissions/${id}/download`, { responseType: 'blob' }),
};

// Feedback API
export const feedbackAPI = {
    getSubmissionFeedback: (submissionId: number) =>
        api.get(`/api/feedback/submission/${submissionId}`),

    createFeedback: (data: { submission_id: number, content: string, grade?: string }) =>
        api.post('/api/feedback', data),

    updateFeedback: (id: number, data: { content?: string, grade?: string }) =>
        api.put(`/api/feedback/${id}`, data),

    deleteFeedback: (id: number) =>
        api.delete(`/api/feedback/${id}`),
};

// Admin API
export const adminAPI = {
    // User management
    getUsers: (page: number = 1, pageSize: number = 10, search?: string) => {
        const params = { page, page_size: pageSize, ...(search && { search }) };
        return api.get('/api/admin/users', { params });
    },

    updateUser: (id: number, data: { is_active?: boolean, is_admin?: boolean }) =>
        api.put(`/api/admin/users/${id}`, data),

    // Submission management
    getSubmissions: (page: number = 1, pageSize: number = 10, status?: string, userId?: number) => {
        const params = {
            page,
            page_size: pageSize,
            ...(status && { status }),
            ...(userId && { user_id: userId })
        };
        return api.get('/api/admin/submissions', { params });
    },

    // Statistics and analytics
    getStats: () => api.get('/api/admin/stats'),
};

export default api; 