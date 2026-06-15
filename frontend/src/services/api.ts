import apiClient from './apiClient';
import type { DashboardSummary } from '../types/api';
import type { OrderDetail, PanelCreatePayload, Product, ProductCreatePayload } from '../types/api';

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

export async function fetchProducts(): Promise<Product[]> {
  const { data } = await apiClient.get<Product[]>('/products');
  return data;
}

export async function fetchTransactions() {
  const { data } = await apiClient.get('/transactions');
  return data;
}

export async function fetchTransactionStats() {
  const { data } = await apiClient.get('/transactions/stats');
  return data;
}

export async function fetchPanels() {
  const { data } = await apiClient.get('/panels');
  return data;
}

export async function blockUser(userId: number, blocked: boolean) {
  const { data } = await apiClient.patch(`/users/${userId}/block`, { blocked });
  return data;
}

export async function createDiscount(payload: Record<string, unknown>) {
  const { data } = await apiClient.post('/discounts', payload);
  return data;
}

export async function deleteDiscount(id: number) {
  await apiClient.delete(`/discounts/${id}`);
}

export async function updateProduct(id: number, payload: ProductCreatePayload): Promise<Product> {
  const { data } = await apiClient.patch<Product>(`/products/${id}`, payload);
  return data;
}

export async function deleteProduct(id: number) {
  await apiClient.delete(`/products/${id}`);
}

export async function deletePanel(id: number) {
  await apiClient.delete(`/panels/${id}`);
}

export async function previewPanelInbounds(payload: PanelCreatePayload) {
  const { data } = await apiClient.post('/panels/preview-inbounds', mapPanelPayload(payload));
  return data as Array<{ id: string; label: string; protocol?: string; port?: number }>;
}

export async function updateDiscount(id: number, payload: Record<string, unknown>) {
  const { data } = await apiClient.patch(`/discounts/${id}`, payload);
  return data;
}

export async function fetchBotSettings() {
  const { data } = await apiClient.get('/bot-settings');
  return data;
}

export async function saveBotSettings(payload: Record<string, unknown>) {
  await apiClient.put('/bot-settings', payload);
}

export async function fetchFreeConnectConfig() {
  const { data } = await apiClient.get('/free-connect');
  return data;
}

export async function saveFreeConnectConfig(payload: Record<string, unknown>) {
  const { data } = await apiClient.put('/free-connect', payload);
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

export async function approveOrder(orderId: number, blockUser = false): Promise<void> {
  await apiClient.post(`/orders/${orderId}/approve`, { blockUser });
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
