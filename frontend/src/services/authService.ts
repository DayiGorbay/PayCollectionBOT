import type { LoginPayload, LoginResponse } from '../types/api';
import apiClient, { getApiErrorMessage } from './apiClient';
import { saveAuthSession } from './authStorage';

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  try {
    const { data } = await apiClient.post<LoginResponse>('/auth/login', {
      username: payload.username.trim(),
      password: payload.password,
    });
    saveAuthSession(data.accessToken, data.user, Boolean(payload.remember));
    return data;
  } catch (error) {
    throw new Error(getApiErrorMessage(error, 'ورود ناموفق بود.'));
  }
}

export async function logout(): Promise<void> {
  try {
    await apiClient.post('/auth/logout');
  } catch {
    // ignore network errors on logout
  }
}

export async function fetchCurrentUser() {
  const { data } = await apiClient.get('/auth/me');
  return data;
}
