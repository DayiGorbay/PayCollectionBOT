import DataTable from './DataTable';

type Product = {
  id: number;
  name: string;
  price: string;
  duration?: string;
  durationDays?: number;
  panel: string;
  code: string;
  category?: string;
};

type Props = {
  products: Product[];
  loading?: boolean;
  onEdit?: (product: Product) => void;
  onDelete?: (product: Product) => void;
};

export default function ProductTable({ products, loading, onEdit, onDelete }: Props) {
  return (
    <DataTable
      loading={loading}
      data={products}
      rowKey={(p) => p.id}
      emptyTitle="محصولی ثبت نشده"
      columns={[
        { key: 'id', header: '#', render: (p) => p.id },
        { key: 'name', header: 'نام محصول', render: (p) => <span className="font-medium">{p.name}</span> },
        { key: 'price', header: 'قیمت', render: (p) => p.price },
        {
          key: 'duration',
          header: 'مدت',
          render: (p) => p.duration ?? (p.durationDays ? `${p.durationDays} روز` : '—'),
        },
        { key: 'panel', header: 'پنل', render: (p) => p.panel },
        { key: 'code', header: 'کد', render: (p) => <span className="font-mono text-xs">{p.code}</span> },
        { key: 'category', header: 'دسته', render: (p) => p.category ?? '—', hideOnMobile: true },
        {
          key: 'actions',
          header: 'عملیات',
          render: (p) => (
            <div className="flex flex-wrap gap-2">
              {onEdit ? (
                <button type="button" className="btn-ghost py-1 text-xs" onClick={() => onEdit(p)}>
                  ویرایش
                </button>
              ) : null}
              {onDelete ? (
                <button type="button" className="btn-ghost py-1 text-xs text-rose-300" onClick={() => onDelete(p)}>
                  حذف
                </button>
              ) : null}
            </div>
          ),
        },
      ]}
    />
  );
}
