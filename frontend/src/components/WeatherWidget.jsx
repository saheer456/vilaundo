import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAppStore } from '../store/useAppStore';

const DISTRICT_COORDS = {
  "thiruvananthapuram": { lat: 8.5241, lon: 76.9366 },
  "kollam": { lat: 8.8932, lon: 76.6141 },
  "pathanamthitta": { lat: 9.2648, lon: 76.7870 },
  "alappuzha": { lat: 9.4981, lon: 76.3388 },
  "kottayam": { lat: 9.5916, lon: 76.5222 },
  "idukki": { lat: 9.8503, lon: 77.0674 },
  "ernakulam": { lat: 9.9816, lon: 76.2999 },
  "thrissur": { lat: 10.5276, lon: 76.2144 },
  "palakkad": { lat: 10.7867, lon: 76.6548 },
  "malappuram": { lat: 11.0735, lon: 76.0740 },
  "kozhikode": { lat: 11.2588, lon: 75.7804 },
  "wayanad": { lat: 11.6854, lon: 76.1320 },
  "kannur": { lat: 11.8745, lon: 75.3704 },
  "kasargod": { lat: 12.5102, lon: 74.9852 }
};

const WEATHER_STATUS = {
  sunny: {
    en: "Sunny / Clear",
    ml: "തെളിഞ്ഞ ആകാശം",
    tip_en: "Optimal conditions for rubber tapping, coconut copra, and spice drying.",
    tip_ml: "റബ്ബർ വെട്ടുന്നതിനും വിളകളും കൊപ്രയും ഉണക്കുന്നതിനും മികച്ച സമയം.",
    bg: "from-amber-500/10 via-orange-500/5 to-transparent border-amber-200/40 text-amber-900 dark:text-amber-100 dark:border-amber-900/20",
    icon: (
      <svg className="w-8 h-8 text-amber-500 animate-[spin_20s_linear_infinite]" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zm0-2c.55 0 1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1v2c0 .55.45 1 1 1zm0 14c-.55 0-1 .45-1 1v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1zm8.66-9c-.19-.48-.67-.79-1.19-.68l-1.92.41c-.48.1-.82.52-.82 1.01s.34.91.82 1.01l1.92.41c.52.11 1-.2 1.19-.68.27-.68.27-1.48 0-2.16zm-14.5-.86c-.52-.11-1 .2-1.19.68-.27.68-.27 1.48 0 2.16.19.48.67.79 1.19.68l1.92-.41c.48-.1.82-.52.82-1.01s-.34-.91-.82-1.01l-1.92-.41zm11.39-4.8c-.4-.4-.93-.6-1.46-.6a2.03 2.03 0 00-1.41 3.44l1.42 1.42c.39.39.9.58 1.41.58.52 0 1.03-.2 1.42-.59.78-.78.78-2.05 0-2.83l-1.38-1.42zM5.91 16.68a2.03 2.03 0 00-2.83 0 2.03 2.03 0 000 2.83l1.42 1.42c.39.39.9.59 1.41.59.51 0 1.02-.2 1.41-.59.78-.78.78-2.05 0-2.83l-1.41-1.42zm12.18 0l-1.42 1.42c-.78.78-.78 2.05 0 2.83.39.39.9.59 1.41.59.52 0 1.02-.2 1.42-.59l1.42-1.42c.78-.78.78-2.05 0-2.83a2.03 2.03 0 00-2.83 0zM5.91 4.46L4.5 5.88c-.78.78-.78 2.05 0 2.83.39.39.9.59 1.41.59.52 0 1.02-.2 1.42-.59l1.42-1.42c.78-.78.78-2.05 0-2.83a2.03 2.03 0 00-2.83 0z" />
      </svg>
    )
  },
  cloudy: {
    en: "Cloudy / Overcast",
    ml: "മേഘാവൃതമായ ആകാശം",
    tip_en: "Cloudy sky. Avoid keeping agricultural harvests outdoors.",
    tip_ml: "മേഘാവൃതമായ കാലാവസ്ഥ. വിളകൾ വെളിയിൽ സൂക്ഷിക്കുന്നത് ഒഴിവാക്കുക.",
    bg: "from-slate-400/10 via-slate-500/5 to-transparent border-slate-200/40 text-slate-800 dark:text-slate-200 dark:border-slate-800/30",
    icon: (
      <svg className="w-8 h-8 text-slate-400 dark:text-slate-500" fill="currentColor" viewBox="0 0 24 24">
        <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" />
      </svg>
    )
  },
  rainy: {
    en: "Rainy / Showers",
    ml: "മഴയുള്ള കാലാവസ്ഥ",
    tip_en: "Rainfall expected. Cover drying crops and delay rubber tapping.",
    tip_ml: "മഴയ്ക്ക് സാധ്യതയുണ്ട്. ഉണക്കാനിട്ട വിളകൾ മാറ്റുക, റബ്ബർ വെട്ട് മാറ്റിവെക്കുക.",
    bg: "from-emerald-500/10 via-teal-500/5 to-transparent border-emerald-200/30 text-slate-800 dark:text-slate-200 dark:border-emerald-950/20",
    icon: (
      <svg className="w-8 h-8 text-emerald-500" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm-1 8h-2V9h2v1zm0-3h-2V6h2v1zm4 3h-2V9h2v1zm0-3h-2V6h2v1z" />
      </svg>
    )
  }
};

