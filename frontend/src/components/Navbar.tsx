import { Link, useLocation } from 'react-router-dom';
import { LogOut, Menu, Moon, Settings, Sun } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import { useAuth } from '../context/AuthContext';
import { PANEL_NAME, ROUTE_META } from '../config/navigation';

type NavbarProps = {
  onMenuClick?: () => void;
};

export default function Navbar({ onMenuClick }: NavbarProps) {
  const { colorMode, toggleColorMode } = useAppContext();
  const { logout } = useAuth();
  const location = useLocation();

  const meta = ROUTE_META[location.pathname] ?? { title: 'پنل' };
  const breadcrumb = `${PANEL_NAME} / ${meta.title}`;

  const handleLogout = async () => {
    await logout();
    window.location.href = '/login';
  };

  return (
    <header
      className="shrink-0 border-b backdrop-blur-md"
      style={{ borderColor: 'var(--border)', background: 'var(--header-bg)' }}
    >
      <div className="flex items-center justify-between gap-3 px-3 py-3 sm:px-5 sm:py-4">
        <div className="flex min-w-0 flex-1 items-center gap-2 sm:gap-3">
          <button type="button" className="icon-btn lg:hidden" onClick={onMenuClick} aria-label="منو">
            <Menu className="h-5 w-5" />
          </button>
          <div className="min-w-0 text-right">
            <p className="truncate text-xs text-[var(--text-muted)]">{breadcrumb}</p>
            <h2 className="truncate text-base font-semibold sm:text-lg">{meta.title}</h2>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <button
            type="button"
            className="icon-btn"
            onClick={toggleColorMode}
            aria-label={colorMode === 'dark' ? 'تم روشن' : 'تم تیره'}
            title={colorMode === 'dark' ? 'تم روشن' : 'تم تیره'}
          >
            {colorMode === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>

          <Link to="/settings" className="icon-btn" aria-label="تنظیمات" title="تنظیمات">
            <Settings className="h-5 w-5" />
          </Link>

          <button type="button" className="icon-btn" onClick={handleLogout} aria-label="خروج" title="خروج">
            <LogOut className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  );
}
