import { FormEvent, useEffect, useMemo, useState } from 'react';
import { Download, X, Wifi } from 'lucide-react';
import { previewPanelInbounds } from '../services/api';
import { getApiErrorMessage } from '../services/apiClient';
import type { PanelCreatePayload } from '../types/api';

type InboundOption = { id: string; label: string; protocol?: string; port?: number; tag?: string };

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
  authMode: 'bearer',
  apiToken: '',
  inbounds: '',
  proxies: '',
  inboundId: undefined,
};

function buildMarzbanConfig(selected: InboundOption[]) {
  const inbounds: Record<string, string[]> = {};
  const proxies: Record<string, Record<string, never>> = {};
  for (const item of selected) {
    const protocol = item.protocol || 'vless';
    const tag = item.tag || item.id;
    inbounds[protocol] = inbounds[protocol] || [];
    if (!inbounds[protocol].includes(tag)) {
      inbounds[protocol].push(tag);
    }
    proxies[protocol] = proxies[protocol] || {};
  }
  return {
    inbounds: JSON.stringify(inbounds),
    proxies: JSON.stringify(proxies),
  };
}

export default function PanelFormModal({ open, onClose, onSubmit, onTest, testing = false }: Props) {
  const [form, setForm] = useState<PanelCreatePayload>(defaultForm);
  const [inboundOptions, setInboundOptions] = useState<InboundOption[]>([]);
  const [selectedInboundIds, setSelectedInboundIds] = useState<string[]>([]);
  const [loadingInbounds, setLoadingInbounds] = useState(false);
  const [inboundError, setInboundError] = useState<string | null>(null);

  const isMarzban = form.panelType === 'marzban';
  const isXui = form.panelType === 'xui';

  useEffect(() => {
    if (!open) {
      setForm(defaultForm);
      setInboundOptions([]);
      setSelectedInboundIds([]);
      setInboundError(null);
    }
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

  const basePayload = useMemo(
    (): PanelCreatePayload => ({
      ...form,
      codePanel: form.codePanel.trim(),
      apiUrl: form.apiUrl.trim().replace(/\/$/, ''),
      apiToken: form.apiToken?.trim() || undefined,
      status: 'فعال',
    }),
    [form],
  );

  const payload = useMemo((): PanelCreatePayload => {
    if (isMarzban && selectedInboundIds.length > 0) {
      const selected = inboundOptions.filter((item) => selectedInboundIds.includes(item.id));
      const config = buildMarzbanConfig(selected);
      return { ...basePayload, ...config };
    }
    if (isXui && selectedInboundIds.length > 0) {
      const first = selectedInboundIds[0];
      return { ...basePayload, inboundId: Number(first) };
    }
    return basePayload;
  }, [basePayload, inboundOptions, isMarzban, isXui, selectedInboundIds]);

  if (!open) return null;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (selectedInboundIds.length === 0) {
      setInboundError('حداقل یک Inbound انتخاب کنید.');
      return;
    }
    await onSubmit(payload);
    onClose();
  };

  const handleTest = async () => {
    if (onTest) await onTest(basePayload);
  };

  const handleFetchInbounds = async () => {
    setLoadingInbounds(true);
    setInboundError(null);
    try {
      const items = await previewPanelInbounds(basePayload);
      setInboundOptions(items);
      setSelectedInboundIds([]);
      if (items.length === 0) {
        setInboundError('Inbound فعالی یافت نشد.');
      }
    } catch (error) {
      setInboundError(getApiErrorMessage(error));
    } finally {
      setLoadingInbounds(false);
    }
  };

  const toggleInbound = (id: string) => {
    if (isXui) {
      setSelectedInboundIds([id]);
      return;
    }
    setSelectedInboundIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const set = <K extends keyof PanelCreatePayload>(key: K, value: PanelCreatePayload[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    if (key === 'panelType') {
      setInboundOptions([]);
      setSelectedInboundIds([]);
      setInboundError(null);
    }
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
            <p className="mt-1 text-sm text-[var(--text-muted)]">Inbounds از API پنل دریافت و انتخاب می‌شوند</p>
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
              </div>
            ) : null}

            <div className="space-y-3 rounded-2xl border p-4" style={{ borderColor: 'var(--border)' }}>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-medium text-[var(--accent)]">Inbounds</p>
                <button
                  type="button"
                  className="btn-ghost inline-flex items-center gap-2 py-1.5 text-xs"
                  disabled={loadingInbounds}
                  onClick={handleFetchInbounds}
                >
                  <Download className="h-3.5 w-3.5" />
                  {loadingInbounds ? 'در حال دریافت...' : 'دریافت از پنل'}
                </button>
              </div>
              {inboundError ? <p className="text-xs text-rose-400">{inboundError}</p> : null}
              {inboundOptions.length > 0 ? (
                <div className="max-h-48 space-y-2 overflow-y-auto">
                  {inboundOptions.map((item) => (
                    <label
                      key={item.id}
                      className="flex cursor-pointer items-center gap-2 rounded-xl px-3 py-2 text-sm"
                      style={{ background: 'var(--bg-muted)' }}
                    >
                      <input
                        type={isXui ? 'radio' : 'checkbox'}
                        name="inbound"
                        checked={selectedInboundIds.includes(item.id)}
                        onChange={() => toggleInbound(item.id)}
                      />
                      <span>{item.label}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-[var(--text-muted)]">
                  پس از وارد کردن اطلاعات اتصال، Inbounds را از پنل دریافت کنید.
                </p>
              )}
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
