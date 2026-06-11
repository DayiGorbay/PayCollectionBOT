import { ReactNode } from 'react';
import EmptyState from './EmptyState';

export type DataColumn<T> = {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  hideOnMobile?: boolean;
};

type DataTableProps<T> = {
  columns: DataColumn<T>[];
  data: T[];
  loading?: boolean;
  rowKey: (row: T) => string | number;
  emptyTitle?: string;
  skeletonRows?: number;
  onRowClick?: (row: T) => void;
};

export default function DataTable<T>({
  columns,
  data,
  loading = false,
  rowKey,
  emptyTitle = 'موردی یافت نشد',
  skeletonRows = 5,
  onRowClick,
}: DataTableProps<T>) {
  const rowClass = onRowClick ? 'cursor-pointer hover:bg-[var(--bg-muted)]' : '';
  const mobileColumns = columns.filter((c) => !c.hideOnMobile);

  if (loading) {
    return (
      <>
        <div className="space-y-3 md:hidden">
          {Array.from({ length: skeletonRows }).map((_, i) => (
            <div key={i} className="h-36 animate-pulse rounded-2xl bg-[var(--bg-muted)]" />
          ))}
        </div>
        <div className="hidden overflow-x-auto md:block">
          <table className="data-table min-w-full">
            <thead>
              <tr>
                {columns.map((col) => (
                  <th key={col.key}>{col.header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Array.from({ length: skeletonRows }).map((_, i) => (
                <tr key={i} className="animate-pulse">
                  {columns.map((col) => (
                    <td key={col.key} className="h-12" />
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </>
    );
  }

  if (!data.length) {
    return <EmptyState title={emptyTitle} />;
  }

  return (
    <>
      <div className="space-y-3 md:hidden">
        {data.map((row) => (
          <article
            key={rowKey(row)}
            className={`rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-4 ${rowClass}`}
            onClick={onRowClick ? () => onRowClick(row) : undefined}
            onKeyDown={
              onRowClick
                ? (e) => {
                    if (e.key === 'Enter') onRowClick(row);
                  }
                : undefined
            }
            role={onRowClick ? 'button' : undefined}
            tabIndex={onRowClick ? 0 : undefined}
          >
            <dl className="space-y-2.5">
              {mobileColumns.map((col) => (
                <div key={col.key} className="flex items-start justify-between gap-3 text-sm">
                  <dt className="shrink-0 text-[var(--text-muted)]">{col.header}</dt>
                  <dd className="text-left font-medium text-[var(--text-primary)]">{col.render(row)}</dd>
                </div>
              ))}
            </dl>
          </article>
        ))}
      </div>

      <div className="hidden overflow-x-auto md:block">
        <table className="data-table min-w-full">
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col.key}>{col.header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={rowKey(row)} className={rowClass} onClick={onRowClick ? () => onRowClick(row) : undefined}>
                {columns.map((col) => (
                  <td key={col.key}>{col.render(row)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
