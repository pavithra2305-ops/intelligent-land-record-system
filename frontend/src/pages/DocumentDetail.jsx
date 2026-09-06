import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  FileText, ArrowLeft, CheckCircle2, AlertTriangle, ShieldAlert,
  Sparkles, CheckSquare, AlertCircle, MapPin, Database, Layers,
  ChevronDown, ChevronUp, FileCode
} from 'lucide-react';
import api from '../services/api';
import { DocumentViewer } from '../components/document/DocumentViewer';
import { FieldExtractorTable } from '../components/document/FieldExtractorTable';
import { ConfidenceBadge } from '../components/common/ConfidenceBadge';
import { ValidationBadge } from '../components/common/ValidationBadge';
import { ParcelMap } from '../components/gis/ParcelMap';

export const DocumentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [document, setDocument] = useState(null);
  const [extraction, setExtraction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showRawOcr, setShowRawOcr] = useState(false);
  const [masterParcels, setMasterParcels] = useState([]);

  useEffect(() => {
    fetchDocumentData();
  }, [id]);

  const fetchDocumentData = async () => {
    setLoading(true);
    setDocument(null);
    setExtraction(null);

    try {
      const docRes = await api.get(`/documents/${id}`);
      setDocument(docRes.data);

      try {
        const extRes = await api.get(`/documents/${id}/extraction`);
        if (extRes.data && Number(extRes.data.document_id) === Number(id)) {
          setExtraction(extRes.data);
        }
      } catch (extErr) {
        console.warn(`[EXTRACTION NOTICE] No extraction result available for doc #${id}:`, extErr);
      }

      try {
        const gisRes = await api.get('/gis/parcels');
        setMasterParcels(gisRes.data);
      } catch (gisErr) {
        console.warn("Could not load GIS master parcels:", gisErr);
      }
    } catch (err) {
      console.error(`Failed to load document detail #${id}`, err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  if (!document) {
    return (
      <div className="p-12 text-center text-muted">
        <p className="text-base font-bold text-navy-900">Document #{id} not found</p>
      </div>
    );
  }

  const validation = extraction?.validation || {};
  const fieldComp = validation.field_comparison_details || {};
  const masterMatchStatus = validation.master_match_status || 'NOT_FOUND';
  const gisMatchStatus = validation.gis_match_status || 'GIS_NOT_FOUND';
  const duplicateStatus = validation.duplicate_status || 'NO_DUPLICATE';

  // Find matching parcel geometry from master parcels
  const extractedSurvey = extraction?.extracted_fields?.survey_number;
  const extractedVillage = extraction?.extracted_fields?.village;
  const matchingParcel = masterParcels.find(p =>
    p.survey_number && extractedSurvey && p.survey_number.toLowerCase().trim() === extractedSurvey.toLowerCase().trim() &&
    p.village_name && extractedVillage && p.village_name.toLowerCase().trim() === extractedVillage.toLowerCase().trim()
  );

  return (
    <div className="space-y-8">
      
      {/* Top Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/documents')}
            className="p-2 bg-white border border-border rounded-xl hover:bg-slate-50 text-slate-700 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold text-navy-900">{document.original_filename}</h1>
              {validation.status && <ValidationBadge status={validation.status} />}
            </div>
            <p className="text-xs text-muted font-mono mt-0.5">
              ID #{document.id} • {document.document_type} • {document.language}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {extraction ? (
            <div className="text-right space-y-1">
              <div className="flex items-center justify-end gap-1.5 text-[11px] font-mono">
                <span className="px-2 py-0.5 rounded bg-slate-100 border text-slate-700 font-semibold">{extraction.ocr_engine_used}</span>
                <span className="px-2 py-0.5 rounded bg-primary-50 border border-primary-200 text-primary-700 font-semibold">{extraction.extraction_source}</span>
              </div>
              <ConfidenceBadge score={extraction.overall_confidence} level={extraction.confidence_level} showBar />
            </div>
          ) : (
            <span className="px-3 py-1 rounded bg-amber-50 border border-amber-200 text-amber-700 font-mono text-xs font-bold">
              Extraction Pending
            </span>
          )}

          <button
            onClick={() => navigate('/verification')}
            className="px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-bold text-xs rounded-xl shadow-xs flex items-center gap-2"
          >
            <CheckSquare className="w-4 h-4" />
            <span>Open Verification Queue</span>
          </button>
        </div>
      </div>

      {/* Validation Warnings Alert Banner */}
      {(validation.warnings?.length > 0 || validation.errors?.length > 0 || validation.duplicate_detected || duplicateStatus !== 'NO_DUPLICATE') && (
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-800 space-y-1.5 shadow-xs">
          <div className="font-bold text-amber-900 flex items-center gap-2 text-sm">
            <ShieldAlert className="w-4 h-4 text-amber-600" />
            <span>System Validation & Quality Alerts</span>
          </div>
          {validation.errors?.map((err, idx) => (
            <p key={idx} className="text-error-600 font-medium">✕ {err}</p>
          ))}
          {validation.warnings?.map((warn, idx) => (
            <p key={idx} className="text-amber-800">⚠ {warn}</p>
          ))}
          {duplicateStatus === 'POTENTIAL_RECORD_DUPLICATE' && (
            <p className="text-purple-700 font-semibold">
              Potential Record Duplicate: Another uploaded document represents the same land record (Record #{validation.duplicate_record_id}, Similarity: {Math.round((validation.similarity_score || 0) * 100)}%)
            </p>
          )}
        </div>
      )}

      {/* ========================================================= */}
      {/* SECTION A — EXTRACTED DOCUMENT DATA */}
      {/* ========================================================= */}
      <section className="space-y-4">
        <div className="border-b border-border pb-3 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-extrabold text-navy-900 flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary-600" />
              <span>SECTION A — Extracted Document Data</span>
            </h2>
            <p className="text-xs text-muted">Original uploaded document image and AI extracted field values</p>
          </div>

          {extraction?.raw_ocr_text && (
            <button
              onClick={() => setShowRawOcr(!showRawOcr)}
              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium text-xs rounded-lg border border-slate-300 flex items-center gap-1.5 transition-colors"
            >
              <FileCode className="w-4 h-4 text-primary-600" />
              <span>{showRawOcr ? 'Hide Raw OCR' : 'View Raw OCR Text'}</span>
              {showRawOcr ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>

        {/* Collapsible Raw OCR Drawer */}
        {showRawOcr && extraction?.raw_ocr_text && (
          <div className="bg-slate-900 text-slate-200 p-4 rounded-xl font-mono text-xs overflow-x-auto max-h-60 border border-slate-700 space-y-2 shadow-inner">
            <div className="flex items-center justify-between text-slate-400 text-[11px] pb-2 border-b border-slate-800">
              <span>RAW OCR ENGINE OUTPUT</span>
              <span>{extraction.raw_ocr_text.length} characters</span>
            </div>
            <pre className="whitespace-pre-wrap">{extraction.raw_ocr_text}</pre>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          {/* Document Viewer */}
          <div className="sticky top-20">
            <DocumentViewer documentId={document.id} originalFilename={document.original_filename} />
          </div>

          {/* Extracted Fields Table */}
          <div>
            {extraction ? (
              <FieldExtractorTable fieldDetails={extraction.field_details} />
            ) : (
              <div className="bg-white rounded-xl border border-border p-8 text-center space-y-3 shadow-xs">
                <AlertCircle className="w-10 h-10 text-amber-500 mx-auto" />
                <h3 className="text-sm font-bold text-navy-900">Extraction result unavailable</h3>
                <p className="text-xs text-muted">Please process the document to see field extractions.</p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* ========================================================= */}
      {/* SECTION B — MASTER DATABASE VALIDATION */}
      {/* ========================================================= */}
      <section className="space-y-4">
        <div className="border-b border-border pb-3">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <h2 className="text-lg font-extrabold text-navy-900 flex items-center gap-2">
                <Database className="w-5 h-5 text-emerald-600" />
                <span>SECTION B — Master Database Validation</span>
              </h2>
              <p className="text-xs text-muted">Comparison against Authoritative Master Land Reference Database (10-record Master Registry)</p>
            </div>

            <div>
              {masterMatchStatus === 'MATCHED' && (
                <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold text-xs flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>MASTER MATCHED</span>
                </span>
              )}
              {masterMatchStatus === 'PARTIAL_MATCH' && (
                <span className="px-3 py-1 rounded-full bg-amber-100 text-amber-800 border border-amber-300 font-bold text-xs flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  <span>PARTIAL MASTER MATCH</span>
                </span>
              )}
              {masterMatchStatus === 'MISMATCH' && (
                <span className="px-3 py-1 rounded-full bg-rose-100 text-rose-800 border border-rose-300 font-bold text-xs flex items-center gap-1.5">
                  <AlertCircle className="w-4 h-4 text-rose-600" />
                  <span>MASTER MISMATCH</span>
                </span>
              )}
              {masterMatchStatus === 'NOT_FOUND' && (
                <span className="px-3 py-1 rounded-full bg-slate-100 text-slate-800 border border-slate-300 font-bold text-xs flex items-center gap-1.5">
                  <AlertCircle className="w-4 h-4 text-slate-500" />
                  <span>MASTER RECORD NOT FOUND</span>
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Master DB Comparison Table */}
        <div className="bg-white rounded-xl border border-border overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-100/70 text-slate-700 text-xs font-semibold uppercase font-mono border-b border-border">
                <tr>
                  <th className="p-3.5 w-1/4">Land Record Field</th>
                  <th className="p-3.5 w-1/3">Uploaded Document Value</th>
                  <th className="p-3.5 w-1/3">Authoritative Master DB</th>
                  <th className="p-3.5 text-right w-1/6">Match Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {[
                  { key: 'owner_name', label: 'Owner Name' },
                  { key: 'survey_number', label: 'Survey Number' },
                  { key: 'khata_number', label: 'Khata Number' },
                  { key: 'khasra_number', label: 'Khasra Number' },
                  { key: 'plot_area', label: 'Plot Area (Acres)' },
                  { key: 'village', label: 'Village' },
                  { key: 'tehsil', label: 'Tehsil' },
                  { key: 'district', label: 'District' },
                  { key: 'land_classification', label: 'Land Classification' },
                  { key: 'ownership_details', label: 'Ownership Details' },
                  { key: 'mutation_number', label: 'Mutation Number' },
                  { key: 'registration_number', label: 'Registration Number' }
                ].map((row) => {
                  const comp = fieldComp[row.key] || {};
                  const uploadedVal = comp.uploaded !== undefined && comp.uploaded !== null ? String(comp.uploaded) : '—';
                  const masterVal = comp.master !== undefined && comp.master !== null ? String(comp.master) : '—';
                  const isMatch = comp.match === true;
                  const hasMasterRecord = masterMatchStatus !== 'NOT_FOUND';

                  return (
                    <tr key={row.key} className="hover:bg-slate-50/80 transition-colors">
                      <td className="p-3.5 font-medium text-slate-700">{row.label}</td>
                      <td className="p-3.5 font-semibold text-navy-900 font-mono">{uploadedVal}</td>
                      <td className="p-3.5 font-mono text-slate-700">{masterVal}</td>
                      <td className="p-3.5 text-right">
                        {!hasMasterRecord ? (
                          <span className="px-2.5 py-1 rounded bg-slate-100 text-slate-600 font-mono text-xs font-semibold border border-slate-200">
                            NOT FOUND
                          </span>
                        ) : isMatch ? (
                          <span className="px-2.5 py-1 rounded bg-emerald-50 text-emerald-700 font-mono text-xs font-bold border border-emerald-200 inline-flex items-center gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            MATCH
                          </span>
                        ) : (
                          <span className="px-2.5 py-1 rounded bg-rose-50 text-rose-700 font-mono text-xs font-bold border border-rose-200 inline-flex items-center gap-1">
                            <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
                            MISMATCH
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ========================================================= */}
      {/* SECTION C — GIS VALIDATION */}
      {/* ========================================================= */}
      <section className="space-y-4">
        <div className="border-b border-border pb-3 flex items-center justify-between flex-wrap gap-2">
          <div>
            <h2 className="text-lg font-extrabold text-navy-900 flex items-center gap-2">
              <MapPin className="w-5 h-5 text-indigo-600" />
              <span>SECTION C — GIS Validation</span>
            </h2>
            <p className="text-xs text-muted">Cadastral plot mapping comparison against Master GIS Parcel database</p>
          </div>

          <div>
            {gisMatchStatus === 'GIS_MATCH' ? (
              <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold text-xs flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>GIS MATCH</span>
              </span>
            ) : gisMatchStatus === 'GIS_MISMATCH' ? (
              <span className="px-3 py-1 rounded-full bg-amber-100 text-amber-800 border border-amber-300 font-bold text-xs flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span>GIS MISMATCH</span>
              </span>
            ) : (
              <span className="px-3 py-1 rounded-full bg-slate-100 text-slate-800 border border-slate-300 font-bold text-xs flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4 text-slate-500" />
                <span>GIS Parcel Not Found</span>
              </span>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          
          {/* GIS Summary Card */}
          <div className="bg-white p-5 rounded-xl border border-border space-y-4 shadow-xs">
            <h3 className="text-sm font-bold text-navy-900 flex items-center gap-2 border-b border-border pb-2.5">
              <Layers className="w-4 h-4 text-primary-600" />
              <span>GIS Parcel Attributes</span>
            </h3>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center py-1 border-b border-slate-100">
                <span className="text-muted">Survey Match</span>
                <span className={`font-bold font-mono ${fieldComp.survey_number?.match ? 'text-emerald-700' : 'text-slate-500'}`}>
                  {fieldComp.survey_number?.match ? '✓ MATCHED' : '✕ NO MATCH'}
                </span>
              </div>

              <div className="flex justify-between items-center py-1 border-b border-slate-100">
                <span className="text-muted">Village Match</span>
                <span className={`font-bold font-mono ${fieldComp.village?.match ? 'text-emerald-700' : 'text-slate-500'}`}>
                  {fieldComp.village?.match ? '✓ MATCHED' : '✕ NO MATCH'}
                </span>
              </div>

              <div className="flex justify-between items-center py-1 border-b border-slate-100">
                <span className="text-muted">District Match</span>
                <span className={`font-bold font-mono ${fieldComp.district?.match ? 'text-emerald-700' : 'text-slate-500'}`}>
                  {fieldComp.district?.match ? '✓ MATCHED' : '✕ NO MATCH'}
                </span>
              </div>
            </div>

            {matchingParcel ? (
              <div className="pt-2 space-y-2 border-t border-border">
                <span className="text-[11px] font-bold uppercase text-slate-500 tracking-wider">Master Parcel Registry</span>
                <div className="p-3 bg-slate-50 rounded-lg space-y-1 text-xs">
                  <p className="font-bold text-navy-900">Survey #{matchingParcel.survey_number}</p>
                  <p className="text-slate-700">Owner: {matchingParcel.owner_name}</p>
                  <p className="text-slate-600">Location: {matchingParcel.village_name}, {matchingParcel.district_name}</p>
                  <p className="text-slate-600 font-mono">Extent: {matchingParcel.area_acre} Acres</p>
                </div>
              </div>
            ) : (
              <div className="pt-2 text-center p-4 bg-slate-50 rounded-lg text-slate-500 text-xs">
                GIS geometry unavailable for this survey & village identity.
              </div>
            )}
          </div>

          {/* GIS Map Display */}
          <div className="lg:col-span-2 min-h-[350px]">
            {matchingParcel ? (
              <ParcelMap parcels={[matchingParcel]} />
            ) : (
              <div className="w-full h-full min-h-[350px] bg-slate-100 rounded-xl border border-border flex flex-col items-center justify-center p-8 text-center text-slate-500 space-y-2">
                <MapPin className="w-10 h-10 text-slate-400" />
                <p className="font-bold text-navy-900">GIS geometry unavailable</p>
                <p className="text-xs text-muted max-w-md">
                  No spatial polygon geometry is registered in the master GIS layer for this uploaded document's land identity.
                </p>
              </div>
            )}
          </div>

        </div>
      </section>

    </div>
  );
};
