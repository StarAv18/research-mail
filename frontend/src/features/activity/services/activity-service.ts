import { apiClient } from '@/services/api-client';
import { ActivityLogItem, APIResponse, DashboardAnalytics } from '@/types';

export const activityService = {
  list: async (): Promise<ActivityLogItem[]> => {
    const response = await apiClient.get<any, APIResponse<ActivityLogItem[]>>('/activity');
    return response.data;
  },

  analytics: async (): Promise<DashboardAnalytics> => {
    const response = await apiClient.get<any, APIResponse<DashboardAnalytics>>('/system/analytics');
    return response.data;
  },
};
