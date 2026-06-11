type Props = {
  value: string;
  label: string;
  accent?: 'green' | 'yellow' | 'neutral';
};

const accentBar = {
  green: '#22c55e',
  yellow: '#f59e0b',
  neutral: 'var(--text-muted)',
};

export default function StatsCard({ value, label, accent = 'neutral' }: Props) {
  return (
    <div className="surface-card p-5 sm:p-6">
      <div className="mb-3 h-0.5 w-10 rounded-full" style={{ background: accentBar[accent] }} />
      <p className="text-sm text-[var(--text-muted)]">{label}</p>
      <p className="mt-2 text-2xl font-semibold sm:text-3xl">{value}</p>
    </div>
  );
}
