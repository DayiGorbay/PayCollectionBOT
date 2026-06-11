import { useEffect, useState } from 'react';
import { Plus, Search } from 'lucide-react';
import { createProduct, fetchProducts } from '../services/api';
import { getApiErrorMessage } from '../services/apiClient';
import { ROUTE_META } from '../config/navigation';
import ProductTable from '../components/ProductTable';
import ProductFormModal from '../components/ProductFormModal';
import { useAppContext } from '../context/AppContext';
import type { ProductCreatePayload } from '../types/api';

export default function ProductsPage() {
  const { addToast } = useAppContext();
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const meta = ROUTE_META['/products'];

  useEffect(() => {
    fetchProducts()
      .then((data) => setProducts(data))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (payload: ProductCreatePayload) => {
    try {
      const created = await createProduct(payload);
      setProducts((prev) => [created, ...prev]);
      addToast({ title: 'محصول جدید', description: payload.name, variant: 'success' });
      setModalOpen(false);
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
          <ProductTable products={products} loading={loading} />
        </div>
      </section>

      <ProductFormModal open={modalOpen} onClose={() => setModalOpen(false)} onSubmit={handleCreate} />
    </div>
  );
}
