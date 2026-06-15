import { useEffect, useState } from 'react';
import { createDiscount, deleteDiscount, fetchDiscounts, updateDiscount } from '../services/api';
import { getApiErrorMessage } from '../services/apiClient';
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

  const load = () => {
    setLoading(true);
    fetchDiscounts()
      .then((data) => setDiscounts(data))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (values: Record<string, string>) => {
    try {
      await createDiscount({
        code: values.code.toUpperCase(),
        amount: values.amount,
        type: values.type,
        maxUses: values.maxUse ? Number(values.maxUse) : 0,
        validUntil: values.validUntil || '—',
        status: 'فعال',
      });
      addToast({ title: 'کد تخفیف', description: values.code, variant: 'success' });
      setModalOpen(false);
      load();
    } catch (error) {
      addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' });
    }
  };

  const handleToggleStatus = async (discount: any) => {
    const next = discount.status === 'فعال' ? 'غیرفعال' : 'فعال';
    try {
      await updateDiscount(discount.id, { status: next });
      addToast({ title: 'به‌روز شد', description: discount.code, variant: 'success' });
      load();
    } catch (error) {
      addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' });
    }
  };

  const handleDelete = async (discount: any) => {
    if (!window.confirm(`کد «${discount.code}» حذف شود؟`)) return;
    try {
      await deleteDiscount(discount.id);
      addToast({ title: 'حذف شد', description: discount.code, variant: 'info' });
      load();
    } catch (error) {
      addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' });
    }
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
              {
                key: 'actions',
                header: 'عملیات',
                render: (d) => (
                  <div className="flex flex-wrap gap-2">
                    <button type="button" className="btn-ghost py-1 text-xs" onClick={() => handleToggleStatus(d)}>
                      {d.status === 'فعال' ? 'غیرفعال' : 'فعال'}
                    </button>
                    <button
                      type="button"
                      className="btn-ghost py-1 text-xs text-rose-300"
                      onClick={() => handleDelete(d)}
                    >
                      حذف
                    </button>
                  </div>
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
