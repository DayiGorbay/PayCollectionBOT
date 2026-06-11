import { FormEvent, useState } from 'react';
import { motion } from 'framer-motion';
import { Eye, EyeOff, Lock, User } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import BrandLogo from '../components/BrandLogo';
import { BRAND_NAME } from '../config/brand';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from || '/dashboard';

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');

    const trimmedUser = username.trim();
    if (!trimmedUser || !password) {
      setError('نام کاربری و رمز عبور الزامی است.');
      return;
    }

    if (password.length < 6) {
      setError('رمز عبور باید حداقل ۶ کاراکتر باشد.');
      return;
    }

    setLoading(true);
    try {
      await login({ username: trimmedUser, password, remember });
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'ورود ناموفق بود.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10" style={{ background: 'var(--bg-base)' }}>
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="mb-8 flex flex-col items-center text-center">
          <BrandLogo size={56} className="mb-4 justify-center" />
          <h1 className="text-2xl font-bold sm:text-3xl">{BRAND_NAME}</h1>
          <p className="mt-2 text-sm text-[var(--text-muted)]">ورود به پنل مدیریت</p>
        </div>

        <form onSubmit={handleSubmit} className="surface-card space-y-5 p-6 sm:p-8" noValidate>
          {error ? (
            <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-400" role="alert">
              {error}
            </div>
          ) : null}

          <div>
            <label htmlFor="username" className="mb-2 block text-sm text-[var(--text-muted)]">
              نام کاربری
            </label>
            <div className="relative">
              <User className="pointer-events-none absolute right-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-muted)]" />
              <input
                id="username"
                type="text"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="input-field pr-11"
                disabled={loading}
              />
            </div>
          </div>

          <div>
            <label htmlFor="password" className="mb-2 block text-sm text-[var(--text-muted)]">
              رمز عبور
            </label>
            <div className="relative">
              <Lock className="pointer-events-none absolute right-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-muted)]" />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-field pl-12 pr-11"
                disabled={loading}
              />
              <button
                type="button"
                className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]"
                onClick={() => setShowPassword((v) => !v)}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          <label className="flex cursor-pointer items-center gap-2 text-sm text-[var(--text-muted)]">
            <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} disabled={loading} />
            مرا به خاطر بسپار
          </label>

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? 'در حال ورود...' : 'ورود به پنل'}
          </button>
        </form>
      </motion.div>
    </div>
  );
}
