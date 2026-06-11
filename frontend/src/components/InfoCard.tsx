type InfoCardProps = {
  title: string;
  value: string;
  caption: string;
  accent?: 'neutral' | 'success' | 'warning' | 'accent';
};

const accentBar: Record<NonNullable<InfoCardProps['accent']>, string> = {
  neutral: 'var(--text-muted)',
  success: '#22c55e',
  warning: '#f59e0b',
  accent: 'var(--accent)',
};

export default function InfoCard({ title, value, caption, accent = 'neutral' }: InfoCardProps) {
  return (
    <div className="surface-card p-5 sm:p-6">
      <div className="mb-3 h-0.5 w-12 rounded-full" style={{ background: accentBar[accent] }} />
      <p className="text-sm text-[var(--text-muted)]">{title}</p>
      <p className="mt-2 text-2xl font-semibold sm:text-3xl">{value}</p>
      <p className="mt-2 text-xs text-[var(--text-muted)] sm:text-sm">{caption}</p>
    </div>
  );
}
