import { apiClient } from '@/services/api-client';
import { APIResponse, DocumentDetail, DocumentItem } from '@/types';

export const documentsService = {
  list: async (): Promise<DocumentItem[]> => {
    const response = await apiClient.get<any, APIResponse<DocumentItem[]>>('/documents');
    return response.data;
  },

  upload: async (file: File): Promise<DocumentItem> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<any, APIResponse<DocumentItem>>('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  get: async (id: string): Promise<DocumentDetail> => {
    const response = await apiClient.get<any, APIResponse<DocumentDetail>>(`/documents/${id}`);
    return response.data;
  },

  replace: async (id: string, payload: { file?: File; filename?: string }): Promise<DocumentItem> => {
    const formData = new FormData();
    if (payload.file) {
      formData.append('file', payload.file);
    }
    if (payload.filename) {
      formData.append('filename', payload.filename);
    }
    const response = await apiClient.patch<any, APIResponse<DocumentItem>>(`/documents/${id}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  remove: async (id: string): Promise<boolean> => {
    const response = await apiClient.delete<any, APIResponse<boolean>>(`/documents/${id}`);
    return response.data;
  },
};
