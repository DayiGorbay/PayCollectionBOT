import { FormEvent, useEffect, useState } from 'react';
import { fetchFreeConnectConfig, fetchPanels, saveFreeConnectConfig } from '../services/api';
import { getApiErrorMessage } from '../services/apiClient';
import { ROUTE_META } from '../config/navigation';
import { useAppContext } from '../context/AppContext';

type PanelOption = { id: number; name: string };

export default function FreeConnectPage() {
  const { addToast } = useAppContext();
  const [panels, setPanels] = useState<PanelOption[]>([]);
  const [form, setForm] = useState({
    coinsRequired: '5',
    dataGb: '10',
    panelId: '',
    durationDays: '30',
    isActive: false,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const meta = ROUTE_META['/free-connect'];

  useEffect(() => {
    Promise.all([fetchFreeConnectConfig(), fetchPanels()])
      .then(([config, panelList]) => {
        setForm({
          coinsRequired: String(config.coinsRequired ?? 5),
          dataGb: String(config.dataGb ?? 10),
          panelId: config.panelId ? String(config.panelId) : '',
          durationDays: String(config.durationDays ?? 30),
          isActive: Boolean(config.isActive),
        });
        setPanels(panelList.map((p: { id: number; name: string }) => ({ id: p.id, name: p.name })));
      })
      .finally(() => setLoading(false));
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await saveFreeConnectConfig({
        coinsRequired: Number(form.coinsRequired),
        dataGb: Number(form.dataGb),
        panelId: form.panelId ? Number(form.panelId) : null,
        durationDays: Number(form.durationDays),
        isActive: form.isActive,
      });
      addToast({ title: 'ذخیره شد', description: 'پیکربندی اتصال رایگان به‌روز شد.', variant: 'success' });
    } catch (error) {
      addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-5 sm:space-y-6">
      <div>
        <h1 className="text-2xl font-bold sm:text-3xl">{meta.title}</h1>
        {meta.subtitle ? <p className="mt-2 text-sm text-[var(--text-muted)]">{meta.subtitle}</p> : null}
      </div>

      <form onSubmit={handleSubmit} className="surface-card max-w-xl space-y-4 p-5 sm:p-6">
        {loading ? (
          <p className="text-sm text-[var(--text-muted)]">در حال بارگذاری...</p>
        ) : (
          <>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm text-[var(--text-muted)]">تعداد کوین مورد نیاز</label>
                <input
                  type="number"
                  min={1}
                  className="input-field"
                  value={form.coinsRequired}
                  onChange={(e) => setForm((f) => ({ ...f, coinsRequired: e.target.value }))}
                  required
                />
              </div>
              <div>
                <label className="mb-2 block text-sm text-[var(--text-muted)]">حجم (گیگابایت)</label>
                <input
                  type="number"
                  min={1}
                  className="input-field"
                  value={form.dataGb}
                  onChange={(e) => setForm((f) => ({ ...f, dataGb: e.target.value }))}
                  required
                />
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm text-[var(--text-muted)]">مدت (روز)</label>
                <input
                  type="number"
                  min={1}
                  className="input-field"
                  value={form.durationDays}
                  onChange={(e) => setForm((f) => ({ ...f, durationDays: e.target.value }))}
                  required
                />
              </div>
              <div>
                <label className="mb-2 block text-sm text-[var(--text-muted)]">پنل</label>
                <select
                  className="input-field"
                  value={form.panelId}
                  onChange={(e) => setForm((f) => ({ ...f, panelId: e.target.value }))}
                  required
                >
                  <option value="">انتخاب پنل</option>
                  {panels.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={form.isActive}
                onChange={(e) => setForm((f) => ({ ...f, isActive: e.target.checked }))}
              />
              فعال بودن اتصال رایگان در ربات
            </label>
          </>
        )}

        <div className="flex justify-end pt-2">
          <button type="submit" className="btn-primary" disabled={loading || saving || panels.length === 0}>
            {saving ? 'در حال ذخیره...' : 'ذخیره پیکربندی'}
          </button>
        </div>
      </form>
    </div>
  );
}
