import type { LucideIcon } from 'lucide-react';
import {
  Grid,
  User,
  Package,
  ShoppingCart,
  CreditCard,
  Layers,
  Ticket,
  Settings,
} from 'lucide-react';

export type NavItem = {
  label: string;
  path: string;
  icon: LucideIcon;
};

export type NavSection = {
  title: string;
  items: NavItem[];
};

export const NAV_SECTIONS: NavSection[] = [
  {
    title: 'عمومی',
    items: [{ label: 'داشبورد', path: '/dashboard', icon: Grid }],
  },
  {
    title: 'مدیریت',
    items: [
      { label: 'کاربران', path: '/users', icon: User },
      { label: 'سفارشات', path: '/orders', icon: ShoppingCart },
      { label: 'محصولات', path: '/products', icon: Package },
      { label: 'تراکنش‌ها', path: '/transactions', icon: CreditCard },
      { label: 'پنل‌ها', path: '/panels', icon: Layers },
    ],
  },
  {
    title: 'ابزارها',
    items: [{ label: 'کدهای تخفیف', path: '/discounts', icon: Ticket }],
  },
];

export const ROUTE_META: Record<string, { title: string; subtitle?: string }> = {
  '/dashboard': { title: 'داشبورد', subtitle: 'نمای کلی پنل و عملکرد ربات' },
  '/users': { title: 'کاربران', subtitle: 'مدیریت کاربران و پلن‌های فعال' },
  '/orders': { title: 'سفارشات', subtitle: 'سفارش‌هایی که نیاز به انجام دارند' },
  '/products': { title: 'محصولات', subtitle: 'فهرست محصولات قابل فروش و مدیریت آن‌ها' },
  '/transactions': { title: 'تراکنش‌ها', subtitle: 'گزارش تمام تراکنش‌های مالی پنل' },
  '/panels': { title: 'پنل‌ها', subtitle: 'مدیریت API پنل‌ها و اتصال سرویس‌ها' },
  '/discounts': { title: 'کدهای تخفیف', subtitle: 'تعریف و مدیریت کدهای تخفیف' },
  '/settings': { title: 'تنظیمات', subtitle: 'رنگ‌بندی، اطلاعات پنل و امنیت حساب' },
};

export { BRAND_NAME as PANEL_NAME } from './brand';
