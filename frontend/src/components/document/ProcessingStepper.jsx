import React from 'react';
import { CheckCircle2, Loader2, FileUp, Sparkles, ScanText, FileSearch, Layers, ShieldCheck, Check } from 'lucide-react';
import { motion } from 'framer-motion';

export const ProcessingStepper = ({ stage = 1, status = 'COMPLETED', error = null }) => {
  const steps = [
    { id: 1, name: 'Uploaded', icon: FileUp, desc: 'File stored' },
    { id: 2, name: 'Preprocessing', icon: Sparkles, desc: 'OpenCV CLAHE & deskew' },
    { id: 3, name: 'OCR', icon: ScanText, desc: 'Text recognition' },
    { id: 4, name: 'Classification', icon: Layers, desc: 'Type identification' },
    { id: 5, name: 'Extraction', icon: FileSearch, desc: 'LLM JSON mapping' },
    { id: 6, name: 'Validation', icon: ShieldCheck, desc: 'Rule & Duplicate check' },
    { id: 7, name: 'Completed', icon: Check, desc: 'Ready for verification' }
  ];

  return (
    <div className="bg-white p-6 rounded-xl border border-border shadow-xs space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-bold text-navy-900 flex items-center gap-2">
          <span>Processing Pipeline Progress</span>
          {status === 'FAILED' && (
            <span className="text-xs px-2 py-0.5 rounded bg-error-50 text-error-600 font-mono">Failed</span>
          )}
        </h3>
        <span className="text-xs font-mono text-muted">Stage {stage} of 7</span>
      </div>

      {error && (
        <div className="p-3 bg-error-50 border border-error-200 rounded-lg text-sm text-error-600">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-7 gap-2 relative">
        {steps.map((step) => {
          const isDone = stage > step.id || status === 'COMPLETED';
          const isCurrent = stage === step.id && status !== 'COMPLETED' && status !== 'FAILED';
          const isFailed = stage === step.id && status === 'FAILED';

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`p-3 rounded-lg border text-center transition-all ${
                isDone ? 'bg-success-50/50 border-success-200 text-success-700' :
                isCurrent ? 'bg-primary-50 border-primary-500 text-primary-700 shadow-xs ring-2 ring-primary-500/20' :
                isFailed ? 'bg-error-50 border-error-300 text-error-700' :
                'bg-slate-50 border-slate-200 text-slate-400'
              }`}
            >
              <div className="flex justify-center mb-1.5">
                {isDone ? (
                  <CheckCircle2 className="w-5 h-5 text-success-600" />
                ) : isCurrent ? (
                  <Loader2 className="w-5 h-5 text-primary-600 animate-spin" />
                ) : (
                  <step.icon className="w-5 h-5" />
                )}
              </div>
              <p className="text-xs font-bold leading-snug">{step.name}</p>
              <p className="text-[10px] font-mono text-muted mt-0.5 truncate">{step.desc}</p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
