import { FormEvent, useEffect, useState } from 'react';
import { fetchBotSettings, saveBotSettings } from '../services/api';
import { getApiErrorMessage } from '../services/apiClient';
import { ROUTE_META } from '../config/navigation';
import { useAppContext } from '../context/AppContext';

const fields = [
  { key: 'paymentCardNumber', label: 'شماره کارت', placeholder: '6037-xxxx-xxxx-xxxx' },
  { key: 'paymentCardHolder', label: 'نام صاحب کارت', placeholder: 'نام و نام خانوادگی' },
  { key: 'channelId', label: 'آیدی کانال (عددی)', placeholder: '-1001234567890' },
  { key: 'channelLink', label: 'لینک کانال', placeholder: 'https://t.me/yourchannel' },
  { key: 'channelUsername', label: 'یوزرنیم کانال', placeholder: '@yourchannel' },
  { key: 'adminTelegramId', label: 'آیدی تلگرام ادمین', placeholder: '123456789' },
  { key: 'minTopupRial', label: 'حداقل شارژ (ریال)', placeholder: '10000' },
  { key: 'referralDailyCap', label: 'سقف روزانه دعوت', placeholder: '50' },
  { key: 'logLevel', label: 'سطح لاگ', placeholder: 'INFO' },
] as const;

export default function BotConfigPage() {
  const { addToast } = useAppContext();
  const [form, setForm] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const meta = ROUTE_META['/bot-config'];

  useEffect(() => {
    fetchBotSettings()
      .then((data) => setForm(data))
      .finally(() => setLoading(false));
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await saveBotSettings({
        ...form,
        requireChannelJoin: form.requireChannelJoin ?? 'true',
      });
      addToast({ title: 'ذخیره شد', description: 'تنظیمات ربات به‌روزرسانی شد.', variant: 'success' });
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

      <form onSubmit={handleSubmit} className="surface-card max-w-2xl space-y-4 p-5 sm:p-6">
        {loading ? (
          <p className="text-sm text-[var(--text-muted)]">در حال بارگذاری...</p>
        ) : (
          <>
            {fields.map((field) => (
              <div key={field.key}>
                <label className="mb-2 block text-sm text-[var(--text-muted)]">{field.label}</label>
                <input
                  className="input-field"
                  value={form[field.key] ?? ''}
                  onChange={(e) => setForm((prev) => ({ ...prev, [field.key]: e.target.value }))}
                  placeholder={field.placeholder}
                />
              </div>
            ))}
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={(form.requireChannelJoin ?? 'true') === 'true'}
                onChange={(e) =>
                  setForm((prev) => ({ ...prev, requireChannelJoin: e.target.checked ? 'true' : 'false' }))
                }
              />
              عضویت در کانال الزامی باشد
            </label>
          </>
        )}

        <div className="flex justify-end pt-2">
          <button type="submit" className="btn-primary" disabled={loading || saving}>
            {saving ? 'در حال ذخیره...' : 'ذخیره تنظیمات'}
          </button>
        </div>
      </form>
    </div>
  );
}
