import { useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import StatsCard from '../components/StatsCard';
import DataTable from '../components/DataTable';
import { fetchTransactions } from '../services/api';
import { ROUTE_META } from '../config/navigation';
import PageHeader from '../components/PageHeader';

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const meta = ROUTE_META['/transactions'];

  useEffect(() => {
    fetchTransactions().then((result) => {
      setTransactions(result);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-5 sm:space-y-6">
      <div>
        <h1 className="text-2xl font-bold sm:text-3xl">{meta.title}</h1>
        <PageHeader subtitle={meta.subtitle} count={loading ? undefined : transactions.length} />
      </div>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <StatsCard value="5,059,980 تومان" label="جمع تراکنش‌های موفق" accent="green" />
        <StatsCard value="468" label="تعداد کل" accent="neutral" />
        <StatsCard value="468" label="تراکنش جدید امروز" accent="yellow" />
      </section>

      <section className="table-shell">
        <div className="flex flex-col gap-4 border-b p-4 sm:flex-row sm:items-center sm:justify-between sm:px-5" style={{ borderColor: 'var(--border)' }}>
          <h2 className="font-semibold">گزارش تراکنش‌ها ({transactions.length})</h2>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            <div className="relative">
              <input
                type="search"
                placeholder="آیدی کاربر یا شماره تراکنش..."
                className="input-field w-full py-2.5 pl-10 pr-4 sm:w-64"
              />
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-muted)]" />
            </div>
            <select className="input-field py-2.5 sm:w-40">
              <option>همه وضعیت‌ها</option>
            </select>
            <button type="button" className="btn-primary py-2.5">
              جستجو
            </button>
          </div>
        </div>
        <div className="p-3 sm:p-4">
          <DataTable
            loading={loading}
            data={transactions}
            rowKey={(t) => t.id}
            columns={[
              { key: 'id', header: '#', render: (t) => t.id },
              { key: 'user', header: 'کاربر', render: (t) => t.user },
              { key: 'hash', header: 'شناسه', render: (t) => <span className="font-mono text-xs">{t.hash}</span> },
              { key: 'method', header: 'روش', render: (t) => t.method, hideOnMobile: true },
              { key: 'amount', header: 'مبلغ', render: (t) => t.amount },
              { key: 'date', header: 'تاریخ', render: (t) => t.date },
              {
                key: 'status',
                header: 'وضعیت',
                render: (t) => (
                  <span
                    className={
                      t.status === 'پرداخت نشده'
                        ? 'text-rose-400'
                        : t.status === 'در انتظار'
                          ? 'text-amber-400'
                          : 'text-[var(--text-muted)]'
                    }
                  >
                    {t.status}
                  </span>
                ),
              },
            ]}
          />
        </div>
      </section>
    </div>
  );
}
