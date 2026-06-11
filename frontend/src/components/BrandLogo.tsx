import { BRAND_LOGO_URL, BRAND_NAME } from '../config/brand';

type BrandLogoProps = {
  size?: number;
  alt?: string;
  className?: string;
  withName?: boolean;
  nameClassName?: string;
};

export default function BrandLogo({
  size = 40,
  alt = BRAND_NAME,
  className = '',
  withName = false,
  nameClassName = 'text-lg font-semibold',
}: BrandLogoProps) {
  const logoMark = (
    <div
      className={`inline-flex shrink-0 items-center justify-center ${withName ? '' : className}`}
      style={{ width: size, height: size }}
      title={alt}
    >
      <div
        className="brand-logo-gradient"
        style={{
          width: size,
          height: size,
          background: `linear-gradient(145deg, var(--accent) 0%, color-mix(in srgb, var(--accent) 45%, #fff) 50%, var(--accent-soft) 100%)`,
          WebkitMaskImage: `url("${BRAND_LOGO_URL}")`,
          maskImage: `url("${BRAND_LOGO_URL}")`,
          WebkitMaskSize: 'contain',
          maskSize: 'contain',
          WebkitMaskRepeat: 'no-repeat',
          maskRepeat: 'no-repeat',
          WebkitMaskPosition: 'center',
          maskPosition: 'center',
        }}
        role="img"
        aria-label={alt}
      />
    </div>
  );

  if (!withName) {
    return logoMark;
  }

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {logoMark}
      <span className={nameClassName} style={{ color: 'var(--text-primary)' }}>
        {BRAND_NAME}
      </span>
    </div>
  );
}
