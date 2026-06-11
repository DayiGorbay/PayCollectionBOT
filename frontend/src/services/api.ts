import apiClient from './apiClient';
import type { DashboardSummary } from '../types/api';
import type { OrderDetail, PanelCreatePayload, ProductCreatePayload } from '../types/api';

export type { OrderDetail } from '../types/api';

export async function fetchDashboard(): Promise<DashboardSummary> {
  const { data } = await apiClient.get<DashboardSummary>('/dashboard/summary');
  return data;
}

export async function fetchUsers() {
  const { data } = await apiClient.get('/users');
  return data;
}

export async function fetchOrders() {
  const { data } = await apiClient.get('/orders');
  return data;
}

export async function fetchProducts() {
  const { data } = await apiClient.get('/products');
  return data;
}

export async function fetchTransactions() {
  const { data } = await apiClient.get('/transactions');
  return data;
}

export async function fetchPanels() {
  const { data } = await apiClient.get('/panels');
  return data;
}

export async function fetchDiscounts() {
  const { data } = await apiClient.get('/discounts');
  return data;
}

export async function fetchSettings() {
  const { data } = await apiClient.get('/settings');
  return data;
}

export async function fetchOrderDetail(orderId: number): Promise<OrderDetail> {
  const { data } = await apiClient.get<OrderDetail>(`/orders/${orderId}`);
  return data;
}

export async function fetchOrderReceiptBlob(orderId: number): Promise<string> {
  const { data } = await apiClient.get<Blob>(`/orders/${orderId}/receipt`, { responseType: 'blob' });
  return URL.createObjectURL(data);
}

export async function approveOrder(orderId: number): Promise<void> {
  await apiClient.post(`/orders/${orderId}/approve`);
}

export async function rejectOrder(orderId: number): Promise<void> {
  await apiClient.post(`/orders/${orderId}/reject`);
}

function mapPanelPayload(payload: PanelCreatePayload) {
  return {
    name: payload.name,
    code_panel: payload.codePanel,
    api_url: payload.apiUrl,
    panel_type: payload.panelType,
    username_panel: payload.usernamePanel,
    password_panel: payload.passwordPanel,
    status: payload.status ?? 'فعال',
    auth_mode: payload.authMode ?? 'bearer',
    api_token: payload.apiToken,
    inbounds: payload.inbounds,
    proxies: payload.proxies,
    inbound_id: payload.inboundId,
  };
}

export async function fetchPanelsList() {
  const { data } = await apiClient.get('/panels');
  return data;
}

export async function createPanel(payload: PanelCreatePayload) {
  const { data } = await apiClient.post('/panels', mapPanelPayload(payload));
  return data;
}

export async function testPanelConnection(payload: PanelCreatePayload) {
  const { data } = await apiClient.post<{ ok: boolean; message: string }>('/panels/test', mapPanelPayload(payload));
  return data;
}

export async function testPanelById(panelId: number) {
  const { data } = await apiClient.post<{ ok: boolean; message: string }>(`/panels/${panelId}/test`);
  return data;
}

export async function fetchPanelsStats() {
  const { data } = await apiClient.get('/panels/stats');
  return data;
}

export async function createProduct(payload: ProductCreatePayload) {
  const { data } = await apiClient.post('/products', {
    name: payload.name,
    price: payload.price,
    duration_days: payload.durationDays,
    panel_id: payload.panelId,
    code: payload.code,
    category: payload.category,
  });
  return data;
}

export { apiClient };
