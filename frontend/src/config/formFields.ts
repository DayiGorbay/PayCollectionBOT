import type { FormField } from '../components/FormModal';

export const PANEL_FORM_FIELDS: FormField[] = [
  { name: 'name', label: 'نام پنل', placeholder: 'مثال: مرزبان ایران', required: true },
  { name: 'api', label: 'آدرس API', type: 'url', placeholder: 'https://api.example.com', required: true },
  {
    name: 'type',
    label: 'نوع پنل',
    type: 'select',
    required: true,
    options: [
      { value: 'VPN', label: 'VPN' },
      { value: 'Hosting', label: 'Hosting' },
      { value: 'x-ui', label: 'x-ui' },
    ],
  },
  {
    name: 'status',
    label: 'وضعیت',
    type: 'select',
    defaultValue: 'فعال',
    options: [
      { value: 'فعال', label: 'فعال' },
      { value: 'در انتظار', label: 'در انتظار' },
      { value: 'غیرفعال', label: 'غیرفعال' },
    ],
  },
];

export const PRODUCT_FORM_FIELDS: FormField[] = [
  { name: 'name', label: 'نام محصول', required: true, placeholder: 'پلن ایران 10GB' },
  { name: 'price', label: 'قیمت (تومان)', required: true, placeholder: '100000' },
  { name: 'size', label: 'حجم', required: true, placeholder: '10 GB' },
  { name: 'duration', label: 'مدت', required: true, placeholder: '30 روز' },
  { name: 'panel', label: 'پنل', placeholder: 'مرزبان' },
  { name: 'code', label: 'کد محصول', required: true, placeholder: 'IR10' },
  { name: 'category', label: 'دسته‌بندی', placeholder: 'ایران' },
];

export const DISCOUNT_FORM_FIELDS: FormField[] = [
  { name: 'code', label: 'کد تخفیف', required: true, placeholder: 'PAYCOL10' },
  { name: 'amount', label: 'مقدار تخفیف', required: true, placeholder: '10% یا 50000' },
  {
    name: 'type',
    label: 'نوع',
    type: 'select',
    required: true,
    options: [
      { value: 'درصدی', label: 'درصدی' },
      { value: 'ثابت', label: 'مبلغ ثابت' },
    ],
  },
  { name: 'maxUse', label: 'حداکثر استفاده', type: 'number', placeholder: '50' },
  { name: 'validUntil', label: 'اعتبار تا', type: 'date', required: true },
];
