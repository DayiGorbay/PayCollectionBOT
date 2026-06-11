/**
 * قرارداد پیشنهادی REST برای بک‌اند — مسیرها نسبت به VITE_API_BASE_URL
 */
export const API_ENDPOINTS = {
  auth: {
    login: '/auth/login',
    logout: '/auth/logout',
    me: '/auth/me',
    changePassword: '/auth/change-password',
  },
  dashboard: {
    summary: '/dashboard/summary',
  },
  users: '/users',
  orders: '/orders',
  products: '/products',
  transactions: '/transactions',
  panels: '/panels',
  discounts: '/discounts',
  settings: '/settings',
} as const;
