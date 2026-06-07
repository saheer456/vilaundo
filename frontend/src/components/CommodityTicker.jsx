import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAppStore } from '../store/useAppStore';

// International base prices in USD per kg
const INT_COMMODITIES = [
  { name_en: "International Rubber (RSS3)", name_ml: "റബ്ബർ അന്താരാഷ്ട്ര വില (RSS3)", usd_per_kg: 2.15 },
  { name_en: "Black Pepper (Malabar Spot)", name_ml: "കുരുമുളക് മലബാർ സ്പോട്ട്", usd_per_kg: 6.85 },
  { name_en: "Cardamom (Guatemala Spot)", name_ml: "ഏലം ഗ്വാട്ടിമാല സ്പോട്ട്", usd_per_kg: 15.20 }
];

export default function CommodityTicker() {
  const { t, i18n } = useTranslation();
  const { language } = useAppStore();
  const [usdToInr, setUsdToInr] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    const fetchRates = async () => {
      try {
        const res = await fetch("https://open.er-api.com/v6/latest/USD");
        if (res.ok && active) {
          const data = await res.json();
          const rate = data.rates?.INR || 95.27; // fallback to tested rate if unavailable
          setUsdToInr(rate);
        }
      } catch (err) {
        console.error("Exchange rate fetch failed, using fallback:", err);
        if (active) {
          setUsdToInr(95.27); // stable tested rate
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };
    fetchRates();
    return () => { active = false; };
  }, []);

  if (loading) {
    return (
      <div className="h-14 flex items-center justify-center bg-slate-50/50 dark:bg-slate-900/30 border border-slate-100 dark:border-slate-800/80 rounded-2xl animate-pulse">
        <div className="w-4 h-4 rounded-full border-2 border-emerald-500 border-t-transparent animate-spin mr-2" />
        <span className="text-xs text-slate-400 font-semibold">Fetching global market updates...</span>
      </div>
    );
  }

  if (!usdToInr) return null;

  return (
    <div className="w-full border border-emerald-500/20 dark:border-emerald-500/10 rounded-2xl p-4 bg-gradient-to-r from-emerald-500/10 via-teal-500/5 to-transparent shadow-sm flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 transition-all duration-300">
      <div className="flex items-center gap-3">
        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-ping flex-shrink-0" />
        <div>
          <h4 className="font-extrabold text-xs tracking-wider text-emerald-800 dark:text-emerald-400 uppercase">
            {language === 'en' ? "Global Commodity Spot Rates" : "ആഗോള വിപണി നിരക്കുകൾ (കിലോയ്ക്ക്)"}
          </h4>
          <p className="text-[10px] text-slate-500 dark:text-slate-400 font-medium">
            {language === 'en' 
              ? `Live conversion per kg (1 USD = ₹${usdToInr.toFixed(2)})` 
              : `തത്സമയ നിരക്കുകൾ കിലോയ്ക്ക് (1 USD = ₹${usdToInr.toFixed(2)})`}
          </p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 flex-1 justify-end">
        {INT_COMMODITIES.map((c, idx) => {
          const inrPrice = (c.usd_per_kg * usdToInr).toFixed(2);
          return (
            <div 
              key={idx} 
              className="flex items-center justify-between sm:justify-start gap-3 px-3 py-2 bg-white/70 dark:bg-slate-900/60 rounded-xl border border-slate-100/50 dark:border-slate-800/50 shadow-sm"
            >
              <div className="text-left">
                <span className="block text-[10px] font-bold text-slate-700 dark:text-slate-300 truncate max-w-[150px]">
                  {language === 'en' ? c.name_en.split(' (')[0] : c.name_ml.split(' (')[0]}
                </span>
                <span className="text-[9px] text-slate-400 font-medium">
                  ${c.usd_per_kg.toFixed(2)} / kg
                </span>
              </div>
              <div className="text-right">
                <span className="text-sm font-extrabold text-emerald-600 dark:text-emerald-400">
                  ₹{inrPrice}
                </span>
                <span className="block text-[8px] text-slate-400 uppercase font-semibold">
                  / kg
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
