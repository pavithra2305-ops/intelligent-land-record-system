import React, { useState } from 'react';
import { ZoomIn, ZoomOut, RotateCw, RefreshCw, Eye, Sparkles } from 'lucide-react';

export const DocumentViewer = ({ documentId, originalFilename }) => {
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [viewProcessed, setViewProcessed] = useState(false);

  const originalUrl = `/api/documents/${documentId}/file`;
  const processedUrl = `/api/documents/${documentId}/processed-file`;

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 25, 250));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 25, 50));
  const handleRotate = () => setRotation((prev) => (prev + 90) % 360);
  const handleReset = () => {
    setZoom(100);
    setRotation(0);
  };

  return (
    <div className="bg-white rounded-xl border border-border overflow-hidden flex flex-col h-full min-h-[550px]">
      {/* Controls Bar */}
      <div className="p-3 bg-slate-50 border-b border-border flex items-center justify-between gap-2 flex-wrap text-xs">
        <div className="flex items-center gap-1.5 font-semibold text-navy-900 truncate">
          <Eye className="w-4 h-4 text-primary-600 shrink-0" />
          <span className="truncate">{originalFilename}</span>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-1 bg-slate-200 p-0.5 rounded-lg">
          <button
            onClick={() => setViewProcessed(false)}
            className={`px-2.5 py-1 rounded-md text-xs font-semibold transition-all ${
              !viewProcessed ? 'bg-white text-navy-900 shadow-xs' : 'text-slate-600 hover:text-navy-900'
            }`}
          >
            Original
          </button>
          <button
            onClick={() => setViewProcessed(true)}
            className={`px-2.5 py-1 rounded-md text-xs font-semibold flex items-center gap-1 transition-all ${
              viewProcessed ? 'bg-primary-600 text-white shadow-xs' : 'text-slate-600 hover:text-navy-900'
            }`}
          >
            <Sparkles className="w-3 h-3" />
            <span>Preprocessed</span>
          </button>
        </div>

        {/* Zoom & Rotate Tools */}
        <div className="flex items-center gap-1">
          <button
            onClick={handleZoomOut}
            className="p-1.5 hover:bg-slate-200 rounded-md text-slate-700"
            title="Zoom out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="font-mono text-[11px] w-12 text-center">{zoom}%</span>
          <button
            onClick={handleZoomIn}
            className="p-1.5 hover:bg-slate-200 rounded-md text-slate-700"
            title="Zoom in"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleRotate}
            className="p-1.5 hover:bg-slate-200 rounded-md text-slate-700"
            title="Rotate 90deg"
          >
            <RotateCw className="w-4 h-4" />
          </button>
          <button
            onClick={handleReset}
            className="p-1.5 hover:bg-slate-200 rounded-md text-slate-700"
            title="Reset view"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Image / PDF Display Region */}
      <div className="flex-1 bg-slate-900/90 p-4 flex items-center justify-center overflow-auto relative">
        <div
          className="transition-transform duration-200 max-w-full"
          style={{
            transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
            transformOrigin: 'center center'
          }}
        >
          <img
            src={viewProcessed ? processedUrl : originalUrl}
            alt="Document"
            className="max-h-[650px] object-contain rounded shadow-2xl bg-white"
            onError={(e) => {
              // Fallback placeholder if image load fails
              e.target.src = "https://placehold.co/600x800/f8fafc/0f172a?text=Land+Record+Document+Preview";
            }}
          />
        </div>
      </div>
    </div>
  );
};
