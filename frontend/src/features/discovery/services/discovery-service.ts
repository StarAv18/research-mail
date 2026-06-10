import { apiClient } from '@/services/api-client';
import { Professor, ProfessorSearchResponse, APIResponse } from '@/types';

export interface ProfessorSearchParams {
  researchArea?: string;
  institution?: string;
  country?: string;
  region?: string;
  limit?: number;
}

export const discoveryService = {
  scrapeProfessor: async (url: string): Promise<Professor> => {
    const response = await apiClient.get<any, APIResponse<Professor>>('/discovery/scrape', {
      params: { url },
    });
    return response.data;
  },

  searchProfessors: async (params: ProfessorSearchParams): Promise<ProfessorSearchResponse> => {
    const response = await apiClient.get<any, APIResponse<ProfessorSearchResponse>>('/discovery/search', {
      params: {
        research_area: params.researchArea,
        institution: params.institution,
        country: params.country,
        region: params.region,
        limit: params.limit,
      },
    });
    return response.data;
  },
};
