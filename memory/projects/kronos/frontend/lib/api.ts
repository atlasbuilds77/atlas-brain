// ============================================
// KRONOS API CLIENT
// ============================================

import type {
  Lead, Client, Message, MessageThread, TaxOrganizer,
  Task, AnalyticsSummary, LeadSourceData, TimeSeriesData,
  ApiResponse, PaginatedResponse, LeadFilters, ClientFilters, MessageFilters,
  User, OrganizerTemplate
} from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

// Generic fetch wrapper
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

// Build query string from object
function buildQuery(params: Record<string, any>): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (Array.isArray(value)) {
        value.forEach(v => searchParams.append(key, v));
      } else {
        searchParams.append(key, String(value));
      }
    }
  });
  const query = searchParams.toString();
  return query ? `?${query}` : '';
}

// ============================================
// AUTH API
// ============================================
export const authApi = {
  getCurrentUser: () =>
    apiFetch<ApiResponse<User>>('/auth/me'),
  
  login: (email: string, password: string) =>
    apiFetch<ApiResponse<{ user: User; token: string }>>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  
  logout: () =>
    apiFetch<ApiResponse<void>>('/auth/logout', { method: 'POST' }),
};

// ============================================
// LEADS API
// ============================================
export const leadsApi = {
  list: (filters?: LeadFilters, page = 1, pageSize = 20) =>
    apiFetch<PaginatedResponse<Lead>>(
      `/leads${buildQuery({ ...filters, page, pageSize })}`
    ),
  
  get: (id: string) =>
    apiFetch<ApiResponse<Lead>>(`/leads/${id}`),
  
  create: (data: Partial<Lead>) =>
    apiFetch<ApiResponse<Lead>>('/leads', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  update: (id: string, data: Partial<Lead>) =>
    apiFetch<ApiResponse<Lead>>(`/leads/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  
  delete: (id: string) =>
    apiFetch<ApiResponse<void>>(`/leads/${id}`, { method: 'DELETE' }),
  
  convert: (id: string) =>
    apiFetch<ApiResponse<Client>>(`/leads/${id}/convert`, { method: 'POST' }),
  
  qualify: (id: string, answers: Record<string, string>) =>
    apiFetch<ApiResponse<{ score: number }>>(`/leads/${id}/qualify`, {
      method: 'POST',
      body: JSON.stringify({ answers }),
    }),
};

// ============================================
// CLIENTS API
// ============================================
export const clientsApi = {
  list: (filters?: ClientFilters, page = 1, pageSize = 20) =>
    apiFetch<PaginatedResponse<Client>>(
      `/clients${buildQuery({ ...filters, page, pageSize })}`
    ),
  
  get: (id: string) =>
    apiFetch<ApiResponse<Client>>(`/clients/${id}`),
  
  update: (id: string, data: Partial<Client>) =>
    apiFetch<ApiResponse<Client>>(`/clients/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  
  getFiles: (id: string, year?: number) =>
    apiFetch<ApiResponse<{ files: import('@/types').ClientFile[] }>>(
      `/clients/${id}/files${buildQuery({ year })}`
    ),
  
  uploadFile: (id: string, file: File, category: string, year?: number) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    if (year) formData.append('year', String(year));
    
    return fetch(`${API_BASE}/clients/${id}/files`, {
      method: 'POST',
      body: formData,
    }).then(res => res.json());
  },
  
  getCommunicationHistory: (id: string, limit = 50) =>
    apiFetch<ApiResponse<Message[]>>(
      `/clients/${id}/communications${buildQuery({ limit })}`
    ),
};

// ============================================
// MESSAGES API
// ============================================
export const messagesApi = {
  listThreads: (filters?: MessageFilters, page = 1, pageSize = 20) =>
    apiFetch<PaginatedResponse<MessageThread>>(
      `/messages/threads${buildQuery({ ...filters, page, pageSize })}`
    ),
  
  getThread: (threadId: string) =>
    apiFetch<ApiResponse<{ thread: MessageThread; messages: Message[] }>>(
      `/messages/threads/${threadId}`
    ),
  
  send: (data: {
    to: string[];
    subject?: string;
    body: string;
    channel: import('@/types').MessageChannel;
    threadId?: string;
  }) =>
    apiFetch<ApiResponse<Message>>('/messages', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  markAsRead: (ids: string[]) =>
    apiFetch<ApiResponse<void>>('/messages/mark-read', {
      method: 'POST',
      body: JSON.stringify({ ids }),
    }),
  
  archive: (ids: string[]) =>
    apiFetch<ApiResponse<void>>('/messages/archive', {
      method: 'POST',
      body: JSON.stringify({ ids }),
    }),
  
  updateCategory: (ids: string[], category: import('@/types').MessageCategory) =>
    apiFetch<ApiResponse<void>>('/messages/categorize', {
      method: 'POST',
      body: JSON.stringify({ ids, category }),
    }),
};

// ============================================
// TAX ORGANIZERS API
// ============================================
export const organizersApi = {
  list: (filters?: { status?: string; year?: number }, page = 1, pageSize = 20) =>
    apiFetch<PaginatedResponse<TaxOrganizer>>(
      `/organizers${buildQuery({ ...filters, page, pageSize })}`
    ),
  
  get: (id: string) =>
    apiFetch<ApiResponse<TaxOrganizer>>(`/organizers/${id}`),
  
  create: (data: { clientId: string; templateId: string; year: number; dueDate?: string }) =>
    apiFetch<ApiResponse<TaxOrganizer>>('/organizers', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  send: (id: string) =>
    apiFetch<ApiResponse<TaxOrganizer>>(`/organizers/${id}/send`, { method: 'POST' }),
  
  remind: (id: string) =>
    apiFetch<ApiResponse<void>>(`/organizers/${id}/remind`, { method: 'POST' }),
  
  download: (id: string) =>
    `${API_BASE}/organizers/${id}/download`,
  
  getTemplates: () =>
    apiFetch<ApiResponse<OrganizerTemplate[]>>('/organizers/templates'),
};

// ============================================
// TASKS API
// ============================================
export const tasksApi = {
  list: (filters?: { status?: string; assignedTo?: string }, page = 1, pageSize = 20) =>
    apiFetch<PaginatedResponse<Task>>(
      `/tasks${buildQuery({ ...filters, page, pageSize })}`
    ),
  
  create: (data: Partial<Task>) =>
    apiFetch<ApiResponse<Task>>('/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  update: (id: string, data: Partial<Task>) =>
    apiFetch<ApiResponse<Task>>(`/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  
  complete: (id: string) =>
    apiFetch<ApiResponse<Task>>(`/tasks/${id}/complete`, { method: 'POST' }),
};

// ============================================
// ANALYTICS API
// ============================================
export const analyticsApi = {
  getSummary: () =>
    apiFetch<ApiResponse<AnalyticsSummary>>('/analytics/summary'),
  
  getLeadSources: (dateFrom?: string, dateTo?: string) =>
    apiFetch<ApiResponse<LeadSourceData[]>>(
      `/analytics/lead-sources${buildQuery({ dateFrom, dateTo })}`
    ),
  
  getConversionTrend: (period: 'week' | 'month' | 'year' = 'month') =>
    apiFetch<ApiResponse<TimeSeriesData[]>>(
      `/analytics/conversion-trend${buildQuery({ period })}`
    ),
  
  getRetention: () =>
    apiFetch<ApiResponse<import('@/types').RetentionData[]>>('/analytics/retention'),
  
  getRevenue: (period: 'week' | 'month' | 'year' = 'month') =>
    apiFetch<ApiResponse<TimeSeriesData[]>>(
      `/analytics/revenue${buildQuery({ period })}`
    ),
};

// ============================================
// DASHBOARD API
// ============================================
export const dashboardApi = {
  getTodaySummary: () =>
    apiFetch<ApiResponse<{
      newLeads: number;
      pendingTasks: number;
      unreadMessages: number;
      organizersDue: number;
      recentActivity: Array<{
        id: string;
        type: 'lead' | 'message' | 'task' | 'organizer';
        description: string;
        timestamp: string;
      }>;
    }>>('/dashboard/today'),
  
  getPendingTasks: (limit = 5) =>
    apiFetch<ApiResponse<Task[]>>(`/dashboard/tasks${buildQuery({ limit })}`),
  
  getRecentMessages: (limit = 5) =>
    apiFetch<ApiResponse<Message[]>>(`/dashboard/messages${buildQuery({ limit })}`),
};

// Export all APIs
export const api = {
  auth: authApi,
  leads: leadsApi,
  clients: clientsApi,
  messages: messagesApi,
  organizers: organizersApi,
  tasks: tasksApi,
  analytics: analyticsApi,
  dashboard: dashboardApi,
};

export default api;
