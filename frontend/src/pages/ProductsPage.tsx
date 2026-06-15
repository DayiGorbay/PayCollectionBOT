import { useEffect, useState } from 'react';
import { Plus, Search } from 'lucide-react';
import { createProduct, deleteProduct, fetchProducts, updateProduct } from '../services/api';
import { getApiErrorMessage } from '../services/apiClient';
import { ROUTE_META } from '../config/navigation';
import ProductTable from '../components/ProductTable';
import ProductFormModal from '../components/ProductFormModal';
import { useAppContext } from '../context/AppContext';
import type { ProductCreatePayload } from '../types/api';

type ProductRow = ProductCreatePayload & { id: number; price?: string; panel?: string; duration?: string };

export default function ProductsPage() {
  const { addToast } = useAppContext();
  const [products, setProducts] = useState<ProductRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<ProductRow | null>(null);
  const meta = ROUTE_META['/products'];

  const load = () => {
    setLoading(true);
    fetchProducts()
      .then((data) => setProducts(data))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (payload: ProductCreatePayload) => {
    try {
      await createProduct(payload);
      addToast({ title: 'محصول جدید', description: payload.name, variant: 'success' });
      setModalOpen(false);
      load();
    } catch (error) {
      addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' });
    }
  };

  const handleUpdate = async (payload: ProductCreatePayload) => {
    if (!editing) return;
    try {
      await updateProduct(editing.id, payload);
      addToast({ title: 'ویرایش شد', description: payload.name, variant: 'success' });
      setEditing(null);
      load();
    } catch (error) {
      addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' });
    }
  };

  const handleDelete = async (product: ProductRow) => {
    if (!window.confirm(`محصول «${product.name}» حذف شود؟`)) return;
    try {
      await deleteProduct(product.id);
      addToast({ title: 'حذف شد', description: product.name, variant: 'info' });
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
          <p className="mt-2 text-sm text-[var(--text-muted)]">{meta.subtitle}</p>
          <p className="mt-1 text-sm text-[var(--text-muted)]">{products.length} محصول ثبت شده</p>
        </div>
        <button
          type="button"
          className="btn-primary inline-flex items-center justify-center gap-2"
          onClick={() => setModalOpen(true)}
        >
          <Plus className="h-4 w-4" />
          افزودن محصول
        </button>
      </div>

      <section className="table-shell">
        <div
          className="flex flex-col gap-3 border-b p-4 sm:flex-row sm:items-center sm:justify-between sm:px-5"
          style={{ borderColor: 'var(--border)' }}
        >
          <h2 className="font-semibold">فهرست محصولات ({products.length})</h2>
          <div className="relative w-full sm:w-72">
            <input type="search" placeholder="جستجو..." className="input-field w-full py-2.5 pl-10 pr-4" />
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-muted)]" />
          </div>
        </div>
        <div className="p-3 sm:p-4">
          <ProductTable
            products={products}
            loading={loading}
            onEdit={(product) => setEditing(product)}
            onDelete={handleDelete}
          />
        </div>
      </section>

      <ProductFormModal open={modalOpen} onClose={() => setModalOpen(false)} onSubmit={handleCreate} />
      <ProductFormModal
        open={Boolean(editing)}
        onClose={() => setEditing(null)}
        onSubmit={handleUpdate}
        initial={editing ?? undefined}
        title="ویرایش محصول"
        submitLabel="ذخیره تغییرات"
      />
    </div>
  );
}
