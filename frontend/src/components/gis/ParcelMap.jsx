import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polygon } from 'react-leaflet';
import L from 'leaflet';

// Fix Leaflet marker icon URLs
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export const ParcelMap = ({ parcels = [], onSelectParcel }) => {
  const defaultCenter = [12.9644, 79.9463]; // Kancheepuram lat/lng center

  return (
    <div className="w-full h-full min-h-[500px] rounded-xl overflow-hidden shadow-xs border border-border relative">
      <MapContainer
        center={defaultCenter}
        zoom={11}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {parcels.map((parcel) => (
          <React.Fragment key={parcel.id}>
            {parcel.boundary && parcel.boundary.length > 0 && (
              <Polygon
                positions={parcel.boundary}
                pathOptions={{
                  color: '#2563EB',
                  fillColor: '#3B82F6',
                  fillOpacity: 0.35,
                  weight: 2
                }}
                eventHandlers={{
                  click: () => onSelectParcel && onSelectParcel(parcel),
                }}
              />
            )}

            <Marker
              position={[parcel.lat, parcel.lng]}
              eventHandlers={{
                click: () => onSelectParcel && onSelectParcel(parcel),
              }}
            >
              <Popup>
                <div className="p-1 space-y-1 text-xs">
                  <h4 className="font-bold text-navy-900 text-sm">Survey #{parcel.survey_number}</h4>
                  <p className="text-slate-700"><strong>Owner:</strong> {parcel.owner_name}</p>
                  <p className="text-slate-700"><strong>Village:</strong> {parcel.village_name}, {parcel.district_name}</p>
                  <p className="text-slate-700"><strong>Area:</strong> {parcel.area_acre} Acres</p>
                  <p className="text-primary-600 font-semibold">{parcel.land_classification}</p>
                </div>
              </Popup>
            </Marker>
          </React.Fragment>
        ))}
      </MapContainer>
    </div>
  );
};
