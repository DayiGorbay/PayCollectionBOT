export type ApiErrorBody = {
  message?: string;
  detail?: string | Record<string, string[]>;
  code?: string;
};

export type DashboardSummary = {
  totalUsers: number;
  activeUsers: number;
  todayUsers: number;
  totalRevenue: number;
  pendingOrders: number;
  activePanels: number;
  activeCoupons: Array<{ id: number; code: string; type: string; amount: number; validUntil: string }>;
  recentOrders: Array<{ id: number; user: string; product: string; amount: string; status: string; date: string }>;
};

export type AuthUser = {
  id: number;
  username: string;
  displayName: string;
  role: 'admin' | 'operator';
};

export type LoginPayload = {
  username: string;
  password: string;
  remember?: boolean;
};

export type LoginResponse = {
  accessToken: string;
  refreshToken?: string;
  expiresIn?: number;
  user: AuthUser;
};

export type PaginatedResponse<T> = {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
};

export type OrderDetail = {
  id: number;
  user: string;
  telegramUserId: number;
  product: string;
  amount: string;
  amountRial: number;
  method: string;
  date: string;
  status: string;
  orderType: string;
  hasReceipt: boolean;
  receiptUrl?: string | null;
  adminNote?: string | null;
  discountCode?: string | null;
  walletPaidRial?: number;
};

export type PanelStats = {
  panelId: number;
  ok: boolean;
  error?: string | null;
  panelType: string;
  version?: string | null;
  cpuPercent?: number | null;
  memUsedBytes?: number | null;
  memTotalBytes?: number | null;
  memPercent?: number | null;
  xrayState?: string | null;
  totalUsers?: number | null;
  onlineUsers?: number | null;
  expiredUsers?: number | null;
  volumeExhaustedUsers?: number | null;
  tcpCount?: number | null;
  netUpBytes?: number | null;
  netDownBytes?: number | null;
  fetchedAt: string;
};

export type PanelCreatePayload = {
  name: string;
  codePanel: string;
  apiUrl: string;
  panelType: 'marzban' | 'xui';
  usernamePanel: string;
  passwordPanel: string;
  status?: string;
  authMode?: 'bearer' | 'session';
  apiToken?: string;
  inbounds?: string;
  proxies?: string;
  inboundId?: number;
};

export type Product = {
  id: number;
  name: string;
  price: string;
  durationDays: number;
  duration: string;
  panel?: string;
  panelId?: number | null;
  code: string;
  category?: string | null;
  isActive?: boolean;
};

export type ProductCreatePayload = {
  name: string;
  price: number;
  durationDays: number;
  panelId: number;
  code: string;
  category?: string;
};

export type ServiceListItem = {
  id: number;
  user: string;
  telegramUserId: number;
  product?: string | null;
  panel?: string | null;
  marzbanUsername: string;
  status: string;
  expireAt?: string | null;
  remainingTrafficBytes?: number | null;
  usedTrafficBytes?: number;
  dataLimitBytes?: number | null;
  onlineStatus?: string | null;
  lastOnlineAt?: string | null;
  createdAt: string;
  lastSyncedAt?: string | null;
};

export type ServiceDetail = ServiceListItem & {
  orderId?: number | null;
  productId?: number | null;
  panelId?: number | null;
  panelType: string;
  subscriptionUrl?: string | null;
  configText?: string | null;
  dataGb: number;
  daysRemaining?: number | null;
  panelUserStatus?: string | null;
  inbounds?: Record<string, unknown> | unknown[] | null;
  links: string[];
  liveFromPanel: boolean;
  panelRaw?: Record<string, unknown> | null;
};
