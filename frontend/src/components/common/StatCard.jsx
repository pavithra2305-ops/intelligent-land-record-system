import React from 'react';

export const StatCard = ({ title, value, icon: Icon, trend, color = 'blue' }) => {
  const colorStyles = {
    blue: 'text-primary-600 bg-primary-50 border-primary-100',
    green: 'text-success-600 bg-success-50 border-success-100',
    amber: 'text-warning-600 bg-warning-50 border-warning-100',
    red: 'text-error-600 bg-error-50 border-error-100',
    purple: 'text-purple-600 bg-purple-50 border-purple-100'
  };

  return (
    <div className="bg-white p-5 rounded-xl border border-border shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-muted">{title}</span>
        {Icon && (
          <div className={`p-2.5 rounded-lg border ${colorStyles[color]}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      
      <div className="mt-3 flex items-baseline justify-between">
        <span className="text-3xl font-bold text-navy-900 font-mono">{value}</span>
        {trend && (
          <span className="text-xs font-medium text-muted flex items-center gap-1">
            {trend}
          </span>
        )}
      </div>
    </div>
  );
};
