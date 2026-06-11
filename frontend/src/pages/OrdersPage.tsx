import { useCallback, useEffect, useState } from 'react';
import { fetchOrders } from '../services/api';
import { ROUTE_META } from '../config/navigation';
import PageHeader from '../components/PageHeader';
import InfoCard from '../components/InfoCard';
import StatusBadge from '../components/StatusBadge';
import DataTable from '../components/DataTable';
import OrderDetailModal from '../components/OrderDetailModal';

export default function OrdersPage() {
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const meta = ROUTE_META['/orders'];

  const loadOrders = useCallback(() => {
    setLoading(true);
    fetchOrders()
      .then((data) => setOrders(data))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadOrders();
  }, [loadOrders]);

  return (
    <div className="space-y-5 sm:space-y-6">
      <div>
        <h1 className="text-2xl font-bold sm:text-3xl">{meta.title}</h1>
        <PageHeader subtitle={meta.subtitle} count={loading ? undefined : orders.length} />
      </div>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <InfoCard
          title="در انتظار"
          value={orders.filter((o) => o.status === 'در انتظار').length.toString()}
          caption="نیاز به پردازش"
          accent="warning"
        />
        <InfoCard
          title="موفق"
          value={orders.filter((o) => o.status === 'موفق').length.toString()}
          caption="تکمیل شده"
          accent="success"
        />
        <InfoCard title="کل سفارشات" value={orders.length.toString()} caption="ثبت شده" accent="neutral" />
      </section>

      <section className="table-shell">
        <div className="border-b px-4 py-4 sm:px-5" style={{ borderColor: 'var(--border)' }}>
          <h2 className="font-semibold">سفارش‌ها</h2>
          <p className="mt-1 text-xs text-[var(--text-muted)]">برای مشاهده رسید و تأیید/رد، روی هر سفارش کلیک کنید</p>
        </div>
        <div className="p-3 sm:p-4">
          <DataTable
            loading={loading}
            data={orders}
            rowKey={(o) => o.id}
            onRowClick={(o) => setSelectedId(o.id)}
            columns={[
              { key: 'id', header: '#', render: (o) => o.id },
              { key: 'user', header: 'کاربر', render: (o) => <span className="font-medium">{o.user}</span> },
              {
                key: 'type',
                header: 'نوع',
                render: (o) => o.orderType ?? '—',
                hideOnMobile: true,
              },
              { key: 'product', header: 'محصول', render: (o) => o.product },
              { key: 'amount', header: 'مبلغ', render: (o) => o.amount },
              {
                key: 'receipt',
                header: 'رسید',
                render: (o) => (o.hasReceipt ? '✓' : '—'),
                hideOnMobile: true,
              },
              { key: 'date', header: 'تاریخ', render: (o) => o.date },
              {
                key: 'status',
                header: 'وضعیت',
                render: (o) => (
                  <StatusBadge
                    label={o.status}
                    variant={o.status === 'در انتظار' ? 'warning' : o.status === 'موفق' ? 'success' : 'danger'}
                  />
                ),
              },
            ]}
          />
        </div>
      </section>

      <OrderDetailModal orderId={selectedId} onClose={() => setSelectedId(null)} onUpdated={loadOrders} />
    </div>
  );
}
