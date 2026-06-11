import { motion } from 'framer-motion';
import AppRoutes from './routes/AppRoutes';
import ToastList from './components/ToastList';

function App() {
  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-base)', color: 'var(--text-primary)' }}>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
        <AppRoutes />
      </motion.div>
      <ToastList />
    </div>
  );
}

export default App;
