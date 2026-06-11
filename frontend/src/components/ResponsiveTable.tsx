import { ReactNode } from 'react';

type ResponsiveTableProps = {
  children: ReactNode;
  minWidth?: string;
};

export default function ResponsiveTable({ children, minWidth = '640px' }: ResponsiveTableProps) {
  return (
    <div className="-mx-4 overflow-x-auto px-4 sm:mx-0 sm:px-0">
      <div className="inline-block min-w-full align-middle" style={{ minWidth }}>
        {children}
      </div>
    </div>
  );
}
