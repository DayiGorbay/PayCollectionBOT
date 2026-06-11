import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { DEFAULT_PANEL_THEME, PANEL_THEMES, type PanelThemeId, getActivePalette, getPanelTheme } from '../config/panelThemes';
import { applyThemePalette } from '../utils/applyThemePalette';

export type ColorMode = 'dark' | 'light';

type ToastItem = {
  id: string;
  title: string;
  description: string;
  variant?: 'success' | 'error' | 'info';
};

type AppContextValue = {
  colorMode: ColorMode;
  panelThemeId: PanelThemeId;
  sidebarOpen: boolean;
  toastItems: ToastItem[];
  toggleColorMode: () => void;
  setColorMode: (mode: ColorMode) => void;
  setPanelThemeId: (id: PanelThemeId) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  addToast: (toast: Omit<ToastItem, 'id'>) => void;
  removeToast: (id: string) => void;
};

const AppContext = createContext<AppContextValue | undefined>(undefined);

const COLOR_MODE_KEY = 'pc_color_mode';
const PANEL_THEME_KEY = 'pc_panel_theme';

function readColorMode(): ColorMode {
  const stored = localStorage.getItem(COLOR_MODE_KEY);
  return stored === 'light' ? 'light' : 'dark';
}

function readPanelTheme(): PanelThemeId {
  const stored = localStorage.getItem(PANEL_THEME_KEY) as PanelThemeId | null;
  if (stored && PANEL_THEMES.some((t) => t.id === stored)) return stored;
  return DEFAULT_PANEL_THEME;
}

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [colorMode, setColorModeState] = useState<ColorMode>(readColorMode);
  const [panelThemeId, setPanelThemeIdState] = useState<PanelThemeId>(readPanelTheme);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [toastItems, setToastItems] = useState<ToastItem[]>([]);

  useEffect(() => {
    const theme = getPanelTheme(panelThemeId);
    const palette = getActivePalette(theme, colorMode);
    applyThemePalette(palette);
    document.documentElement.setAttribute('data-color-mode', colorMode);
    document.documentElement.setAttribute('data-panel-theme', panelThemeId);
    localStorage.setItem(COLOR_MODE_KEY, colorMode);
    localStorage.setItem(PANEL_THEME_KEY, panelThemeId);
  }, [colorMode, panelThemeId]);

  const toggleSidebar = () => setSidebarOpen((state) => !state);

  const removeToast = (id: string) => {
    setToastItems((current) => current.filter((item) => item.id !== id));
  };

  const addToast = (toast: Omit<ToastItem, 'id'>) => {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    setToastItems((current) => [{ id, ...toast }, ...current].slice(0, 4));
    window.setTimeout(() => removeToast(id), 4200);
  };

  const setColorMode = (mode: ColorMode) => setColorModeState(mode);

  const toggleColorMode = () => setColorModeState((m) => (m === 'dark' ? 'light' : 'dark'));

  const setPanelThemeId = (id: PanelThemeId) => {
    setPanelThemeIdState(id);
  };

  const value = useMemo(
    () => ({
      colorMode,
      panelThemeId,
      sidebarOpen,
      toggleColorMode,
      setColorMode,
      setPanelThemeId,
      toggleSidebar,
      setSidebarOpen,
      toastItems,
      addToast,
      removeToast,
    }),
    [colorMode, panelThemeId, sidebarOpen, toastItems],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext باید داخل AppProvider استفاده شود.');
  }
  return context;
}
