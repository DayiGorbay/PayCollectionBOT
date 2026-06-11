import { AnimatePresence, motion } from 'framer-motion';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { LogOut, Settings, X } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import { useAuth } from '../context/AuthContext';
import useMediaQuery from '../hooks/useMediaQuery';
import { NAV_SECTIONS } from '../config/navigation';
import Navbar from '../components/Navbar';
import BrandLogo from '../components/BrandLogo';

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `flex items-center gap-3 rounded-2xl border border-transparent px-4 py-3 text-sm transition-all duration-200 ${
    isActive
      ? 'nav-link-active font-medium'
      : 'text-[var(--text-muted)]'
  }`;

function DashboardLayout() {
  const { sidebarOpen, toggleSidebar, setSidebarOpen } = useAppContext();
  const { logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const isDesktop = useMediaQuery('(min-width: 1024px)');

  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  const closeSidebarOnMobile = () => {
    if (!isDesktop) setSidebarOpen(false);
  };

  return (
    <div className="h-[100dvh] overflow-hidden" style={{ background: 'var(--bg-base)' }}>
      {!isDesktop && sidebarOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          aria-label="بستن منو"
          onClick={() => setSidebarOpen(false)}
        />
      ) : null}

      <div className="flex h-full">
        <aside
          className={`fixed inset-y-0 right-0 z-40 flex h-full w-[min(280px,88vw)] shrink-0 flex-col border-l px-3 py-5 transition-transform duration-300 lg:static lg:z-auto lg:w-[260px] lg:translate-x-0 xl:w-[280px] ${
            sidebarOpen || isDesktop ? 'translate-x-0' : 'translate-x-full'
          }`}
          style={{ background: 'var(--bg-sidebar)', borderColor: 'var(--border)' }}
        >
          <div className="mb-6 flex shrink-0 items-center justify-between gap-2 px-2">
            <BrandLogo size={40} withName />
            <button type="button" className="icon-btn lg:hidden" onClick={toggleSidebar} aria-label="بستن">
              <X className="h-5 w-5" />
            </button>
          </div>

          <nav className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
            <div className="space-y-5 pb-4">
              {NAV_SECTIONS.map((section) => (
                <div key={section.title}>
                  <p className="mb-2 px-3 text-xs font-medium text-[var(--text-muted)]">{section.title}</p>
                  <div className="space-y-0.5">
                    {section.items.map((item) => {
                      const Icon = item.icon;
                      return (
                        <NavLink key={item.path} to={item.path} className={navLinkClass} onClick={closeSidebarOnMobile}>
                          <Icon className="h-[18px] w-[18px] shrink-0" />
                          <span>{item.label}</span>
                        </NavLink>
                      );
                    })}
                  </div>
                </div>
              ))}

              <div>
                <p className="mb-2 px-3 text-xs font-medium text-[var(--text-muted)]">پنل</p>
                <NavLink to="/settings" className={navLinkClass} onClick={closeSidebarOnMobile}>
                  <Settings className="h-[18px] w-[18px]" />
                  <span>تنظیمات</span>
                </NavLink>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="mt-0.5 flex w-full items-center gap-3 rounded-2xl border border-transparent px-4 py-3 text-sm text-rose-400"
                >
                  <LogOut className="h-[18px] w-[18px]" />
                  <span>خروج</span>
                </button>
              </div>
            </div>
          </nav>
        </aside>

        <div className="flex min-h-0 min-w-0 flex-1 flex-col">
          <Navbar onMenuClick={toggleSidebar} />
          <main className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
            <div className="mx-auto w-full max-w-[1320px] px-3 pb-8 pt-4 sm:px-5 lg:px-6">
              <AnimatePresence mode="wait">
                <motion.section
                  key={location.pathname}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="space-y-5 sm:space-y-6"
                >
                  <Outlet />
                </motion.section>
              </AnimatePresence>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

export default DashboardLayout;
