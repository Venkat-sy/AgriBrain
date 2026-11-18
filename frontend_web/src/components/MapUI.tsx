"use client";
import React, { useEffect, useMemo, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const svgPin = L.divIcon({
  className: "custom-pin-icon",
  html: `<div style="transform: translate(-16px, -40px); cursor: grab;">
    <svg width="36" height="44" viewBox="0 0 24 30" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 0C5.37 0 0 5.37 0 12C0 21 12 30 12 30C12 30 24 21 24 12C24 5.37 18.63 0 12 0Z" fill="#10B981" stroke="#ffffff" stroke-width="1.5"/>
      <circle cx="12" cy="11" r="5" fill="#0F172A"/>
    </svg>
  </div>`,
  iconSize: [36, 44],
  iconAnchor: [18, 44],
});

interface MapUIProps {
  pin: { lat: number; lng: number } | null;
  onPinDrop: (lat: number, lng: number) => void;
  center?: [number, number];
  zoom?: number;
  className?: string;
}

function ClickHandler({ onPinDrop }: { onPinDrop: (lat: number, lng: number) => void }) {
  useMapEvents({
    click(e) {
      onPinDrop(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

function MapFlyTo({ pin, center, zoom }: { pin: { lat: number; lng: number } | null; center?: [number, number]; zoom?: number }) {
  const map = useMap();
  const defaultCenter: [number, number] = center || [20.5937, 78.9629];
  const defaultZoom: number = zoom || 5;
  
  useEffect(() => {
    if (pin) {
      map.flyTo([pin.lat, pin.lng], Math.max(map.getZoom(), 7), { duration: 0.75 });
    } else {
      map.flyTo(defaultCenter, defaultZoom, { duration: 0.75 });
    }
  }, [pin, map, defaultCenter, defaultZoom]);
  return null;
}

export default function MapUI({ pin, onPinDrop, center, zoom, className }: MapUIProps) {
  const markerRef = useRef<any>(null);
  const defaultCenter: [number, number] = center || [20.5937, 78.9629];
  const defaultZoom: number = zoom || 5;
  const markerPos: [number, number] | null = pin ? [pin.lat, pin.lng] : null;

  const eventHandlers = useMemo(
    () => ({
      dragend() {
        const marker = markerRef.current;
        if (marker != null) {
          const pos = marker.getLatLng();
          onPinDrop(pos.lat, pos.lng);
        }
      },
    }),
    [onPinDrop]
  );

  return (
      <div className={`w-full h-[320px] sm:h-[390px] lg:h-[430px] rounded-2xl overflow-hidden border border-slate-700/80 shadow-2xl relative z-0 ${className || ''}`}>
      <MapContainer center={defaultCenter} className="w-full h-full z-0" scrollWheelZoom={true} zoom={defaultZoom}>
        <TileLayer
                          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
        <ClickHandler onPinDrop={onPinDrop}/>
        <MapFlyTo pin={pin} center={center} zoom={zoom}/>
        {markerPos && pin && (
          <Marker draggable={true} eventHandlers={eventHandlers} icon={svgPin} position={markerPos} ref={markerRef}>
            <Popup>
              <div className="text-xs font-semibold text-slate-900">
                📍 Farm Pin: {pin.lat.toFixed(4)}°N, {pin.lng.toFixed(4)}°E
                <br />
                <span className="text-emerald-700">(Drag pin or click map to adjust)</span>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}