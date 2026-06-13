export * from './professor';
export * from './outreach';
export * from './document';
export * from './campaign';
export * from './activity';

export interface StudentProfile {
  id: string;
  fullName: string;
  email: string;
  university: string;
  major: string;
  gpa?: number;
  skills: string[];
  experience: string;
  interests: string[];
  resumeUrl?: string;
  createdAt: string;
}

export interface APIResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
