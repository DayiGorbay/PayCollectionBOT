import { Activity, ArrowDownUp, Cpu, HardDrive, UserCheck, UserX, Users, Wifi } from 'lucide-react';
import type { PanelStats } from '../types/api';

function formatBytes(bytes: number | null | undefined): string {
  if (bytes == null || bytes < 0) return '—';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let value = bytes;
  let i = 0;
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024;
    i += 1;
  }
  return `${value.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

function formatCount(value: number | null | undefined): string {
  if (value == null) return '—';
  return value.toLocaleString('fa-IR');
}

function StatRow({ icon: Icon, label, value }: { icon: typeof Cpu; label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-2 text-xs">
      <span className="flex items-center gap-1.5 text-[var(--text-muted)]">
        <Icon className="h-3.5 w-3.5 shrink-0" />
        {label}
      </span>
      <span className="font-medium text-[var(--text-primary)]">{value}</span>
    </div>
  );
}

type Props = {
  stats: PanelStats | undefined;
  loading?: boolean;
};

export default function PanelStatsBlock({ stats, loading }: Props) {
  if (loading && !stats) {
    return (
      <div className="mt-3 animate-pulse space-y-2 rounded-xl border p-3" style={{ borderColor: 'var(--border)' }}>
        <div className="h-3 w-24 rounded bg-[var(--bg-muted)]" />
        <div className="h-3 w-full rounded bg-[var(--bg-muted)]" />
        <div className="h-3 w-3/4 rounded bg-[var(--bg-muted)]" />
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="mt-3 rounded-xl border px-3 py-2.5 text-xs text-[var(--text-muted)]" style={{ borderColor: 'var(--border)' }}>
        در انتظار دریافت آمار سرور...
      </div>
    );
  }

  if (!stats.ok) {
    return (
      <div
        className="mt-3 rounded-xl border px-3 py-2.5 text-xs text-rose-400"
        style={{ borderColor: 'var(--border)', background: 'var(--bg-muted)' }}
      >
        خطا در دریافت آمار: {stats.error ?? 'نامشخص'}
      </div>
    );
  }

  const isXui = stats.panelType === 'xui';

  return (
    <div className="mt-3 space-y-2 rounded-xl border p-3" style={{ borderColor: 'var(--border)', background: 'var(--bg-muted)' }}>
      <div className="flex items-center justify-between gap-2">
        <span className="flex items-center gap-1.5 text-xs font-medium text-[var(--accent)]">
          <Activity className="h-3.5 w-3.5" />
          آمار زنده
        </span>
        <span className="text-[10px] text-[var(--text-muted)]">{stats.fetchedAt}</span>
      </div>

      <div className="space-y-1.5">
        <p className="text-[10px] font-medium uppercase tracking-wide text-[var(--text-muted)]">کاربران</p>
        <StatRow icon={Users} label="کل کاربران" value={formatCount(stats.totalUsers)} />
        <StatRow icon={UserCheck} label="آنلاین" value={formatCount(stats.onlineUsers)} />
        <StatRow icon={UserX} label="انقضا شده" value={formatCount(stats.expiredUsers)} />
        <StatRow icon={UserX} label="اتمام حجم" value={formatCount(stats.volumeExhaustedUsers)} />
      </div>

      <div className="space-y-1.5 border-t pt-2" style={{ borderColor: 'var(--border)' }}>
        <p className="text-[10px] font-medium uppercase tracking-wide text-[var(--text-muted)]">ترافیک</p>
        <StatRow
          icon={ArrowDownUp}
          label="آپلود / دانلود"
          value={`↑ ${formatBytes(stats.netUpBytes)}  ↓ ${formatBytes(stats.netDownBytes)}`}
        />
      </div>

      <div className="space-y-1.5 border-t pt-2" style={{ borderColor: 'var(--border)' }}>
        <p className="text-[10px] font-medium uppercase tracking-wide text-[var(--text-muted)]">سرور</p>
        {stats.version ? <StatRow icon={HardDrive} label="نسخه" value={stats.version} /> : null}
        {stats.cpuPercent != null ? <StatRow icon={Cpu} label="CPU" value={`${stats.cpuPercent}%`} /> : null}
        {stats.memPercent != null ? (
          <StatRow
            icon={HardDrive}
            label="RAM"
            value={`${stats.memPercent}% (${formatBytes(stats.memUsedBytes)} / ${formatBytes(stats.memTotalBytes)})`}
          />
        ) : null}
        {isXui && stats.xrayState ? <StatRow icon={Wifi} label="Xray" value={stats.xrayState} /> : null}
        {isXui && stats.tcpCount != null ? <StatRow icon={Activity} label="TCP" value={formatCount(stats.tcpCount)} /> : null}
      </div>
    </div>
  );
}