export default function WeatherWidget({ activeDistrict }) {
  const { language } = useAppStore();
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;
    const fetchWeather = async () => {
      setLoading(true);
      setError(false);
      try {
        const distKey = (activeDistrict || "ernakulam").toLowerCase().trim();
        const coords = DISTRICT_COORDS[distKey] || DISTRICT_COORDS["ernakulam"];

        const res = await fetch(
          `https://api.open-meteo.com/v1/forecast?latitude=${coords.lat}&longitude=${coords.lon}&current_weather=true&daily=precipitation_probability_max&timezone=Asia/Kolkata`
        );
        if (res.ok && active) {
          const data = await res.json();
          setWeatherData({
            temp: data.current_weather.temperature,
            code: data.current_weather.weathercode,
            rainProb: data.daily?.precipitation_probability_max?.[0] ?? 0
          });
        } else if (active) {
          setError(true);
        }
      } catch (err) {
        console.error("Weather fetch failed:", err);
        if (active) {
          setError(true);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    fetchWeather();
    return () => { active = false; };
  }, [activeDistrict]);

  if (loading) {
    return (
      <div className="h-20 flex items-center justify-center bg-slate-50/50 dark:bg-slate-900/30 border border-slate-100 dark:border-slate-800/80 rounded-2xl animate-pulse">
        <div className="w-4 h-4 rounded-full border-2 border-emerald-500 border-t-transparent animate-spin mr-2" />
        <span className="text-xs text-slate-400 font-semibold">Updating weather forecast...</span>
      </div>
    );
  }

  if (error || !weatherData) return null;

  // Determine weather category from code
  let statusKey = 'sunny';
  const c = weatherData.code;
  if (c >= 2 && c <= 48) {
    statusKey = 'cloudy';
  } else if (c > 48) {
    statusKey = 'rainy';
  }

  const status = WEATHER_STATUS[statusKey];

  return (
    <div className={`w-full border rounded-2xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-r ${status.bg} shadow-sm transition-all duration-300`}>
      <div className="flex items-center gap-3.5">
        <div className="p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-100/50 dark:border-slate-800/50 shadow-sm flex-shrink-0">
          {status.icon}
        </div>
        <div>
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-black text-slate-800 dark:text-slate-100">
              {weatherData.temp}°C
            </span>
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 capitalize">
              {language === 'en' ? status.en : status.ml}
            </span>
          </div>
          <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 font-medium mt-0.5">
            {language === 'en' ? status.tip_en : status.tip_ml}
          </p>
        </div>
      </div>

      <div className="w-full sm:w-auto flex items-center justify-between sm:justify-end gap-6 border-t sm:border-t-0 pt-3 sm:pt-0 border-slate-200/40 dark:border-slate-800/20">
        <div className="text-left sm:text-right">
          <span className="block text-[9px] text-slate-400 uppercase tracking-wider font-semibold">
            {language === 'en' ? 'Rain Chance' : 'മഴസാധ്യത'}
          </span>
          <span className="text-sm font-extrabold text-slate-700 dark:text-slate-300">
            {weatherData.rainProb}%
          </span>
        </div>
        <div className="text-right">
          <span className="block text-[9px] text-slate-400 uppercase tracking-wider font-semibold">
            {language === 'en' ? 'Region' : 'മേഖല'}
          </span>
          <span className="text-sm font-extrabold text-emerald-600 dark:text-emerald-400 truncate max-w-[120px] block">
            {activeDistrict || (language === 'en' ? 'All Kerala' : 'കേരളം')}
          </span>
        </div>
      </div>
    </div>
  );
}
