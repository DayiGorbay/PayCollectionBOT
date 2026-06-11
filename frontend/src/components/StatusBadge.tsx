type BadgeVariant = 'success' | 'warning' | 'danger' | 'info';

type StatusBadgeProps = {
  label: string;
  variant?: BadgeVariant;
};

const badgeStyles: Record<BadgeVariant, string> = {
  success: 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/15',
  warning: 'bg-amber-500/10 text-amber-300 border border-amber-500/15',
  danger: 'bg-rose-500/10 text-rose-300 border border-rose-500/15',
  info: 'bg-sky-500/10 text-sky-300 border border-sky-500/15',
};

export default function StatusBadge({ label, variant = 'info' }: StatusBadgeProps) {
  return <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${badgeStyles[variant]}`}>{label}</span>;
}
