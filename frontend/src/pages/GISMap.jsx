import React, { useEffect, useState } from 'react';
import { MapPin, Filter, Layers, Info } from 'lucide-react';
import api from '../services/api';
import { ParcelMap } from '../components/gis/ParcelMap';

export const GISMap = () => {
  const [parcels, setParcels] = useState([]);
  const [selectedParcel, setSelectedParcel] = useState(null);
  const [district, setDistrict] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchParcels();
  }, [district]);

  const fetchParcels = async () => {
    try {
      const res = await api.get('/gis/parcels', {
        params: { district: district || undefined }
      });
      setParcels(res.data);
      if (res.data.length > 0 && !selectedParcel) {
        setSelectedParcel(res.data[0]);
      }
    } catch (err) {
      console.error("Failed to load GIS parcels", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 h-[calc(100vh-8rem)] flex flex-col">
      
      {/* Title & Filter Controls */}
      <div className="flex items-center justify-between flex-wrap gap-4 shrink-0">
        <div>
          <h1 className="text-2xl font-extrabold text-navy-900 flex items-center gap-2">
            <MapPin className="w-6 h-6 text-primary-600" />
            <span>GIS Master Land Parcel Visualization</span>
          </h1>
          <p className="text-sm text-muted">Cadastral plot mapping visualization connected to authoritative Master Parcel Reference Database</p>
        </div>

        <div className="flex items-center gap-3">
          <Filter className="w-4 h-4 text-muted" />
          <select
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
            className="px-3 py-2 bg-white border border-border rounded-xl text-sm font-medium shadow-xs"
          >
            <option value="">All Districts</option>
            <option value="Kancheepuram">Kancheepuram</option>
            <option value="Chengalpattu">Chengalpattu</option>
            <option value="Coimbatore">Coimbatore</option>
          </select>
        </div>
      </div>

      {/* Main Grid: Leaflet Map Left, Parcel Info Card Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        
        {/* Leaflet Map (Spans 2 columns) */}
        <div className="lg:col-span-2 h-full min-h-[450px]">
          <ParcelMap parcels={parcels} onSelectParcel={(p) => setSelectedParcel(p)} />
        </div>

        {/* Selected Parcel Information Card */}
        <div className="bg-white p-6 rounded-xl border border-border shadow-xs overflow-y-auto space-y-4">
          <h3 className="text-base font-bold text-navy-900 flex items-center gap-2 border-b border-border pb-3">
            <Layers className="w-5 h-5 text-primary-600" />
            <span>Master Parcel Details</span>
          </h3>

          {selectedParcel ? (
            <div className="space-y-4 text-sm">
              
              <div className="p-3 bg-primary-50/60 rounded-xl border border-primary-100 space-y-1">
                <span className="text-xs text-primary-700 font-mono font-bold uppercase">Survey Number</span>
                <p className="text-xl font-extrabold text-navy-900 font-mono">{selectedParcel.survey_number}</p>
              </div>

              <div className="space-y-3 divide-y divide-border">
                <div className="pt-2">
                  <span className="text-xs text-muted block font-medium">Registered Owner Name</span>
                  <p className="font-bold text-navy-900 text-base">{selectedParcel.owner_name}</p>
                </div>

                <div className="pt-2">
                  <span className="text-xs text-muted block font-medium">Location Hierarchy</span>
                  <p className="font-semibold text-slate-800">
                    Village: {selectedParcel.village_name}
                  </p>
                  <p className="text-xs text-slate-600">
                    Tehsil: {selectedParcel.tehsil_name} • District: {selectedParcel.district_name}
                  </p>
                </div>

                <div className="pt-2">
                  <span className="text-xs text-muted block font-medium">Plot Extent Area</span>
                  <p className="font-mono font-bold text-navy-900 text-base">{selectedParcel.area_acre} Acres</p>
                </div>

                <div className="pt-2">
                  <span className="text-xs text-muted block font-medium">Land Classification</span>
                  <span className="inline-block mt-1 px-2.5 py-1 bg-slate-100 text-slate-800 rounded-md font-semibold text-xs border border-slate-200">
                    {selectedParcel.land_classification}
                  </span>
                </div>

                <div className="pt-2">
                  <span className="text-xs text-muted block font-medium">GPS Center Coordinates</span>
                  <p className="font-mono text-xs text-slate-600">
                    Lat: {selectedParcel.lat.toFixed(4)}, Lng: {selectedParcel.lng.toFixed(4)}
                  </p>
                </div>
              </div>

            </div>
          ) : (
            <div className="text-center py-12 text-muted text-xs space-y-2">
              <Info className="w-8 h-8 mx-auto text-slate-300" />
              <p>Click on any polygon parcel or pin marker on the map to view master parcel metadata.</p>
            </div>
          )}
        </div>

      </div>

    </div>
  );
};
