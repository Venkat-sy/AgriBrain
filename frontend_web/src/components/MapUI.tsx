"use client";
import React from "react";
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const svgPin = L.divIcon({
  className: "custom-pin-icon",
  html: `<div style="transform: translate(-14px, -38px);">
    <svg width="34" height="42" viewBox="0 0 24 30" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 0C5.37 0 0 5.37 0 12C0 21 12 30 12 30C12 30 24 21 24 12C24 5.37 18.63 0 12 0Z" fill="#10B981"/>
      <circle cx="12" cy="11" r="5" fill="#0F172A"/>
    </svg>
  </div>`,
  iconSize: [34, 42],
  iconAnchor: [17, 42],
});

interface MapUIProps {
  pin: { lat: number; lng: number } | null;
  onPinDrop: (lat: number, lng: number) => void;
}

function ClickHandler({ onPinDrop }: { onPinDrop: (lat: number, lng: number) => void }) {
  useMapEvents({
    click(e) {
      onPinDrop(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export default function MapUI({ pin, onPinDrop }: MapUIProps) {
  const centerPos: [number, number] = pin ? [pin.lat, pin.lng] : [20.5937, 78.9629];

  return (
    <div className="w-full h-[320px] sm:h-[400px] lg:h-[460px] rounded-2xl overflow-hidden border border-slate-700/80 shadow-2xl relative z-0">
      <MapContainer center={centerPos} className="w-full h-full z-0" scrollWheelZoom={true} zoom={5}>
        <TileLayer
          attribution={`&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>`}
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ClickHandler onPinDrop={onPinDrop} />
        {pin && (
          <Marker icon={svgPin} position={[pin.lat, pin.lng]}>
            <Popup>
              Selected Farm: {pin.lat.toFixed(4)}°N, {pin.lng.toFixed(4)}°E
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}