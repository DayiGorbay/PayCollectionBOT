import { useCallback, useEffect, useRef, useState } from 'react';
import { Plus, Wifi } from 'lucide-react';
import { createPanel, fetchPanels, fetchPanelsStats, testPanelById, testPanelConnection } from '../services/api';
import { getApiErrorMessage } from '../services/apiClient';
import { ROUTE_META } from '../config/navigation';
import StatusBadge from '../components/StatusBadge';
import PanelFormModal from '../components/PanelFormModal';
import PanelStatsBlock from '../components/PanelStatsBlock';
import { useAppContext } from '../context/AppContext';
import type { PanelCreatePayload, PanelStats } from '../types/api';

const STATS_POLL_MS = 5000;

export default function PanelsPage() {
  const { addToast } = useAppContext();
  const [panels, setPanels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testingId, setTestingId] = useState<number | null>(null);
  const [statsMap, setStatsMap] = useState<Record<number, PanelStats>>({});
  const [statsLoading, setStatsLoading] = useState(false);
  const meta = ROUTE_META['/panels'];
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    fetchPanels()
      .then((data) => setPanels(data))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const refreshStats = useCallback(async () => {
    if (panels.length === 0) return;
    setStatsLoading(true);
    try {
      const list: PanelStats[] = await fetchPanelsStats();
      const next: Record<number, PanelStats> = {};
      for (const item of list) {
        next[item.panelId] = item;
      }
      setStatsMap(next);
    } catch {
      /* keep previous stats on transient errors */
    } finally {
      setStatsLoading(false);
    }
  }, [panels.length]);

  useEffect(() => {
    if (panels.length === 0) {
      setStatsMap({});
      return undefined;
    }

    refreshStats();
    pollRef.current = setInterval(refreshStats, STATS_POLL_MS);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [panels, refreshStats]);

  const handleCreate = async (payload: PanelCreatePayload) => {
    try {
      const created = await createPanel(payload);
      setPanels((prev) => [created, ...prev]);
      addToast({ title: 'پنل جدید', description: payload.name, variant: 'success' });
      setModalOpen(false);
    } catch (error) {
      addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' });
    }
  };

  const handleTestNew = async (payload: PanelCreatePayload) => {
    setTesting(true);
    try {
      const result = await testPanelConnection(payload);
      addToast({
        title: result.ok ? 'اتصال موفق' : 'اتصال ناموفق',
        description: result.message,
        variant: result.ok ? 'success' : 'error',
      });
    } catch (error) {
      addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' });
    } finally {
      setTesting(false);
    }
  };

  const handleTestExisting = async (panelId: number) => {
    setTestingId(panelId);
    try {
      const result = await testPanelById(panelId);
      addToast({
        title: result.ok ? 'اتصال موفق' : 'اتصال ناموفق',
        description: result.message,
        variant: result.ok ? 'success' : 'error',
      });
      load();
    } catch (error) {
      addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' });
    } finally {
      setTestingId(null);
    }
  };

  return (
    <div className="space-y-5 sm:space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold sm:text-3xl">{meta.title}</h1>
          {meta.subtitle ? <p className="mt-2 text-sm text-[var(--text-muted)]">{meta.subtitle}</p> : null}
        </div>
        <button
          type="button"
          className="btn-primary inline-flex items-center justify-center gap-2"
          onClick={() => setModalOpen(true)}
        >
          <Plus className="h-4 w-4" />
          پنل جدید
        </button>
      </div>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {loading
          ? Array.from({ length: 3 }).map((_, index) => (
              <div key={index} className="surface-card h-52 animate-pulse" />
            ))
          : panels.map((panel) => (
              <div key={panel.id} className="surface-card p-5 sm:p-6">
                <div className="mb-4 flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs text-[var(--text-muted)]">{panel.type}</p>
                    <h3 className="mt-1 text-lg font-semibold">{panel.name}</h3>
                    <p className="mt-1 font-mono text-xs text-[var(--text-muted)]">{panel.codePanel ?? panel.code_panel}</p>
                  </div>
                  <StatusBadge label={panel.status} variant={panel.status === 'فعال' ? 'success' : 'warning'} />
                </div>
                <div className="space-y-2 text-sm text-[var(--text-muted)]">
                  <div className="rounded-xl px-3 py-2.5" style={{ background: 'var(--bg-muted)' }}>
                    URL: <span className="break-all text-[var(--text-primary)]">{panel.api}</span>
                  </div>
                  {panel.inboundId != null ? (
                    <div className="rounded-xl px-3 py-2.5" style={{ background: 'var(--bg-muted)' }}>
                      Inbound ID: <span className="text-[var(--text-primary)]">{panel.inboundId}</span>
                    </div>
                  ) : null}
                  {panel.authMode ? (
                    <div className="rounded-xl px-3 py-2.5" style={{ background: 'var(--bg-muted)' }}>
                      احراز: {panel.authMode}
                      {panel.apiTokenSet ? ' (توکن ثبت شده)' : ''}
                    </div>
                  ) : null}
                  <div className="rounded-xl px-3 py-2.5" style={{ background: 'var(--bg-muted)' }}>
                    آخرین سینک: {panel.lastSync}
                  </div>
                </div>
                <PanelStatsBlock stats={statsMap[panel.id]} loading={statsLoading && !statsMap[panel.id]} />
                <button
                  type="button"
                  className="btn-ghost mt-4 inline-flex w-full items-center justify-center gap-2"
                  disabled={testingId === panel.id}
                  onClick={() => handleTestExisting(panel.id)}
                >
                  <Wifi className="h-4 w-4" />
                  {testingId === panel.id ? 'در حال تست...' : 'تست اتصال'}
                </button>
              </div>
            ))}
      </section>

      {!loading && panels.length === 0 ? (
        <p className="text-center text-sm text-[var(--text-muted)]">هنوز پنلی ثبت نشده است.</p>
      ) : null}

      <PanelFormModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleCreate}
        onTest={handleTestNew}
        testing={testing}
      />
    </div>
  );
}
