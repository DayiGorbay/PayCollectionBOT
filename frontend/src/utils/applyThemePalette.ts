import type { ThemePalette } from '../config/panelThemes';

const CSS_MAP: Record<keyof ThemePalette, string> = {
  bgBase: '--bg-base',
  bgSidebar: '--bg-sidebar',
  bgCard: '--bg-card',
  bgMuted: '--bg-muted',
  bgInput: '--bg-input',
  textPrimary: '--text-primary',
  textMuted: '--text-muted',
  border: '--border',
  accent: '--accent',
  accentSoft: '--accent-soft',
  headerBg: '--header-bg',
  navActiveBg: '--nav-active-bg',
  navHoverBg: '--nav-hover-bg',
  logoBg: '--logo-bg',
  logoBorder: '--logo-border',
  logoGlow: '--logo-glow',
};

export function applyThemePalette(palette: ThemePalette) {
  const root = document.documentElement;
  (Object.keys(CSS_MAP) as (keyof ThemePalette)[]).forEach((key) => {
    root.style.setProperty(CSS_MAP[key], palette[key]);
  });
}
