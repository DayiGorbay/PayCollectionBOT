import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { env } from '../config/env';
import type { ApiErrorBody } from '../types/api';
import { clearAuthSession, getAccessToken } from './authStorage';

export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  withCredentials: false,
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  config.headers['X-Requested-With'] = 'XMLHttpRequest';
  return config;
});

let onUnauthorized: (() => void) | null = null;

export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler;
}

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorBody>) => {
    if (error.response?.status === 401) {
      clearAuthSession();
      onUnauthorized?.();
    }
    return Promise.reject(error);
  },
);

export function getApiErrorMessage(error: unknown, fallback = 'خطایی رخ داد. دوباره تلاش کنید.') {
  if (!axios.isAxiosError<ApiErrorBody>(error)) {
    return error instanceof Error ? error.message : fallback;
  }

  const data = error.response?.data;
  if (typeof data?.message === 'string' && data.message.trim()) {
    return data.message;
  }
  if (typeof data?.detail === 'string' && data.detail.trim()) {
    return data.detail;
  }
  if (error.response?.status === 401) {
    return 'نام کاربری یا رمز عبور نادرست است.';
  }
  if (error.response?.status === 403) {
    return 'دسترسی به این بخش مجاز نیست.';
  }
  if (error.response?.status === 429) {
    return 'تعداد درخواست‌ها زیاد است. لطفاً کمی صبر کنید.';
  }
  if (!error.response) {
    return 'اتصال به سرور برقرار نشد.';
  }
  return fallback;
}

export default apiClient;
