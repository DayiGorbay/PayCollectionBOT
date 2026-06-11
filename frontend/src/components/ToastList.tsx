import { motion, AnimatePresence } from 'framer-motion';
import { useAppContext } from '../context/AppContext';

const variantStyles = {
  success: 'bg-emerald-500/10 border-emerald-400/30 text-emerald-200',
  error: 'bg-rose-500/10 border-rose-400/30 text-rose-200',
  info: 'bg-sky-500/10 border-sky-400/30 text-sky-200',
};

export default function ToastList() {
  const { toastItems, removeToast } = useAppContext();

  return (
    <div className="fixed bottom-4 left-3 right-3 z-50 flex flex-col gap-3 sm:left-4 sm:right-auto sm:max-w-sm">
      <AnimatePresence>
        {toastItems.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.25 }}
            className={`flex min-w-[260px] flex-col gap-2 rounded-3xl border p-4 shadow-soft ${variantStyles[toast.variant ?? 'info']}`}
          >
            <div className="flex items-center justify-between gap-2 text-sm font-semibold">
              <span>{toast.title}</span>
              <button type="button" onClick={() => removeToast(toast.id)} className="text-white/50 hover:text-white">
                ×
              </button>
            </div>
            <p className="text-sm text-white/80">{toast.description}</p>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
