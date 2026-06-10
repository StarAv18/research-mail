import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { APIResponse } from '../types';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "https://research-mail-2.onrender.com/api/v1";

const AI_PROVIDER_KEY = 'research_mail_ai_provider';
const AI_API_KEY_KEY = 'research_mail_ai_api_key';
const GMAIL_ADDRESS_KEY = 'research_mail_gmail_address';
const GMAIL_APP_PASSWORD_KEY = 'research_mail_gmail_app_password';

const toCamel = (value: string) =>
  value.replace(/_([a-z])/g, (_, letter: string) => letter.toUpperCase());

const toSnake = (value: string) =>
  value.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);

const convertKeys = (value: unknown, keyConverter: (key: string) => string): unknown => {
  if (Array.isArray(value)) {
    return value.map((item) => convertKeys(item, keyConverter));
  }

  if (value && typeof value === 'object' && !(value instanceof Date)) {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [
        keyConverter(key),
        convertKeys(item, keyConverter),
      ])
    );
  }

  return value;
};

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
        const aiProvider = typeof window !== 'undefined' ? localStorage.getItem(AI_PROVIDER_KEY) : null;
        const aiApiKey = typeof window !== 'undefined' ? localStorage.getItem(AI_API_KEY_KEY) : null;
        const gmailAddress = typeof window !== 'undefined' ? localStorage.getItem(GMAIL_ADDRESS_KEY) : null;
        const gmailAppPassword = typeof window !== 'undefined' ? localStorage.getItem(GMAIL_APP_PASSWORD_KEY) : null;
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        if (aiProvider && config.headers) {
          config.headers['X-AI-Provider'] = aiProvider;
        }
        if (aiApiKey && config.headers) {
          config.headers['X-AI-API-Key'] = aiApiKey;
        }
        if (gmailAddress && config.headers) {
          config.headers['X-Gmail-Address'] = gmailAddress;
        }
        if (gmailAppPassword && config.headers) {
          config.headers['X-Gmail-App-Password'] = gmailAppPassword;
        }
        if (config.data && typeof config.data === 'object') {
          config.data = convertKeys(config.data, toSnake);
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for consistent error handling
    ApiClient.instance.interceptors.response.use(
      (response) => convertKeys(response.data, toCamel) as any,
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
export { AI_API_KEY_KEY, AI_PROVIDER_KEY, GMAIL_ADDRESS_KEY, GMAIL_APP_PASSWORD_KEY };
