import type { AuthUser } from '../types/api';

const TOKEN_KEY = 'pc_access_token';
const USER_KEY = 'pc_user';

type StorageMode = 'session' | 'local';

function getStore(mode: StorageMode): Storage {
  return mode === 'local' ? localStorage : sessionStorage;
}

export function saveAuthSession(token: string, user: AuthUser, remember: boolean) {
  const primary = getStore(remember ? 'local' : 'session');
  const secondary = getStore(remember ? 'session' : 'local');

  secondary.removeItem(TOKEN_KEY);
  secondary.removeItem(USER_KEY);

  primary.setItem(TOKEN_KEY, token);
  primary.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuthSession() {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getAccessToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY) || localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser(): AuthUser | null {
  const raw = sessionStorage.getItem(USER_KEY) || localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken());
}
