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

export default function ProductTable({ products, loading }: { products: Product[]; loading?: boolean }) {
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
      ]}
    />
  );
}
