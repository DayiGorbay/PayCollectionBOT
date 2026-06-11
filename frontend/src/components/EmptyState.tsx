type EmptyStateProps = {
  title: string;
  description?: string;
};

export default function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 px-6 py-14 text-center">
      <p className="text-base font-medium text-white/80">{title}</p>
      {description ? <p className="max-w-sm text-sm text-white/50">{description}</p> : null}
    </div>
  );
}
