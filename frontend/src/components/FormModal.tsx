import { FormEvent, ReactNode, useEffect } from 'react';
import { X } from 'lucide-react';

export type FormField = {
  name: string;
  label: string;
  type?: 'text' | 'password' | 'number' | 'url' | 'date' | 'select' | 'textarea';
  placeholder?: string;
  required?: boolean;
  options?: { value: string; label: string }[];
  defaultValue?: string;
};

type FormModalProps = {
  open: boolean;
  title: string;
  description?: string;
  fields: FormField[];
  submitLabel?: string;
  onClose: () => void;
  onSubmit: (values: Record<string, string>) => void;
  footer?: ReactNode;
};

export default function FormModal({
  open,
  title,
  description,
  fields,
  submitLabel = 'ذخیره',
  onClose,
  onSubmit,
}: FormModalProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = '';
    };
  }, [open, onClose]);

  if (!open) return null;

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const values: Record<string, string> = {};
    fields.forEach((field) => {
      values[field.name] = String(form.get(field.name) ?? '');
    });
    onSubmit(values);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center p-0 sm:items-center sm:p-4">
      <button type="button" className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} aria-label="بستن" />
      <div
        className="relative z-10 flex max-h-[92vh] w-full max-w-lg flex-col overflow-hidden rounded-t-3xl border sm:rounded-3xl"
        style={{ background: 'var(--bg-card)', borderColor: 'var(--border)' }}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div className="flex items-start justify-between gap-3 border-b px-5 py-4" style={{ borderColor: 'var(--border)' }}>
          <div>
            <h2 id="modal-title" className="text-lg font-semibold">
              {title}
            </h2>
            {description ? <p className="mt-1 text-sm text-[var(--text-muted)]">{description}</p> : null}
          </div>
          <button type="button" className="icon-btn shrink-0" onClick={onClose} aria-label="بستن">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="overflow-y-auto px-5 py-4">
          <div className="space-y-4">
            {fields.map((field) => (
              <div key={field.name}>
                <label htmlFor={field.name} className="mb-2 block text-sm text-[var(--text-muted)]">
                  {field.label}
                  {field.required ? <span className="text-rose-400"> *</span> : null}
                </label>
                {field.type === 'select' ? (
                  <select
                    id={field.name}
                    name={field.name}
                    required={field.required}
                    defaultValue={field.defaultValue ?? ''}
                    className="input-field"
                  >
                    <option value="">انتخاب کنید</option>
                    {field.options?.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                ) : field.type === 'textarea' ? (
                  <textarea
                    id={field.name}
                    name={field.name}
                    rows={3}
                    required={field.required}
                    placeholder={field.placeholder}
                    defaultValue={field.defaultValue}
                    className="input-field resize-none"
                  />
                ) : (
                  <input
                    id={field.name}
                    name={field.name}
                    type={field.type ?? 'text'}
                    required={field.required}
                    placeholder={field.placeholder}
                    defaultValue={field.defaultValue}
                    className="input-field"
                  />
                )}
              </div>
            ))}
          </div>

          <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <button type="button" className="btn-ghost w-full sm:w-auto" onClick={onClose}>
              انصراف
            </button>
            <button type="submit" className="btn-primary w-full sm:w-auto">
              {submitLabel}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
