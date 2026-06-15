import { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowRight, RefreshCw } from 'lucide-react';
import { fetchService, refreshService, syncService } from '../services/api';
import type { ServiceDetail } from '../types/api';
import StatusBadge from '../components/StatusBadge';
import { formatBytes, formatDateTime, serviceStatusVariant } from '../utils/format';
import { useAppContext } from '../context/AppContext';
import { getApiErrorMessage } from '../services/apiClient';

export default function ServiceDetailPage() {
  const { id } = useParams();
  const serviceId = Number(id);
  const { addToast } = useAppContext();
  const [service, setService] = useState<ServiceDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(() => {
    if (!serviceId) return;
    setLoading(true);
    fetchService(serviceId)
      .then(setService)
      .catch((error) => addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' }))
      .finally(() => setLoading(false));
  }, [serviceId, addToast]);

  useEffect(() => {
    load();
  }, [load]);

  const handleRefresh = async () => {
    if (!serviceId) return;
    setRefreshing(true);
    try {
      const data = await refreshService(serviceId);
      setService(data);
      addToast({ title: 'بروزرسانی شد', description: 'اطلاعات لحظه‌ای از پنل دریافت شد.', variant: 'success' });
    } catch (error) {
      addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' });
    } finally {
      setRefreshing(false);
    }
  };

  const handleSync = async () => {
    if (!serviceId) return;
    try {
      await syncService(serviceId);
      await load();
      addToast({ title: 'همگام‌سازی', description: 'کش سرویس بروزرسانی شد.', variant: 'info' });
    } catch (error) {
      addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' });
    }
  };

  if (loading) {
    return <p className="text-[var(--text-muted)]">در حال بارگذاری...</p>;
  }

  if (!service) {
    return <p className="text-rose-300">سرویس یافت نشد.</p>;
  }

  const rows: Array<{ label: string; value: string }> = [
    { label: 'شناسه سرویس', value: String(service.id) },
    { label: 'کاربر', value: service.user },
    { label: 'تلگرام ID', value: String(service.telegramUserId) },
    { label: 'محصول', value: service.product ?? '—' },
    { label: 'پنل', value: service.panel ?? '—' },
    { label: 'نوع پنل', value: service.panelType },
    { label: 'نام کاربری Marzban', value: service.marzbanUsername },
    { label: 'وضعیت سرویس', value: service.status },
    { label: 'وضعیت کاربر پنل', value: service.panelUserStatus ?? '—' },
    { label: 'حجم کل', value: formatBytes(service.dataLimitBytes) },
    { label: 'مصرف شده', value: formatBytes(service.usedTrafficBytes) },
    { label: 'باقی‌مانده', value: formatBytes(service.remainingTrafficBytes) },
    { label: 'تاریخ انقضا', value: formatDateTime(service.expireAt) },
    { label: 'روزهای باقی‌مانده', value: service.daysRemaining != null ? `${service.daysRemaining} روز` : '—' },
    { label: 'وضعیت آنلاین', value: service.onlineStatus ?? '—' },
    { label: 'آخرین اتصال', value: formatDateTime(service.lastOnlineAt) },
    { label: 'لینک اشتراک', value: service.subscriptionUrl ?? '—' },
    { label: 'ایجاد شده', value: formatDateTime(service.createdAt) },
    { label: 'آخرین همگام‌سازی', value: formatDateTime(service.lastSyncedAt) },
    { label: 'داده زنده از پنل', value: service.liveFromPanel ? 'بله' : 'خیر' },
  ];

  return (
    <div className="space-y-5 sm:space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <Link to="/services" className="mb-3 inline-flex items-center gap-1 text-sm text-[var(--text-muted)] hover:text-white">
            <ArrowRight className="h-4 w-4" />
            بازگشت به سرویس‌ها
          </Link>
          <h1 className="text-2xl font-bold sm:text-3xl">سرویس #{service.id}</h1>
          <p className="mt-2 text-sm text-[var(--text-muted)]">
            <StatusBadge label={service.status} variant={serviceStatusVariant(service.status)} /> — {service.marzbanUsername}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button type="button" className="btn-ghost" onClick={handleSync}>
            همگام‌سازی کش
          </button>
          <button type="button" className="btn-primary inline-flex items-center gap-2" onClick={handleRefresh} disabled={refreshing}>
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            دریافت از پنل
          </button>
        </div>
      </div>

      <section className="table-shell p-4 sm:p-6">
        <dl className="grid gap-4 sm:grid-cols-2">
          {rows.map((row) => (
            <div key={row.label} className="rounded-xl border p-4" style={{ borderColor: 'var(--border)' }}>
              <dt className="text-xs text-[var(--text-muted)]">{row.label}</dt>
              <dd className="mt-1 break-all text-sm font-medium">{row.value}</dd>
            </div>
          ))}
        </dl>
      </section>

      {service.links.length > 0 ? (
        <section className="table-shell p-4 sm:p-6">
          <h2 className="mb-3 font-semibold">لینک‌ها</h2>
          <ul className="space-y-2">
            {service.links.map((link) => (
              <li key={link} className="rounded-lg border p-3 font-mono text-xs break-all" style={{ borderColor: 'var(--border)' }}>
                {link}
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {service.inbounds ? (
        <section className="table-shell p-4 sm:p-6">
          <h2 className="mb-3 font-semibold">Inbounds</h2>
          <pre className="overflow-x-auto rounded-lg border p-3 text-xs" style={{ borderColor: 'var(--border)' }}>
            {JSON.stringify(service.inbounds, null, 2)}
          </pre>
        </section>
      ) : null}
    </div>
  );
}
