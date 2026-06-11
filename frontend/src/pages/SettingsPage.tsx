import { useEffect, useState } from 'react';
import { fetchSettings } from '../services/api';
import { useAppContext } from '../context/AppContext';
import { PANEL_THEMES } from '../config/panelThemes';
import { ROUTE_META } from '../config/navigation';
import ThemeCard from '../components/ThemeCard';

export default function SettingsPage() {
  const { panelThemeId, setPanelThemeId } = useAppContext();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetchSettings().then(setData);
  }, []);

  const meta = ROUTE_META['/settings'];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold sm:text-3xl">{meta.title}</h1>
        {meta.subtitle ? <p className="mt-2 text-sm text-[var(--text-muted)]">{meta.subtitle}</p> : null}
      </div>

      <section className="surface-card p-5 sm:p-6">
        <h2 className="mb-1 text-lg font-semibold">رنگ‌بندی پنل</h2>
        <p className="mb-6 text-sm text-[var(--text-muted)]">
          با انتخاب هر تم، رنگ پس‌زمینه، کارت‌ها، دکمه‌ها و لوگو به‌صورت یکپارچه اعمال می‌شود.
        </p>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {PANEL_THEMES.map((theme) => (
            <ThemeCard
              key={theme.id}
              title={theme.title}
              subtitle={theme.subtitle}
              colors={theme.colors}
              selected={panelThemeId === theme.id}
              onSelect={() => setPanelThemeId(theme.id)}
            />
          ))}
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="surface-card p-5 sm:p-6">
          <h3 className="text-lg font-semibold">تغییر رمز عبور</h3>
          <p className="mt-1 text-sm text-[var(--text-muted)]">برای ورود به پنل</p>
          <div className="mt-5 space-y-4">
            <div>
              <label htmlFor="current-password" className="mb-2 block text-sm text-[var(--text-muted)]">
                رمز فعلی
              </label>
              <input id="current-password" type="password" autoComplete="current-password" className="input-field" />
            </div>
            <div>
              <label htmlFor="new-password" className="mb-2 block text-sm text-[var(--text-muted)]">
                رمز جدید
              </label>
              <input id="new-password" type="password" autoComplete="new-password" className="input-field" placeholder="حداقل ۸ کاراکتر" />
            </div>
            <button type="button" className="btn-primary w-full">
              ذخیره تغییرات
            </button>
          </div>
        </div>

        <div className="surface-card p-5 sm:p-6">
          <h3 className="text-lg font-semibold">اطلاعات پنل</h3>
          <dl className="mt-5 space-y-3 text-sm">
            <div className="flex justify-between gap-4 rounded-xl px-4 py-3" style={{ background: 'var(--bg-muted)' }}>
              <dt className="text-[var(--text-muted)]">نام پنل</dt>
              <dd className="font-medium">{data?.profileName ?? '—'}</dd>
            </div>
            <div className="flex justify-between gap-4 rounded-xl px-4 py-3" style={{ background: 'var(--bg-muted)' }}>
              <dt className="text-[var(--text-muted)]">نسخه پنل</dt>
              <dd className="font-medium">{data?.version ?? '—'}</dd>
            </div>
            <div className="flex justify-between gap-4 rounded-xl px-4 py-3" style={{ background: 'var(--bg-muted)' }}>
              <dt className="text-[var(--text-muted)]">تم فعال</dt>
              <dd className="font-medium">{PANEL_THEMES.find((t) => t.id === panelThemeId)?.title ?? '—'}</dd>
            </div>
          </dl>
        </div>
      </section>
    </div>
  );
}
