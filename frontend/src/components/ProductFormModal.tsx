import { FormEvent, useEffect, useState } from 'react';
import { X } from 'lucide-react';
import { fetchPanels } from '../services/api';
import type { ProductCreatePayload } from '../types/api';

type PanelOption = { id: number; name: string };

type Props = {
  open: boolean;
  onClose: () => void;
  onSubmit: (payload: ProductCreatePayload) => void | Promise<void>;
  initial?: Partial<ProductCreatePayload> & { id?: number; price?: string | number; durationDays?: number };
  title?: string;
  submitLabel?: string;
};

const emptyForm = {
  name: '',
  price: '',
  durationDays: '30',
  panelId: '',
  code: '',
  category: '',
};

export default function ProductFormModal({
  open,
  onClose,
  onSubmit,
  initial,
  title = 'افزودن محصول',
  submitLabel = 'ثبت محصول',
}: Props) {
  const [form, setForm] = useState(emptyForm);
  const [panels, setPanels] = useState<PanelOption[]>([]);
  const [loadingPanels, setLoadingPanels] = useState(false);

  useEffect(() => {
    if (!open) {
      setForm(emptyForm);
      return;
    }
    if (initial) {
      const priceValue =
        typeof initial.price === 'number'
          ? String(initial.price)
          : String(initial.price ?? '').replace(/\D/g, '') || '';
      setForm({
        name: initial.name ?? '',
        price: priceValue,
        durationDays: String(initial.durationDays ?? 30),
        panelId: String(initial.panelId ?? ''),
        code: initial.code ?? '',
        category: initial.category ?? '',
      });
    }
    setLoadingPanels(true);
    fetchPanels()
      .then((data) =>
        setPanels(
          data.map((p: { id: number; name: string }) => ({
            id: p.id,
            name: p.name,
          })),
        ),
      )
      .finally(() => setLoadingPanels(false));
  }, [open, initial]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = '';
    };
  }, [open, onClose]);

  if (!open) return null;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await onSubmit({
      name: form.name.trim(),
      price: Number(form.price),
      durationDays: Number(form.durationDays),
      panelId: Number(form.panelId),
      code: form.code.trim(),
      category: form.category.trim() || undefined,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center p-0 sm:items-center sm:p-4">
      <button type="button" className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} aria-label="بستن" />
      <div
        className="relative z-10 flex max-h-[92vh] w-full max-w-lg flex-col overflow-hidden rounded-t-3xl border sm:rounded-3xl"
        style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}
        role="dialog"
        aria-modal="true"
      >
        <div className="flex items-start justify-between gap-3 border-b px-5 py-4" style={{ borderColor: 'var(--border)' }}>
          <div>
            <h2 className="text-lg font-semibold">{title}</h2>
            <p className="mt-1 text-sm text-[var(--text-muted)]">این محصول در ربات تلگرام نمایش داده می‌شود</p>
          </div>
          <button type="button" className="icon-btn shrink-0" onClick={onClose} aria-label="بستن">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="overflow-y-auto px-5 py-4">
          <div className="space-y-4">
            <div>
              <label htmlFor="product-name" className="mb-2 block text-sm text-[var(--text-muted)]">
                نام محصول <span className="text-rose-400">*</span>
              </label>
              <input
                id="product-name"
                className="input-field"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="مثال: پلن ایران ۱۰ گیگ"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="product-price" className="mb-2 block text-sm text-[var(--text-muted)]">
                  قیمت (تومان) <span className="text-rose-400">*</span>
                </label>
                <input
                  id="product-price"
                  type="number"
                  min={1}
                  className="input-field"
                  value={form.price}
                  onChange={(e) => setForm((f) => ({ ...f, price: e.target.value }))}
                  placeholder="100000"
                  required
                />
              </div>
              <div>
                <label htmlFor="product-duration" className="mb-2 block text-sm text-[var(--text-muted)]">
                  مدت (روز) <span className="text-rose-400">*</span>
                </label>
                <input
                  id="product-duration"
                  type="number"
                  min={1}
                  className="input-field"
                  value={form.durationDays}
                  onChange={(e) => setForm((f) => ({ ...f, durationDays: e.target.value }))}
                  placeholder="30"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="product-panel" className="mb-2 block text-sm text-[var(--text-muted)]">
                پنل <span className="text-rose-400">*</span>
              </label>
              <select
                id="product-panel"
                className="input-field"
                value={form.panelId}
                onChange={(e) => setForm((f) => ({ ...f, panelId: e.target.value }))}
                required
                disabled={loadingPanels}
              >
                <option value="">{loadingPanels ? 'در حال بارگذاری...' : 'انتخاب پنل'}</option>
                {panels.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
              {!loadingPanels && panels.length === 0 ? (
                <p className="mt-2 text-xs text-amber-400">ابتدا از بخش «پنل‌ها» یک پنل اضافه کنید.</p>
              ) : null}
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="product-code" className="mb-2 block text-sm text-[var(--text-muted)]">
                  کد محصول <span className="text-rose-400">*</span>
                </label>
                <input
                  id="product-code"
                  className="input-field font-mono text-sm"
                  value={form.code}
                  onChange={(e) => setForm((f) => ({ ...f, code: e.target.value }))}
                  placeholder="IR10"
                  required
                />
              </div>
              <div>
                <label htmlFor="product-category" className="mb-2 block text-sm text-[var(--text-muted)]">
                  دسته‌بندی
                </label>
                <input
                  id="product-category"
                  className="input-field"
                  value={form.category}
                  onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
                  placeholder="ایران"
                />
              </div>
            </div>
          </div>

          <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <button type="button" className="btn-ghost w-full sm:w-auto" onClick={onClose}>
              انصراف
            </button>
            <button type="submit" className="btn-primary w-full sm:w-auto" disabled={panels.length === 0}>
              {submitLabel}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
