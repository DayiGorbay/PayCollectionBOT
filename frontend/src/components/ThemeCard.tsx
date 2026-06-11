import { Check } from 'lucide-react';

type ThemeCardProps = {
  title: string;
  subtitle: string;
  colors: string[];
  selected?: boolean;
  onSelect?: () => void;
};

export default function ThemeCard({ title, subtitle, colors, selected = false, onSelect }: ThemeCardProps) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`relative w-full overflow-hidden rounded-2xl border p-4 text-right transition ${
        selected ? 'ring-2 ring-[var(--text-primary)]' : 'hover:border-[var(--text-muted)]'
      }`}
      style={{
        borderColor: selected ? 'var(--text-primary)' : 'var(--border)',
        background: 'var(--bg-card)',
      }}
    >
      {selected ? (
        <span
          className="absolute left-3 top-3 flex h-6 w-6 items-center justify-center rounded-full"
          style={{ background: 'var(--text-primary)', color: 'var(--bg-base)' }}
        >
          <Check className="h-3.5 w-3.5" />
        </span>
      ) : null}

      <div className="mb-3 flex h-16 gap-1.5 overflow-hidden rounded-xl p-1.5" style={{ background: 'var(--bg-muted)' }}>
        {colors.map((color) => (
          <div key={color} className="h-full flex-1 rounded-lg" style={{ background: color }} />
        ))}
      </div>
      <h3 className="text-sm font-semibold">{title}</h3>
      <p className="mt-1 text-xs text-[var(--text-muted)]">{subtitle}</p>
    </button>
  );
}
