import { ReactNode } from 'react';

type PageHeaderProps = {
  subtitle?: string;
  actions?: ReactNode;
  count?: number;
};

/** زیرعنوان صفحه — عنوان اصلی در Navbar نمایش داده می‌شود */
export default function PageHeader({ subtitle, actions, count }: PageHeaderProps) {
  if (!subtitle && !actions && count === undefined) return null;

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      {subtitle ? <p className="text-sm text-[var(--text-muted)] sm:text-base">{subtitle}</p> : <div />}
      <div className="flex flex-wrap items-center gap-2 sm:gap-3">
        {count !== undefined ? (
          <span className="text-sm text-[var(--text-muted)]">{count.toLocaleString('fa-IR')} مورد</span>
        ) : null}
        {actions}
      </div>
    </div>
  );
}
