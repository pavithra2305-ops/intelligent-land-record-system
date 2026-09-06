import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Copy } from 'lucide-react';

export const ValidationBadge = ({ status = 'VALID' }) => {
  const normalized = status.toUpperCase();

  switch (normalized) {
    case 'VALID':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-success-50 text-success-600 border border-success-500/20">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>✓ Valid</span>
        </span>
      );
    case 'WARNING':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-warning-50 text-warning-600 border border-warning-500/20">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>⚠ Needs Review</span>
        </span>
      );
    case 'INVALID':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-error-50 text-error-600 border border-error-500/20">
          <XCircle className="w-3.5 h-3.5" />
          <span>✕ Invalid</span>
        </span>
      );
    case 'DUPLICATE':
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-purple-50 text-purple-700 border border-purple-300">
          <Copy className="w-3.5 h-3.5" />
          <span>Potential Duplicate</span>
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-300">
          {status}
        </span>
      );
  }
};
