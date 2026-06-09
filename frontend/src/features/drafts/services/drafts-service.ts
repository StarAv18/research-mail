import { apiClient } from '@/services/api-client';
import { Draft, APIResponse } from '@/types';

export const draftsService = {
  listDrafts: async (query?: string): Promise<Draft[]> => {
    const response = await apiClient.get<any, APIResponse<Draft[]>>('/drafts', {
      params: { query },
    });
    return response.data;
  },

  getDraft: async (id: string): Promise<Draft> => {
    const response = await apiClient.get<any, APIResponse<Draft>>(`/drafts/${id}`);
    return response.data;
  },

  updateDraft: async (id: string, draft: Partial<Draft>): Promise<Draft> => {
    const response = await apiClient.put<any, APIResponse<Draft>>(`/drafts/${id}`, draft);
    return response.data;
  },

  deleteDraft: async (id: string): Promise<boolean> => {
    const response = await apiClient.delete<any, APIResponse<boolean>>(`/drafts/${id}`);
    return response.data;
  },
};
