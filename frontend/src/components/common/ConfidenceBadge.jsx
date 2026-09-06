import React from 'react';

export const ConfidenceBadge = ({ score = 0, level = 'LOW', showBar = false }) => {
  const percentage = Math.round(score * 100);
  
  let colorClass = 'bg-error-50 text-error-600 border-error-500/30';
  let barColor = 'bg-error-500';

  if (percentage >= 85 || level === 'HIGH') {
    colorClass = 'bg-success-50 text-success-600 border-success-500/30';
    barColor = 'bg-success-600';
  } else if (percentage >= 60 || level === 'MEDIUM') {
    colorClass = 'bg-warning-50 text-warning-600 border-warning-500/30';
    barColor = 'bg-warning-500';
  }

  return (
    <div className="inline-flex flex-col gap-1">
      <div className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-xs font-mono font-semibold ${colorClass}`}>
        <span>{percentage}%</span>
        <span className="uppercase font-sans text-[10px] tracking-wider font-bold">
          {percentage >= 85 ? 'HIGH' : percentage >= 60 ? 'MEDIUM' : 'LOW'}
        </span>
      </div>
      {showBar && (
        <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
          <div className={`h-full ${barColor} transition-all duration-500`} style={{ width: `${percentage}%` }} />
        </div>
      )}
    </div>
  );
};
