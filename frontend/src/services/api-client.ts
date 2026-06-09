import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { APIResponse } from '../types';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_URL && typeof window === 'undefined') {
  console.warn(
    'WARNING: NEXT_PUBLIC_API_URL is not defined. API calls will fail in production. ' +
    'Check your environment variables.'
  );
}

class ApiClient {
  private static instance: AxiosInstance;

  public static getInstance(): AxiosInstance {
    if (!ApiClient.instance) {
      if (!API_URL) {
        throw new Error(
          'API Base URL is not configured. Please set NEXT_PUBLIC_API_URL environment variable.'
        );
      }

      ApiClient.instance = axios.create({
        baseURL: API_URL,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      this.setupInterceptors();
    }
    return ApiClient.instance;
  }

  private static setupInterceptors() {
    // Request interceptor for Auth tokens
    ApiClient.instance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for consistent error handling
    ApiClient.instance.interceptors.response.use(
      (response) => response.data,
      (error: AxiosError<APIResponse<unknown>>) => {
        const apiError = error.response?.data?.error || error.message || 'An unexpected error occurred';
        const statusCode = error.response?.status;

        // Centralized logging for non-404 errors
        if (statusCode !== 404) {
          console.error(`[API Error ${statusCode}]:`, apiError);
        }

        // Handle 401 Unauthorized globally
        if (statusCode === 401 && typeof window !== 'undefined') {
          // localStorage.removeItem('auth_token');
          // window.location.href = '/login';
        }

        return Promise.reject(new Error(apiError));
      }
    );
  }
}

export const apiClient = ApiClient.getInstance();
