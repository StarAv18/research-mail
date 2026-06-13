import { apiClient } from '@/services/api-client';
import { APIResponse, Campaign, CampaignDetail, CampaignExecutionResult, CampaignLog } from '@/types';

export const campaignsService = {
  list: async (): Promise<Campaign[]> => {
    const response = await apiClient.get<any, APIResponse<Campaign[]>>('/campaigns');
    return response.data;
  },

  create: async (payload: { name: string; draftIds: string[] }): Promise<Campaign> => {
    const response = await apiClient.post<any, APIResponse<Campaign>>('/campaigns', payload);
    return response.data;
  },

  get: async (id: string): Promise<CampaignDetail> => {
    const response = await apiClient.get<any, APIResponse<CampaignDetail>>(`/campaigns/${id}`);
    return response.data;
  },

  execute: async (id: string): Promise<CampaignExecutionResult> => {
    const response = await apiClient.post<any, APIResponse<CampaignExecutionResult>>(`/campaigns/${id}/execute`);
    return response.data;
  },

  logs: async (id: string): Promise<CampaignLog[]> => {
    const response = await apiClient.get<any, APIResponse<CampaignLog[]>>(`/campaigns/${id}/logs`);
    return response.data;
  },
};
