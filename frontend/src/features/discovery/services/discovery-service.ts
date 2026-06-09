import { apiClient } from '@/services/api-client';
import { Professor, APIResponse } from '@/types';

export const discoveryService = {
  scrapeProfessor: async (url: string): Promise<Professor> => {
    const response = await apiClient.get<any, APIResponse<Professor>>('/discovery/scrape', {
      params: { url },
    });
    return response.data;
  },

  // Future: searchProfessors: async (query: SearchParams) => ...
};
