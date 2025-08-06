import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for API responses
export interface BackendTask {
  id: string;
  title: string;
  status: string;
  created_at: string;
}

export interface BackendMessage {
  id: string;
  task_id: string;
  role: string;
  content: any;
  ordering: number;
  created_at: string;
}

export interface BackendEvent {
  id: string;
  task_id: string;
  kind: string;
  ordering: number;
  payload: any;
  created_at: string;
}

export interface BackendScreenshot {
  id: string;
  event_id: string;
  url: string;
  sha256: string;
}

export interface BackendMedia {
  id: string;
  task_id: string;
  uploaded_by: string;
  filename: string;
  content_type: string;
  url: string;
  sha256: string;
  created_at: string;
}

// Task API
export const taskAPI = {
  create: async (data: { title: string; status?: string }): Promise<BackendTask> => {
    const response = await api.post('/tasks/', data);
    return response.data;
  },

  getAll: async (): Promise<BackendTask[]> => {
    const response = await api.get('/tasks/');
    return response.data;
  },

  getById: async (id: string): Promise<BackendTask> => {
    const response = await api.get(`/tasks/${id}`);
    return response.data;
  },

  update: async (id: string, data: { title?: string; status?: string }): Promise<BackendTask> => {
    const response = await api.patch(`/tasks/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/tasks/${id}`);
  },

  start: async (id: string): Promise<{ detail: string }> => {
    const response = await api.post(`/tasks/${id}/start`);
    return response.data;
  },
};

// Message API
export const messageAPI = {
  create: async (data: {
    task_id: string;
    role: string;
    content: any;
    ordering: number;
  }): Promise<BackendMessage> => {
    const response = await api.post('/messages/', data);
    return response.data;
  },

  getByTask: async (taskId: string): Promise<BackendMessage[]> => {
    const response = await api.get(`/messages/by-task/${taskId}`);
    return response.data;
  },

  getById: async (id: string): Promise<BackendMessage> => {
    const response = await api.get(`/messages/${id}`);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/messages/${id}`);
  },
};

// Event API
export const eventAPI = {
  create: async (data: {
    task_id: string;
    kind: string;
    payload: any;
    ordering: number;
  }): Promise<BackendEvent> => {
    const response = await api.post('/events/', data);
    return response.data;
  },

  getByTask: async (taskId: string): Promise<BackendEvent[]> => {
    const response = await api.get(`/events/by-task/${taskId}`);
    return response.data;
  },

  getById: async (id: string): Promise<BackendEvent> => {
    const response = await api.get(`/events/${id}`);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/events/${id}`);
  },
};

// Screenshot API
export const screenshotAPI = {
  create: async (data: {
    event_id: string;
    url: string;
    sha256: string;
  }): Promise<BackendScreenshot> => {
    const response = await api.post('/screenshots/', data);
    return response.data;
  },

  getByEvent: async (eventId: string): Promise<BackendScreenshot[]> => {
    const response = await api.get(`/screenshots/by-event/${eventId}`);
    return response.data;
  },

  getById: async (id: string): Promise<BackendScreenshot> => {
    const response = await api.get(`/screenshots/${id}`);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/screenshots/${id}`);
  },
};

// Media API
export const mediaAPI = {
  upload: async (
    taskId: string,
    uploadedBy: string,
    file: File
  ): Promise<BackendMedia> => {
    const formData = new FormData();
    formData.append('task_id', taskId);
    formData.append('uploaded_by', uploadedBy);
    formData.append('file', file);

    const response = await api.post('/media/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getByTask: async (taskId: string): Promise<BackendMedia[]> => {
    const response = await api.get(`/media/by-task/${taskId}`);
    return response.data;
  },

  getById: async (id: string): Promise<BackendMedia> => {
    const response = await api.get(`/media/${id}`);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/media/${id}`);
  },
};

// Agent API
export const agentAPI = {
  postMessage: async (taskId: string, message: any): Promise<void> => {
    await api.post(`/tasks/${taskId}/message`, message);
  },
};

export default api;