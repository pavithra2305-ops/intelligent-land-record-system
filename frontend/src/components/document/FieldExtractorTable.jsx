import React from 'react';
import { ConfidenceBadge } from '../common/ConfidenceBadge';
import { ValidationBadge } from '../common/ValidationBadge';

export const FieldExtractorTable = ({ fieldDetails = {} }) => {
  const fieldsConfig = [
    { key: 'owner_name', label: 'Owner Name' },
    { key: 'survey_number', label: 'Survey Number' },
    { key: 'khasra_number', label: 'Khasra Number' },
    { key: 'khata_number', label: 'Khata Number' },
    { key: 'plot_area', label: 'Plot Area' },
    { key: 'area_unit', label: 'Area Unit' },
    { key: 'village', label: 'Village' },
    { key: 'tehsil', label: 'Tehsil' },
    { key: 'district', label: 'District' },
    { key: 'land_classification', label: 'Land Classification' },
    { key: 'ownership_details', label: 'Ownership Details' },
    { key: 'mutation_number', label: 'Mutation Number' },
    { key: 'registration_number', label: 'Registration Number' }
  ];

  return (
    <div className="bg-white rounded-xl border border-border overflow-hidden shadow-xs">
      <div className="p-4 bg-slate-50 border-b border-border flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-navy-900">Extracted Land Record Fields</h3>
          <p className="text-xs text-muted">Field-level values, confidence scores & validation status</p>
        </div>
      </div>

      <div className="divide-y divide-border overflow-x-auto">
        {fieldsConfig.map((field) => {
          const detail = fieldDetails[field.key] || { value: 'N/A', confidence: 0.0, confidence_level: 'LOW', status: 'WARNING' };
          const displayVal = detail.value !== null && detail.value !== undefined ? String(detail.value) : '—';

          return (
            <div key={field.key} className="p-3.5 hover:bg-slate-50/80 transition-colors flex items-center justify-between gap-4 text-sm">
              <div className="w-1/3 font-medium text-slate-700">
                {field.label}
              </div>

              <div className="w-2/5 font-semibold text-navy-900 font-mono truncate" title={displayVal}>
                {displayVal}
              </div>

              <div className="w-1/4 flex items-center justify-end gap-3">
                <ConfidenceBadge score={detail.confidence} level={detail.confidence_level} />
                <ValidationBadge status={detail.status} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
