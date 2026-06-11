import { useEffect, useState } from 'react';
import { ClipboardList, ShieldCheck, Ticket } from 'lucide-react';
import InfoCard from '../components/InfoCard';
import { fetchDashboard } from '../services/api';
import type { DashboardSummary } from '../types/api';
import { ROUTE_META } from '../config/navigation';
import StatusBadge from '../components/StatusBadge';

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const meta = ROUTE_META['/dashboard'];

  useEffect(() => {
    fetchDashboard().then((data) => setSummary(data));
  }, []);

  return (
    <div className="space-y-5 sm:space-y-6">
      <div>
        <h1 className="text-2xl font-bold sm:text-3xl">{meta.title}</h1>
        {meta.subtitle ? <p className="mt-2 text-sm text-[var(--text-muted)]">{meta.subtitle}</p> : null}
      </div>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <InfoCard title="کاربران فعال" value={summary?.activeUsers.toLocaleString('fa-IR') ?? '...'} caption="کاربران فعال" accent="accent" />
        <InfoCard title="کل کاربران" value={summary?.totalUsers.toLocaleString('fa-IR') ?? '...'} caption="ثبت شده" accent="neutral" />
        <InfoCard
          title="درآمد مجموع"
          value={summary ? `${summary.totalRevenue.toLocaleString('fa-IR')} تومان` : '...'}
          caption="تراکنش‌های موفق"
          accent="success"
        />
        <InfoCard title="سفارش در انتظار" value={summary?.pendingOrders.toString() ?? '...'} caption="نیاز به انجام" accent="warning" />
      </section>

      <section className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
        <div className="surface-card p-5 sm:p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-semibold">وضعیت کاربری</h2>
            <ShieldCheck className="h-5 w-5 text-[var(--text-muted)]" />
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-xl p-4" style={{ background: 'var(--bg-muted)' }}>
              <p className="text-sm text-[var(--text-muted)]">کاربران امروز</p>
              <p className="mt-1 text-xl font-semibold">{summary?.todayUsers.toLocaleString('fa-IR') ?? '...'}</p>
            </div>
            <div className="rounded-xl p-4" style={{ background: 'var(--bg-muted)' }}>
              <p className="text-sm text-[var(--text-muted)]">پنل‌های فعال</p>
              <p className="mt-1 text-xl font-semibold">{summary?.activePanels.toLocaleString('fa-IR') ?? '...'}</p>
            </div>
          </div>
        </div>

        <div className="surface-card p-5 sm:p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-semibold">سفارش‌های اخیر</h2>
            <ClipboardList className="h-5 w-5 text-[var(--text-muted)]" />
          </div>
          <div className="space-y-3">
            {summary?.recentOrders.slice(0, 4).map((order) => (
              <div key={order.id} className="rounded-xl border p-3 sm:p-4" style={{ borderColor: 'var(--border)', background: 'var(--bg-muted)' }}>
                <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
                  <span className="font-medium">{order.product}</span>
                  <StatusBadge
                    label={order.status}
                    variant={order.status === 'در انتظار' ? 'warning' : order.status === 'موفق' ? 'success' : 'info'}
                  />
                </div>
                <p className="mt-2 text-xs text-[var(--text-muted)] sm:text-sm">
                  {order.user} • {order.amount} • {order.date}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="surface-card p-5 sm:p-6 lg:col-span-2 xl:col-span-1">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-semibold">کدهای فعال</h2>
            <Ticket className="h-5 w-5 text-[var(--text-muted)]" />
          </div>
          <div className="space-y-3">
            {summary?.activeCoupons.slice(0, 3).map((coupon) => (
              <div key={coupon.id} className="rounded-xl border p-3 sm:p-4" style={{ borderColor: 'var(--border)', background: 'var(--bg-muted)' }}>
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-semibold">{coupon.code}</span>
                  <StatusBadge label={`${coupon.amount}%`} variant="info" />
                </div>
                <p className="mt-2 text-xs text-[var(--text-muted)]">تا {coupon.validUntil}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
