export type PanelThemeId =
  | 'pure-black'
  | 'warm-sunset'
  | 'green-emerald'
  | 'dream-purple'
  | 'blue-sea'
  | 'lavender'
  | 'green-mint'
  | 'cream-paper'
  | 'bright-white';

export type ThemePalette = {
  bgBase: string;
  bgSidebar: string;
  bgCard: string;
  bgMuted: string;
  bgInput: string;
  textPrimary: string;
  textMuted: string;
  border: string;
  accent: string;
  accentSoft: string;
  headerBg: string;
  navActiveBg: string;
  navHoverBg: string;
  logoBg: string;
  logoBorder: string;
  logoGlow: string;
};

export type PanelTheme = {
  id: PanelThemeId;
  title: string;
  subtitle: string;
  colors: [string, string, string];
  dark: ThemePalette;
  light: ThemePalette;
};

function palette(
  accent: string,
  c1: string,
  c2: string,
  c3: string,
  isLightBase: boolean,
): ThemePalette {
  if (isLightBase) {
    return {
      bgBase: c3,
      bgSidebar: '#ffffff',
      bgCard: '#ffffff',
      bgMuted: c2,
      bgInput: '#ffffff',
      textPrimary: '#111827',
      textMuted: '#6b7280',
      border: 'rgba(0,0,0,0.08)',
      accent,
      accentSoft: `${accent}22`,
      headerBg: 'rgba(255,255,255,0.92)',
      navActiveBg: c2,
      navHoverBg: c2,
      logoBg: `linear-gradient(135deg, ${c1} 0%, ${accent} 100%)`,
      logoBorder: `${accent}44`,
      logoGlow: `0 0 20px ${accent}33`,
    };
  }
  return {
    bgBase: c3,
    bgSidebar: c2,
    bgCard: c1,
    bgMuted: c2,
    bgInput: c3,
    textPrimary: '#f5f5f5',
    textMuted: '#9ca3af',
    border: 'rgba(255,255,255,0.08)',
    accent,
    accentSoft: `${accent}28`,
    headerBg: `${c3}f2`,
    navActiveBg: `color-mix(in srgb, ${accent} 22%, ${c1})`,
    navHoverBg: `color-mix(in srgb, ${accent} 10%, ${c2})`,
    logoBg: `linear-gradient(135deg, ${c1} 0%, ${accent} 100%)`,
    logoBorder: `${accent}55`,
    logoGlow: `0 0 24px ${accent}40`,
  };
}

export const PANEL_THEMES: PanelTheme[] = [
  {
    id: 'pure-black',
    title: 'مشکی خالص',
    subtitle: 'برگه — مینیمال',
    colors: ['#141823', '#0c121e', '#3ecf8e'],
    dark: palette('#3ecf8e', '#1a1f2e', '#0d0f14', '#08080c', false),
    light: palette('#059669', '#e8fff3', '#f4f4f5', '#fafafa', true),
  },
  {
    id: 'warm-sunset',
    title: 'غروب گرم',
    subtitle: 'گرم — پرانرژی',
    colors: ['#f67e24', '#4f1e09', '#20120d'],
    dark: palette('#f67e24', '#3d2210', '#20120d', '#140c08', false),
    light: palette('#ea580c', '#fff4eb', '#fef3e2', '#fffaf5', true),
  },
  {
    id: 'green-emerald',
    title: 'زمرد سبز',
    subtitle: 'طبیعی — آرام',
    colors: ['#1f4f3d', '#2b6a4f', '#0b1f14'],
    dark: palette('#2b6a4f', '#1f4f3d', '#0f281c', '#0b1f14', false),
    light: palette('#047857', '#ecfdf5', '#d1fae5', '#f0fdf9', true),
  },
  {
    id: 'dream-purple',
    title: 'رویا بنفش',
    subtitle: 'پررنگ — مدرن',
    colors: ['#8b5cf6', '#2f2c7b', '#0f1220'],
    dark: palette('#8b5cf6', '#2f2c7b', '#17142e', '#0f1220', false),
    light: palette('#7c3aed', '#f3eeff', '#ede9fe', '#faf8ff', true),
  },
  {
    id: 'blue-sea',
    title: 'دریای آبی',
    subtitle: 'پایدار — حرفه‌ای',
    colors: ['#1982d1', '#0779e4', '#0c1736'],
    dark: palette('#1982d1', '#0c2d52', '#0c1736', '#081020', false),
    light: palette('#0284c7', '#eff8ff', '#dbeafe', '#f8fbff', true),
  },
  {
    id: 'lavender',
    title: 'اسطوخودوس',
    subtitle: 'نرم — دلنشین',
    colors: ['#c4b5fd', '#ede9fe', '#fafafa'],
    dark: palette('#a78bfa', '#2e2640', '#1a1528', '#12101c', false),
    light: palette('#7c3aed', '#f5f3ff', '#ede9fe', '#fafafa', true),
  },
  {
    id: 'green-mint',
    title: 'سبز نعنایی',
    subtitle: 'تازه — طبیعی',
    colors: ['#6ee7b7', '#d1fae5', '#f8fafc'],
    dark: palette('#34d399', '#134e3a', '#0c2e22', '#071a14', false),
    light: palette('#059669', '#ecfdf5', '#d1fae5', '#f8fafc', true),
  },
  {
    id: 'cream-paper',
    title: 'کاغذ کرمی',
    subtitle: 'گرم — دنج',
    colors: ['#d6b47c', '#f5e4c0', '#faf8f5'],
    dark: palette('#d6b47c', '#3d3020', '#221c14', '#14110d', false),
    light: palette('#b45309', '#fff8eb', '#f5e4c0', '#faf8f5', true),
  },
  {
    id: 'bright-white',
    title: 'سفید روشن',
    subtitle: 'تمیز — مدرن',
    colors: ['#e5e7eb', '#f9fafb', '#ffffff'],
    dark: palette('#e5e7eb', '#27272a', '#18181b', '#09090b', false),
    light: palette('#111827', '#f3f4f6', '#f9fafb', '#ffffff', true),
  },
];

export const DEFAULT_PANEL_THEME: PanelThemeId = 'pure-black';

export function getPanelTheme(id: PanelThemeId) {
  return PANEL_THEMES.find((t) => t.id === id) ?? PANEL_THEMES[0];
}

export function getActivePalette(theme: PanelTheme, colorMode: 'dark' | 'light') {
  return colorMode === 'dark' ? theme.dark : theme.light;
}
