import { useEffect, useState } from 'react';
import { fetchUsers, blockUser } from '../services/api';
import { ROUTE_META } from '../config/navigation';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import DataTable from '../components/DataTable';
import { useAppContext } from '../context/AppContext';
import { getApiErrorMessage } from '../services/apiClient';

export default function UsersPage() {
  const { addToast } = useAppContext();
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const meta = ROUTE_META['/users'];

  const load = () => {
    setLoading(true);
    fetchUsers()
      .then((data) => setUsers(data))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const toggleBlock = async (user: any) => {
    try {
      await blockUser(user.id, !user.isBlocked);
      addToast({
        title: user.isBlocked ? 'رفع مسدودیت' : 'مسدود شد',
        description: user.name,
        variant: 'success',
      });
      load();
    } catch (error) {
      addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' });
    }
  };

  return (
    <div className="space-y-5 sm:space-y-6">
      <div>
        <h1 className="text-2xl font-bold sm:text-3xl">{meta.title}</h1>
        <PageHeader subtitle={meta.subtitle} count={loading ? undefined : users.length} />
      </div>

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
              { key: 'username', header: 'یوزرنیم', render: (u) => u.username },
              { key: 'phone', header: 'موبایل', render: (u) => u.phone, hideOnMobile: true },
              { key: 'history', header: 'تاریخچه خرید', render: (u) => u.purchaseHistory, hideOnMobile: true },
              { key: 'total', header: 'جمع خرید', render: (u) => u.totalSpent },
              { key: 'registered', header: 'ثبت‌نام', render: (u) => u.registeredAt },
              {
                key: 'status',
                header: 'وضعیت',
                render: (u) => (
                  <StatusBadge
                    label={u.status}
                    variant={
                      u.status === 'احراز شده' ? 'success' : u.status === 'مسدود' ? 'danger' : 'warning'
                    }
                  />
                ),
              },
              {
                key: 'actions',
                header: 'عملیات',
                render: (u) => (
                  <button type="button" className="btn-ghost py-1 text-xs" onClick={() => toggleBlock(u)}>
                    {u.isBlocked ? 'رفع مسدودیت' : 'مسدود کردن'}
                  </button>
                ),
              },
            ]}
          />
        </div>
      </section>
    </div>
  );
}
