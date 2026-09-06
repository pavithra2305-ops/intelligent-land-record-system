import React, { createContext, useContext, useState } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Info, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const ToastContext = createContext(null);

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = (message, type = 'info', duration = 4000) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      removeToast(id);
    }, duration);
  };

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const toast = {
    success: (msg) => addToast(msg, 'success'),
    error: (msg) => addToast(msg, 'error'),
    warning: (msg) => addToast(msg, 'warning'),
    info: (msg) => addToast(msg, 'info')
  };

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
        <AnimatePresence>
          {toasts.map((t) => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, x: 50, scale: 0.9 }}
              className={`pointer-events-auto p-4 rounded-xl shadow-lg border flex items-start gap-3 text-sm font-medium ${
                t.type === 'success' ? 'bg-white border-success-500 text-navy-900' :
                t.type === 'error' ? 'bg-white border-error-500 text-navy-900' :
                t.type === 'warning' ? 'bg-white border-warning-500 text-navy-900' :
                'bg-white border-primary-500 text-navy-900'
              }`}
            >
              {t.type === 'success' && <CheckCircle2 className="w-5 h-5 text-success-600 shrink-0 mt-0.5" />}
              {t.type === 'error' && <XCircle className="w-5 h-5 text-error-600 shrink-0 mt-0.5" />}
              {t.type === 'warning' && <AlertTriangle className="w-5 h-5 text-warning-600 shrink-0 mt-0.5" />}
              {t.type === 'info' && <Info className="w-5 h-5 text-primary-600 shrink-0 mt-0.5" />}

              <div className="flex-1">{t.message}</div>
              
              <button onClick={() => removeToast(t.id)} className="text-muted hover:text-navy-900">
                <X className="w-4 h-4" />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToast must be used within a ToastProvider');
  return context;
};
