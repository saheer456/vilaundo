import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import TrendBadge from './TrendBadge';
import PriceChart from './PriceChart';

export default function PriceCard({ item, activeDistrict }) {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(false);
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  useEffect(() => {
    if (expanded && history.length === 0) {
      const loadHistory = async () => {
        setLoadingHistory(true);
        try {
          const url = `/api/prices/${item.commodity_id}/history${
            activeDistrict ? `?district=${encodeURIComponent(activeDistrict)}` : ''
          }`;
          const res = await fetch(url);
          if (res.ok) {
            const data = await res.json();
            setHistory(data.history || []);
          }
        } catch (err) {
          console.error('Error fetching history:', err);
        } finally {
          setLoadingHistory(false);
        }
      };
      loadHistory();
    }
  }, [expanded, item.commodity_id, activeDistrict, history.length]);

  const handleShare = (e) => {
    e.stopPropagation(); // Prevent card expansion when clicking share
    const changeText = item.trend === 'up' ? '↑' : (item.trend === 'down' ? '↓' : '→');
    const changeVal = item.change_from_yesterday !== null ? `₹${Math.abs(item.change_from_yesterday)}` : '';
    const message = encodeURIComponent(
      `📊 *VilaUndo — Kerala Price Update*\n` +
      `🌿 *Crop*: ${item.name_en} (${item.name_ml})\n` +
      `📍 *District*: ${activeDistrict || 'All Kerala'}\n` +
      `💰 *Price*: ₹${item.price_modal} per ${item.unit}\n` +
      `📈 *Trend*: ${changeText} ${changeVal} vs yesterday\n\n` +
      `Check live daily Kerala prices → vilaundo.app`
    );
    window.open(`https://wa.me/?text=${message}`, '_blank');
  };

  return (
    <div 
      onClick={() => setExpanded(!expanded)}
      className={`group w-full border rounded-2xl bg-white transition-all duration-300 overflow-hidden cursor-pointer select-none ${
        expanded 
          ? 'shadow-lg border-emerald-500/20 ring-1 ring-emerald-500/10' 
          : 'border-slate-100 shadow-sm hover:shadow-md hover:border-slate-200/80 hover:-translate-y-0.5'
      }`}
    >
      {/* Main card row */}
      <div className="p-4 sm:p-5 flex justify-between items-center gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-bold text-slate-800 text-sm sm:text-base truncate">
              {item.name_en}
            </h4>
            <span className="text-slate-400 font-medium">|</span>
            <span className="font-medium text-slate-500 text-xs sm:text-sm truncate">
              {item.name_ml}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-[10px] sm:text-xs font-semibold px-2 py-0.5 bg-slate-100 text-slate-500 rounded-full uppercase tracking-wider">
              {t(item.category)}
            </span>
            <span className="text-slate-400 text-xs">•</span>
            <span className="text-slate-500 text-[11px] sm:text-xs">
              Per {item.unit}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-base sm:text-lg font-extrabold text-slate-900">
              {item.price_modal !== null ? `₹${item.price_modal}` : '-'}
            </div>
            <div className="mt-0.5">
              <TrendBadge 
                change={item.change_from_yesterday} 
                percent={item.change_percent} 
                trend={item.trend} 
              />
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-2">
            {/* Share action */}
            <button
              onClick={handleShare}
              title={t('whatsAppShare')}
              className="p-2 text-slate-400 hover:text-emerald-500 hover:bg-emerald-50 rounded-xl transition-all duration-200 cursor-pointer"
            >
              <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946C.06 5.348 5.397.01 12.008.01c3.202.001 6.212 1.246 8.477 3.514 2.266 2.268 3.507 5.28 3.505 8.484-.004 6.657-5.34 11.997-11.953 11.997-2.005-.001-3.973-.502-5.724-1.455L0 24zm6.79-4.024l.41.243c1.472.873 3.134 1.333 4.829 1.334 5.378 0 9.757-4.379 9.761-9.76.002-2.607-1.012-5.059-2.859-6.908C16.294 3.037 13.84 2.022 11.233 2.02c-5.385 0-9.767 4.382-9.771 9.764-.002 1.764.462 3.486 1.348 5.011l.278.482-.998 3.645 3.73-.978zM17.15 14.54c-.294-.147-1.743-.86-2.012-.959-.267-.098-.463-.147-.659.147-.196.294-.759.959-.93 1.155-.172.196-.344.22-.638.073-.293-.147-1.243-.458-2.368-1.462-.876-.782-1.467-1.747-1.639-2.042-.172-.294-.018-.453.128-.598.133-.131.294-.343.441-.515.147-.171.196-.294.294-.49.098-.196.049-.367-.025-.515-.074-.147-.659-1.592-.906-2.18-.24-.578-.484-.5-.659-.51-.171-.007-.367-.008-.563-.008-.196 0-.514.073-.784.367-.27.294-1.028 1.004-1.028 2.449 0 1.445 1.052 2.84 1.199 3.037.147.196 2.073 3.166 5.02 4.44.701.302 1.25.483 1.677.619.704.224 1.344.193 1.85.118.563-.083 1.742-.71 1.987-1.396.244-.686.244-1.273.171-1.396-.074-.122-.27-.196-.564-.343z" />
              </svg>
            </button>

            {/* Expand / Collapse Indicator */}
            <div className="p-2 text-slate-400 group-hover:text-slate-600 transition-colors">
              <svg 
                className={`w-5 h-5 transform transition-transform duration-300 ${expanded ? 'rotate-180 text-emerald-500' : ''}`} 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Expanded Chart & History Area */}
      {expanded && (
        <div 
          onClick={(e) => e.stopPropagation()} // Prevent collapse when clicking details
          className="border-t border-slate-100 bg-slate-50/30 p-5 space-y-4 cursor-default animate-slide-down"
        >
          {/* Header Info */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-semibold text-slate-500">
            <div>
              <span className="block text-[10px] text-slate-400 uppercase tracking-wider mb-0.5">{t('minMaxPrice')}</span>
              <span className="text-slate-800 font-bold text-sm">
                ₹{item.price_min || '-'} - ₹{item.price_max || '-'}
              </span>
            </div>
            <div>
              <span className="block text-[10px] text-slate-400 uppercase tracking-wider mb-0.5">{t('modalPrice')}</span>
              <span className="text-slate-800 font-bold text-sm">₹{item.price_modal || '-'}</span>
            </div>
            <div>
              <span className="block text-[10px] text-slate-400 uppercase tracking-wider mb-0.5">{t('sourceLabel')}</span>
              <span className="text-slate-800 font-bold text-sm">{item.source || 'Unknown'}</span>
            </div>
            <div>
              <span className="block text-[10px] text-slate-400 uppercase tracking-wider mb-0.5">Date</span>
              <span className="text-slate-800 font-bold text-sm">{item.date || '-'}</span>
            </div>
          </div>

          {/* Chart Display */}
          <div>
            <h5 className="text-xs font-bold text-slate-700 mb-2 uppercase tracking-wide">
              {t('historyTitle')}
            </h5>
            {loadingHistory ? (
              <div className="h-48 flex flex-col items-center justify-center space-y-2">
                <svg className="animate-spin h-6 w-6 text-emerald-500" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span className="text-slate-400 text-xs font-medium">{t('loading')}</span>
              </div>
            ) : (
              <PriceChart history={history} />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
