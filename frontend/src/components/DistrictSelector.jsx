import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

// Kerala District centers (Latitude, Longitude) for geolocation matching
const DISTRICT_COORDS = [
  { name: "Thiruvananthapuram", lat: 8.5241, lon: 76.9366 },
  { name: "Kollam", lat: 8.8932, lon: 76.6141 },
  { name: "Pathanamthitta", lat: 9.2648, lon: 76.7870 },
  { name: "Alappuzha", lat: 9.4981, lon: 76.3388 },
  { name: "Kottayam", lat: 9.5916, lon: 76.5222 },
  { name: "Idukki", lat: 9.8503, lon: 77.0674 },
  { name: "Ernakulam", lat: 9.9816, lon: 76.2999 },
  { name: "Thrissur", lat: 10.5276, lon: 76.2144 },
  { name: "Palakkad", lat: 10.7867, lon: 76.6548 },
  { name: "Malappuram", lat: 11.0735, lon: 76.0740 },
  { name: "Kozhikode", lat: 11.2588, lon: 75.7804 },
  { name: "Wayanad", lat: 11.6854, lon: 76.1320 },
  { name: "Kannur", lat: 11.8745, lon: 75.3704 },
  { name: "Kasargod", lat: 12.5102, lon: 74.9852 }
];

export default function DistrictSelector({ districts, value, onChange }) {
  const { t } = useTranslation();
  const [detecting, setDetecting] = useState(false);

  const detectDistrict = () => {
    if (!navigator.geolocation) return;
    setDetecting(true);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        let closest = null;
        let minDist = Infinity;

        DISTRICT_COORDS.forEach((d) => {
          const dist = Math.pow(d.lat - latitude, 2) + Math.pow(d.lon - longitude, 2);
          if (dist < minDist) {
            minDist = dist;
            closest = d.name;
          }
        });

        if (closest) {
          // Find matching district in loaded list to ensure correct casing
          const match = districts.find(d => d.name_en.toLowerCase() === closest.toLowerCase());
          if (match) {
            onChange(match.name_en);
          }
        }
        setDetecting(false);
      },
      (error) => {
        console.error("Geolocation failed:", error);
        setDetecting(false);
      },
      { timeout: 10000 }
    );
  };

  return (
    <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 w-full sm:w-auto">
      <div className="relative flex-1 sm:flex-initial">
        <select 
          className="w-full sm:w-64 pl-9 pr-8 py-2.5 text-sm font-semibold text-slate-700 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all appearance-none cursor-pointer"
          value={value} 
          onChange={(e) => onChange(e.target.value)}
        >
          <option value="">📍 {t('selectDistrict')}</option>
          {districts.map((d) => (
            <option key={d.id} value={d.name_en}>
              {d.name_en} ({d.name_ml})
            </option>
          ))}
        </select>
        <div className="absolute inset-y-0 right-0 pr-3.5 flex items-center pointer-events-none text-slate-400">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {navigator.geolocation && (
        <button
          onClick={detectDistrict}
          disabled={detecting}
          className="px-4 py-2.5 text-xs sm:text-sm font-semibold text-emerald-600 bg-emerald-50 hover:bg-emerald-100/80 active:bg-emerald-100 rounded-xl transition-all border border-emerald-100/50 flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-60"
        >
          {detecting ? (
            <>
              <svg className="animate-spin h-4 w-4 text-emerald-600" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span>...</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                <path d="M12 8c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm8.94 3c-.46-4.17-3.77-7.48-7.94-7.94V1h-2v2.06C6.83 3.52 3.52 6.83 3.06 11H1v2h2.06c.46 4.17 3.77 7.48 7.94 7.94V23h2v-2.06c4.17-.46 7.48-3.77 7.94-7.94H23v-2h-2.06zM12 19c-3.87 0-7-3.13-7-7s3.13-7 7-7 7 3.13 7 7-3.13 7-7 7z" />
              </svg>
              <span>{t('detectLocation')}</span>
            </>
          )}
        </button>
      )}
    </div>
  );
}
