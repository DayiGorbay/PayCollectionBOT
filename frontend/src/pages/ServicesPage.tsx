import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { RefreshCw } from 'lucide-react';
import { fetchServices } from '../services/api';
import { ROUTE_META } from '../config/navigation';
import PageHeader from '../components/PageHeader';
import DataTable from '../components/DataTable';
import StatusBadge from '../components/StatusBadge';
import { formatBytes, formatDateTime, serviceStatusVariant } from '../utils/format';

export default function ServicesPage() {
  const [services, setServices] = useState<Awaited<ReturnType<typeof fetchServices>>>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const meta = ROUTE_META['/services'];

  const load = useCallback(() => {
    setLoading(true);
    fetchServices()
      .then(setServices)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="space-y-5 sm:space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold sm:text-3xl">{meta.title}</h1>
          <PageHeader subtitle={meta.subtitle} count={loading ? undefined : services.length} />
        </div>
        <button type="button" className="btn-ghost inline-flex items-center gap-2" onClick={load}>
          <RefreshCw className="h-4 w-4" />
          بروزرسانی لیست
        </button>
      </div>

      <section className="table-shell">
        <div className="border-b px-4 py-4 sm:px-5" style={{ borderColor: 'var(--border)' }}>
          <h2 className="font-semibold">سرویس‌های کاربران</h2>
          <p className="mt-1 text-xs text-[var(--text-muted)]">برای جزئیات لحظه‌ای از پنل، روی هر سطر کلیک کنید</p>
        </div>
        <div className="p-3 sm:p-4">
          <DataTable
            loading={loading}
            data={services}
            rowKey={(s) => s.id}
            onRowClick={(s) => navigate(`/services/${s.id}`)}
            columns={[
              { key: 'id', header: 'ID', render: (s) => s.id },
              { key: 'user', header: 'کاربر', render: (s) => <span className="font-medium">{s.user}</span> },
              { key: 'telegram', header: 'تلگرام', render: (s) => s.telegramUserId, hideOnMobile: true },
              { key: 'product', header: 'محصول', render: (s) => s.product ?? '—' },
              { key: 'panel', header: 'پنل', render: (s) => s.panel ?? '—', hideOnMobile: true },
              {
                key: 'username',
                header: 'نام کاربری',
                render: (s) => <span className="font-mono text-xs">{s.marzbanUsername}</span>,
              },
              {
                key: 'status',
                header: 'وضعیت',
                render: (s) => <StatusBadge label={s.status} variant={serviceStatusVariant(s.status)} />,
              },
              { key: 'expire', header: 'انقضا', render: (s) => formatDateTime(s.expireAt), hideOnMobile: true },
              { key: 'remaining', header: 'حجم باقی', render: (s) => formatBytes(s.remainingTrafficBytes), hideOnMobile: true },
              { key: 'used', header: 'مصرف', render: (s) => formatBytes(s.usedTrafficBytes), hideOnMobile: true },
              { key: 'online', header: 'آنلاین', render: (s) => s.onlineStatus ?? '—', hideOnMobile: true },
              { key: 'created', header: 'ایجاد', render: (s) => formatDateTime(s.createdAt), hideOnMobile: true },
            ]}
          />
        </div>
      </section>
    </div>
  );
}
