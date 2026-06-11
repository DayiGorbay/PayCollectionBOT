import { FormEvent, useEffect, useMemo, useState } from 'react';
import { X, Wifi } from 'lucide-react';
import type { PanelCreatePayload } from '../types/api';

type Props = {
  open: boolean;
  onClose: () => void;
  onSubmit: (payload: PanelCreatePayload) => void | Promise<void>;
  onTest?: (payload: PanelCreatePayload) => void | Promise<void>;
  testing?: boolean;
};

const defaultForm: PanelCreatePayload = {
  name: '',
  codePanel: '',
  apiUrl: '',
  panelType: 'marzban',
  usernamePanel: '',
  passwordPanel: '',
  status: 'فعال',
  authMode: 'bearer',
  apiToken: '',
  inbounds: '',
  proxies: '',
  inboundId: undefined,
};

export default function PanelFormModal({ open, onClose, onSubmit, onTest, testing = false }: Props) {
  const [form, setForm] = useState<PanelCreatePayload>(defaultForm);

  const isMarzban = form.panelType === 'marzban';
  const isXui = form.panelType === 'xui';

  useEffect(() => {
    if (!open) setForm(defaultForm);
  }, [open]);

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

  const payload = useMemo(
    (): PanelCreatePayload => ({
      ...form,
      codePanel: form.codePanel.trim(),
      apiUrl: form.apiUrl.trim().replace(/\/$/, ''),
      inbounds: form.inbounds?.trim() || undefined,
      proxies: form.proxies?.trim() || undefined,
      apiToken: form.apiToken?.trim() || undefined,
      inboundId: isXui && form.inboundId ? Number(form.inboundId) : undefined,
    }),
    [form, isXui],
  );

  if (!open) return null;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await onSubmit(payload);
    onClose();
  };

  const handleTest = async () => {
    if (onTest) await onTest(payload);
  };

  const set = <K extends keyof PanelCreatePayload>(key: K, value: PanelCreatePayload[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center p-0 sm:items-center sm:p-4">
      <button type="button" className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} aria-label="بستن" />
      <div
        className="relative z-10 flex max-h-[92vh] w-full max-w-xl flex-col overflow-hidden rounded-t-3xl border sm:rounded-3xl"
        style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}
        role="dialog"
        aria-modal="true"
      >
        <div className="flex items-start justify-between gap-3 border-b px-5 py-4" style={{ borderColor: 'var(--border)' }}>
          <div>
            <h2 className="text-lg font-semibold">پنل جدید</h2>
            <p className="mt-1 text-sm text-[var(--text-muted)]">اتصال از طریق OpenAPI رسمی Marzban / 3X-UI</p>
          </div>
          <button type="button" className="icon-btn shrink-0" onClick={onClose} aria-label="بستن">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="overflow-y-auto px-5 py-4">
          <div className="space-y-4">
            <div>
              <label className="mb-2 block text-sm text-[var(--text-muted)]">نوع پنل *</label>
              <select
                className="input-field"
                value={form.panelType}
                onChange={(e) => set('panelType', e.target.value as 'marzban' | 'xui')}
                required
              >
                <option value="marzban">Marzban</option>
                <option value="xui">3X-UI</option>
              </select>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm text-[var(--text-muted)]">نام نمایشی *</label>
                <input className="input-field" value={form.name} onChange={(e) => set('name', e.target.value)} required />
              </div>
              <div>
                <label className="mb-2 block text-sm text-[var(--text-muted)]">کد یکتا *</label>
                <input
                  className="input-field font-mono text-sm"
                  value={form.codePanel}
                  onChange={(e) => set('codePanel', e.target.value)}
                  pattern="[a-zA-Z0-9_-]+"
                  required
                />
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm text-[var(--text-muted)]">آدرس پنل (URL) *</label>
              <input
                type="url"
                className="input-field"
                value={form.apiUrl}
                onChange={(e) => set('apiUrl', e.target.value)}
                placeholder="https://panel.example.com"
                required
              />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm text-[var(--text-muted)]">نام کاربری ادمین *</label>
                <input
                  className="input-field"
                  value={form.usernamePanel}
                  onChange={(e) => set('usernamePanel', e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="mb-2 block text-sm text-[var(--text-muted)]">رمز عبور *</label>
                <input
                  type="password"
                  className="input-field"
                  value={form.passwordPanel}
                  onChange={(e) => set('passwordPanel', e.target.value)}
                  required
                />
              </div>
            </div>

            {isXui ? (
              <div className="space-y-4 rounded-2xl border p-4" style={{ borderColor: 'var(--border)' }}>
                <p className="text-sm font-medium text-[var(--accent)]">احراز هویت 3X-UI</p>
                <div>
                  <label className="mb-2 block text-sm text-[var(--text-muted)]">روش احراز</label>
                  <select
                    className="input-field"
                    value={form.authMode}
                    onChange={(e) => set('authMode', e.target.value as 'bearer' | 'session')}
                  >
                    <option value="bearer">Bearer API Token (پیشنهادی)</option>
                    <option value="session">Session / Cookie (Login)</option>
                  </select>
                </div>
                {form.authMode === 'bearer' ? (
                  <div>
                    <label className="mb-2 block text-sm text-[var(--text-muted)]">API Token *</label>
                    <input
                      type="password"
                      className="input-field font-mono text-sm"
                      value={form.apiToken ?? ''}
                      onChange={(e) => set('apiToken', e.target.value)}
                      placeholder="از Settings → Security → API Token"
                      required={form.authMode === 'bearer'}
                    />
                  </div>
                ) : null}
                <div>
                  <label className="mb-2 block text-sm text-[var(--text-muted)]">شناسه Inbound *</label>
                  <input
                    type="number"
                    className="input-field"
                    value={form.inboundId ?? ''}
                    onChange={(e) => set('inboundId', e.target.value ? Number(e.target.value) : undefined)}
                    min={1}
                    required
                  />
                </div>
              </div>
            ) : null}

            {isMarzban ? (
              <div className="space-y-4 rounded-2xl border p-4" style={{ borderColor: 'var(--border)' }}>
                <p className="text-sm font-medium text-[var(--accent)]">تنظیمات Marzban (UserCreate)</p>
                <div>
                  <label className="mb-2 block text-sm text-[var(--text-muted)]">Inbounds (JSON)</label>
                  <textarea
                    className="input-field resize-none font-mono text-xs"
                    rows={3}
                    value={form.inbounds ?? ''}
                    onChange={(e) => set('inbounds', e.target.value)}
                    placeholder='{"vless": ["VLESS_INBOUND"], "vmess": ["VMess TCP"]}'
                  />
                </div>
                <div>
                  <label className="mb-2 block text-sm text-[var(--text-muted)]">Proxies (JSON)</label>
                  <textarea
                    className="input-field resize-none font-mono text-xs"
                    rows={3}
                    value={form.proxies ?? ''}
                    onChange={(e) => set('proxies', e.target.value)}
                    placeholder='{"vless": {}, "vmess": {}}'
                  />
                </div>
              </div>
            ) : null}

            <div>
              <label className="mb-2 block text-sm text-[var(--text-muted)]">وضعیت</label>
              <select className="input-field" value={form.status} onChange={(e) => set('status', e.target.value)}>
                <option value="فعال">فعال</option>
                <option value="در انتظار">در انتظار</option>
                <option value="غیرفعال">غیرفعال</option>
              </select>
            </div>
          </div>

          <div className="mt-6 flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:justify-end">
            {onTest ? (
              <button
                type="button"
                className="btn-ghost inline-flex items-center justify-center gap-2 sm:order-first sm:mr-auto"
                disabled={testing}
                onClick={handleTest}
              >
                <Wifi className="h-4 w-4" />
                {testing ? 'در حال تست...' : 'تست اتصال'}
              </button>
            ) : null}
            <button type="button" className="btn-ghost w-full sm:w-auto" onClick={onClose}>
              انصراف
            </button>
            <button type="submit" className="btn-primary w-full sm:w-auto">
              ایجاد پنل
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
