import { useEffect, useState } from 'react';
import { fetchDiscounts } from '../services/api';
import { ROUTE_META } from '../config/navigation';
import { DISCOUNT_FORM_FIELDS } from '../config/formFields';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import DataTable from '../components/DataTable';
import FormModal from '../components/FormModal';
import { useAppContext } from '../context/AppContext';

export default function DiscountsPage() {
  const { addToast } = useAppContext();
  const [discounts, setDiscounts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const meta = ROUTE_META['/discounts'];

  useEffect(() => {
    fetchDiscounts().then((data) => {
      setDiscounts(data);
      setLoading(false);
    });
  }, []);

  const handleCreate = (values: Record<string, string>) => {
    const amountLabel = values.type === 'درصدی' ? `${values.amount}%` : `${values.amount} ت`;
    const newDiscount = {
      id: Date.now(),
      code: values.code.toUpperCase(),
      amount: amountLabel,
      type: values.type,
      used: `0/${values.maxUse || '∞'}`,
      validUntil: values.validUntil,
      status: 'فعال',
    };
    setDiscounts((prev) => [newDiscount, ...prev]);
    addToast({ title: 'کد تخفیف', description: values.code, variant: 'success' });
  };

  return (
    <div className="space-y-5 sm:space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold sm:text-3xl">{meta.title}</h1>
          <PageHeader subtitle={meta.subtitle} count={loading ? undefined : discounts.length} />
        </div>
        <button type="button" className="btn-primary shrink-0" onClick={() => setModalOpen(true)}>
          + کد جدید
        </button>
      </div>

      <section className="table-shell">
        <div className="border-b px-4 py-4 sm:px-5" style={{ borderColor: 'var(--border)' }}>
          <h2 className="font-semibold">لیست کدهای تخفیف</h2>
        </div>
        <div className="p-3 sm:p-4">
          <DataTable
            loading={loading}
            data={discounts}
            rowKey={(d) => d.id}
            columns={[
              { key: 'id', header: '#', render: (d) => d.id },
              { key: 'code', header: 'کد', render: (d) => <span className="font-medium">{d.code}</span> },
              { key: 'amount', header: 'مبلغ', render: (d) => d.amount },
              { key: 'type', header: 'نوع', render: (d) => d.type },
              { key: 'used', header: 'استفاده', render: (d) => d.used, hideOnMobile: true },
              { key: 'valid', header: 'اعتبار', render: (d) => d.validUntil },
              {
                key: 'status',
                header: 'وضعیت',
                render: (d) => (
                  <StatusBadge label={d.status} variant={d.status === 'فعال' ? 'success' : 'danger'} />
                ),
              },
            ]}
          />
        </div>
      </section>

      <FormModal
        open={modalOpen}
        title="کد تخفیف جدید"
        description="تعریف کد تخفیف برای کاربران ربات"
        fields={DISCOUNT_FORM_FIELDS}
        submitLabel="ایجاد کد"
        onClose={() => setModalOpen(false)}
        onSubmit={handleCreate}
      />
    </div>
  );
}
