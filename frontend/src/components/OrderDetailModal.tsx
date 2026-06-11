import { useCallback, useEffect, useState } from 'react';
import { X, Check, Ban, Loader2 } from 'lucide-react';
import StatusBadge from './StatusBadge';
import {
  approveOrder,
  fetchOrderDetail,
  fetchOrderReceiptBlob,
  rejectOrder,
  type OrderDetail,
} from '../services/api';
import { getApiErrorMessage } from '../services/apiClient';
import { useAppContext } from '../context/AppContext';

type Props = {
  orderId: number | null;
  onClose: () => void;
  onUpdated: () => void;
};

export default function OrderDetailModal({ orderId, onClose, onUpdated }: Props) {
  const { addToast } = useAppContext();
  const [detail, setDetail] = useState<OrderDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [acting, setActing] = useState(false);
  const [receiptUrl, setReceiptUrl] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (orderId == null) return;
    setLoading(true);
    try {
      const data = await fetchOrderDetail(orderId);
      setDetail(data);
      if (data.hasReceipt) {
        const blobUrl = await fetchOrderReceiptBlob(orderId);
        setReceiptUrl((prev) => {
          if (prev) URL.revokeObjectURL(prev);
          return blobUrl;
        });
      } else {
        setReceiptUrl(null);
      }
    } catch (error) {
      addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' });
      onClose();
    } finally {
      setLoading(false);
    }
  }, [orderId, addToast, onClose]);

  useEffect(() => {
    if (orderId != null) load();
  }, [orderId, load]);

  useEffect(() => {
    return () => {
      if (receiptUrl) URL.revokeObjectURL(receiptUrl);
    };
  }, [receiptUrl]);

  const handleApprove = async () => {
    if (!orderId) return;
    setActing(true);
    try {
      await approveOrder(orderId);
      addToast({ title: 'تأیید شد', description: `سفارش #${orderId} تأیید شد.`, variant: 'success' });
      onUpdated();
      onClose();
    } catch (error) {
      addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' });
    } finally {
      setActing(false);
    }
  };

  const handleReject = async () => {
    if (!orderId) return;
    if (!window.confirm('سفارش رد و حذف شود؟ به کاربر در تلگرام اطلاع داده می‌شود.')) return;
    setActing(true);
    try {
      await rejectOrder(orderId);
      addToast({ title: 'رد شد', description: `سفارش #${orderId} حذف شد.`, variant: 'info' });
      onUpdated();
      onClose();
    } catch (error) {
      addToast({ title: 'خطا', description: getApiErrorMessage(error), variant: 'error' });
    } finally {
      setActing(false);
    }
  };

  if (orderId == null) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center p-0 sm:items-center sm:p-4">
      <button type="button" className="absolute inset-0 bg-black/60" aria-label="بستن" onClick={onClose} />
      <div
        className="relative z-10 flex max-h-[92vh] w-full max-w-lg flex-col overflow-hidden rounded-t-3xl border sm:rounded-3xl"
        style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}
      >
        <div
          className="flex items-center justify-between gap-3 border-b px-5 py-4"
          style={{ borderColor: 'var(--border)' }}
        >
          <h2 className="text-lg font-semibold">سفارش #{orderId}</h2>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="بستن">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5">
          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-[var(--accent)]" />
            </div>
          ) : detail ? (
            <div className="space-y-4 text-sm">
              <div className="flex items-center justify-between gap-2">
                <StatusBadge
                  label={detail.status}
                  variant={
                    detail.status === 'در انتظار' ? 'warning' : detail.status === 'موفق' ? 'success' : 'danger'
                  }
                />
                <span className="text-[var(--text-muted)]">{detail.orderType}</span>
              </div>
              <dl className="grid gap-2">
                <div className="flex justify-between gap-3">
                  <dt className="text-[var(--text-muted)]">کاربر</dt>
                  <dd className="font-medium">{detail.user}</dd>
                </div>
                <div className="flex justify-between gap-3">
                  <dt className="text-[var(--text-muted)]">سرویس</dt>
                  <dd className="text-left font-medium">{detail.product}</dd>
                </div>
                <div className="flex justify-between gap-3">
                  <dt className="text-[var(--text-muted)]">مبلغ</dt>
                  <dd className="font-medium">{detail.amount}</dd>
                </div>
                <div className="flex justify-between gap-3">
                  <dt className="text-[var(--text-muted)]">روش</dt>
                  <dd>{detail.method}</dd>
                </div>
                <div className="flex justify-between gap-3">
                  <dt className="text-[var(--text-muted)]">تاریخ</dt>
                  <dd>{detail.date}</dd>
                </div>
                <div className="flex justify-between gap-3">
                  <dt className="text-[var(--text-muted)]">آیدی تلگرام</dt>
                  <dd className="font-mono text-xs">{detail.telegramUserId}</dd>
                </div>
              </dl>

              {receiptUrl ? (
                <div>
                  <p className="mb-2 text-[var(--text-muted)]">رسید پرداخت</p>
                  <img
                    src={receiptUrl}
                    alt="رسید"
                    className="max-h-64 w-full rounded-xl border object-contain"
                    style={{ borderColor: 'var(--border)' }}
                  />
                </div>
              ) : (
                <p className="rounded-xl border p-3 text-[var(--text-muted)]" style={{ borderColor: 'var(--border)' }}>
                  رسید هنوز ارسال نشده است.
                </p>
              )}
            </div>
          ) : null}
        </div>

        {detail?.status === 'در انتظار' && detail.hasReceipt ? (
          <div
            className="flex flex-col gap-2 border-t p-4 sm:flex-row-reverse sm:justify-start"
            style={{ borderColor: 'var(--border)' }}
          >
            <button
              type="button"
              className="btn-primary inline-flex items-center justify-center gap-2"
              disabled={acting}
              onClick={handleApprove}
            >
              <Check className="h-4 w-4" />
              تأیید
            </button>
            <button
              type="button"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-rose-500/30 px-4 py-2.5 text-sm text-rose-300 transition hover:bg-rose-500/10"
              disabled={acting}
              onClick={handleReject}
            >
              <Ban className="h-4 w-4" />
              رد و حذف
            </button>
          </div>
        ) : null}
      </div>
    </div>
  );
}
