export interface Professor {
  id: string;
  name: string;
  university: string;
  department?: string;
  email?: string;
  website?: string;
  researchInterests: string[];
  biography?: string;
  fitScore?: number;
  country?: string;
  createdAt: string;
  updatedAt?: string;
}

export interface ProfessorSearchResult {
  name: string;
  university: string;
  department?: string;
  email?: string;
  website?: string;
  researchInterests: string[];
  recentWork: string;
  biography: string;
}

export interface ProfessorSearchResponse {
  query: string;
  count: number;
  professors: ProfessorSearchResult[];
}

export interface ResearchSummary {
  id: string;
  professorId: string;
  summary: string;
  keyAchievements: string[];
  recentPublications: Publication[];
  activeProjects: string[];
  createdAt: string;
}

export interface Publication {
  id: string;
  title: string;
  year?: number;
  url?: string;
}
