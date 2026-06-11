import { useEffect, useState } from 'react';
import { fetchUsers } from '../services/api';
import { ROUTE_META } from '../config/navigation';
import PageHeader from '../components/PageHeader';
import InfoCard from '../components/InfoCard';
import StatusBadge from '../components/StatusBadge';
import DataTable from '../components/DataTable';

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const meta = ROUTE_META['/users'];

  useEffect(() => {
    fetchUsers().then((data) => {
      setUsers(data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-5 sm:space-y-6">
      <div>
        <h1 className="text-2xl font-bold sm:text-3xl">{meta.title}</h1>
        <PageHeader subtitle={meta.subtitle} count={loading ? undefined : users.length} />
      </div>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <InfoCard title="کل کاربران" value={users.length.toString()} caption="تمام کاربران ثبت شده" accent="accent" />
        <InfoCard
          title="کاربران فعال"
          value={users.filter((item) => item.status === 'فعال').length.toString()}
          caption="کاربران دارای پلن فعال"
          accent="success"
        />
        <InfoCard
          title="پلن‌های فعال"
          value={new Set(users.map((item) => item.plan)).size.toString()}
          caption="تنوع سرویس‌ها"
          accent="neutral"
        />
      </section>

      <section className="table-shell">
        <div className="border-b px-4 py-4 sm:px-5" style={{ borderColor: 'var(--border)' }}>
          <h2 className="font-semibold">لیست کاربران</h2>
        </div>
        <div className="p-3 sm:p-4">
          <DataTable
            loading={loading}
            data={users}
            rowKey={(u) => u.id}
            emptyTitle="کاربری یافت نشد"
            columns={[
              { key: 'id', header: '#', render: (u) => u.id },
              { key: 'name', header: 'نام', render: (u) => <span className="font-medium">{u.name}</span> },
              { key: 'plan', header: 'پلن', render: (u) => u.plan },
              { key: 'volume', header: 'حجم', render: (u) => u.volume, hideOnMobile: true },
              { key: 'expiry', header: 'انقضا', render: (u) => u.expiry },
              {
                key: 'status',
                header: 'وضعیت',
                render: (u) => (
                  <StatusBadge
                    label={u.status}
                    variant={u.status === 'فعال' ? 'success' : u.status === 'منقضی' ? 'danger' : 'warning'}
                  />
                ),
              },
            ]}
          />
        </div>
      </section>
    </div>
  );
}
