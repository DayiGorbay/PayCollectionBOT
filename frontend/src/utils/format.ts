export function formatBytes(bytes?: number | null): string {
  if (bytes == null || bytes < 0) return '—';
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** i;
  return `${value.toFixed(value >= 10 || i === 0 ? 0 : 1)} ${units[i]}`;
}

export function formatDateTime(value?: string | null): string {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('fa-IR');
}

export function serviceStatusVariant(status: string): 'success' | 'warning' | 'danger' | 'info' {
  if (status === 'active' || status === 'موفق') return 'success';
  if (status === 'deleted' || status === 'رد شده') return 'danger';
  if (status === 'در انتظار') return 'warning';
  return 'info';
}
