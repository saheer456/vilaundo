import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAppStore } from './store/useAppStore';
import DistrictSelector from './components/DistrictSelector';
import CategoryFilter from './components/CategoryFilter';
import PriceList from './components/PriceList';
import CommunitySubmitModal from './components/CommunitySubmitModal';
import AlertsModal from './components/AlertsModal';
import CommodityTicker from './components/CommodityTicker';

export default function App() {
  const { t } = useTranslation();
  const {
    language,
    setLanguage,
    district,
    setDistrict,
    category,
    searchQuery,
    setSearchQuery,
    theme,
    setTheme,
    setShowSubmitModal,
    setShowAlertModal
  } = useAppStore();

  const [prices, setPrices] = useState([]);
  const [pricesDate, setPricesDate] = useState('');
  const [delayed, setDelayed] = useState(false);
  const [loading, setLoading] = useState(true);
  
  const [commodities, setCommodities] = useState([]);
  const [districts, setDistricts] = useState([]);

  // Fetch commodities and districts on mount
  useEffect(() => {
    const loadMetadata = async () => {
      try {
        const resC = await fetch('/api/commodities');
        if (resC.ok) {
          const dC = await resC.json();
          setCommodities(dC.commodities || []);
        }
        
        const resD = await fetch('/api/districts');
        if (resD.ok) {
          const dD = await resD.json();
          setDistricts(dD.districts || []);
        }
      } catch (err) {
        console.error('Failed to fetch metadata:', err);
      }
    };
    loadMetadata();
  }, []);

  // Sync theme with body class
  useEffect(() => {
    if (theme === 'dark') {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
  }, [theme]);

  // Fetch prices based on active district filter
  useEffect(() => {
    let active = true;
    const loadPrices = async () => {
      setLoading(true);
      try {
        const url = `/api/prices/today${district ? `?district=${encodeURIComponent(district)}` : ''}`;
        const res = await fetch(url);
        if (res.ok && active) {
          const data = await res.json();
          setPrices(data.prices || []);
          setPricesDate(data.prices_date || data.date || '');
          setDelayed(!!data.delayed);
        }
      } catch (err) {
        console.error('Failed to fetch prices:', err);
        if (active) {
          setPrices([]);
          setDelayed(true);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };
    loadPrices();
    return () => { active = false; };
  }, [district]);

  // Filter prices by Category and Search query
  const filteredPrices = prices.filter((item) => {
    // Category filter
    const matchesCategory = category === 'all' || item.category === category;
    
    // Search query filter (matches English or Malayalam names)
    const query = searchQuery.trim().toLowerCase();
    const matchesSearch = !query || 
      item.name_en.toLowerCase().includes(query) || 
      item.name_ml.toLowerCase().includes(query);
      
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors duration-300 pb-16">
      {/* Header Bar */}
      <header className="sticky top-0 z-40 w-full glass-header shadow-sm transition-all duration-300">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <img 
              src="/logo.png" 
              alt="VilaUndo Logo" 
              className="w-9 h-9 rounded-xl object-cover shadow-md shadow-emerald-500/10 border border-emerald-500/20"
            />
            <div>
              <h1 className="font-extrabold text-base sm:text-xl tracking-tight bg-gradient-to-r from-emerald-600 to-teal-500 dark:from-emerald-400 dark:to-teal-300 bg-clip-text text-transparent">
                {t('appTitle')}
              </h1>
              <p className="text-[9px] sm:text-[11px] font-semibold text-slate-400 dark:text-slate-500 tracking-wide">
                {t('appSubtitle')}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Language Toggle */}
            <button
              id="btn-language-toggle"
              onClick={() => setLanguage(language === 'en' ? 'ml' : 'en')}
              className="px-3 py-1.5 text-xs font-bold text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 transition-all cursor-pointer shadow-sm"
            >
              {t('langToggleLabel')}
            </button>

            {/* Theme Toggle */}
            <button
              id="btn-theme-toggle"
              onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
              className="p-2 text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 transition-all cursor-pointer shadow-sm"
              title="Toggle Dark Mode"
            >
              {theme === 'light' ? (
                <svg className="w-4.5 h-4.5 fill-current" viewBox="0 0 24 24">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                </svg>
              ) : (
                <svg className="w-4.5 h-4.5 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="5" />
                  <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 mt-6 space-y-6">
        
        {/* Delayed Data Alert Banner */}
        {delayed && pricesDate && (
          <div className="p-3.5 bg-amber-50 dark:bg-amber-950/20 text-amber-800 dark:text-amber-300 border border-amber-200/50 dark:border-amber-900/30 rounded-2xl flex items-start gap-3 animate-fade-in shadow-sm">
            <svg className="w-5 h-5 stroke-current flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div className="text-xs font-semibold">
              {t('delayedWarning')} <span className="underline decoration-wavy decoration-amber-500/50 font-bold">{pricesDate}</span>.
            </div>
          </div>
        )}

        {/* Filters Controls Panel */}
        <section className="glass-card rounded-2xl p-5 shadow-sm space-y-4">
          <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
            {/* Search Input */}
            <div className="relative flex-1">
              <input
                id="input-search-crop"
                type="text"
                placeholder={t('searchPlaceholder')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 text-sm font-semibold text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800/80 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all placeholder-slate-400 dark:placeholder-slate-500"
              />
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>

            {/* District dropdown & geolocation */}
            <DistrictSelector
              districts={districts}
              value={district}
              onChange={setDistrict}
            />
          </div>

          {/* Categories Horizontal Tabs */}
          <CategoryFilter />

          {/* Quick Submission & Alert Action buttons */}
          <div className="flex items-center gap-3 pt-1 border-t border-slate-100/50 dark:border-slate-800/30">
            <button
              id="btn-submit-price"
              onClick={() => setShowSubmitModal(true)}
              className="flex-1 py-2.5 px-4 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white font-bold rounded-xl text-xs sm:text-sm shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer flex items-center justify-center gap-1.5"
            >
              <svg className="w-4.5 h-4.5 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {t('submitPriceAction')}
            </button>
            <button
              id="btn-set-alert"
              onClick={() => setShowAlertModal(true)}
              className="flex-1 py-2.5 px-4 border border-emerald-500/20 hover:border-emerald-500 text-emerald-600 dark:text-emerald-400 font-bold bg-emerald-50/10 hover:bg-emerald-500/5 rounded-xl text-xs sm:text-sm transition-all duration-200 cursor-pointer flex items-center justify-center gap-1.5"
            >
              <svg className="w-4.5 h-4.5 fill-none stroke-current stroke-2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              {t('setAlertAction')}
            </button>
          </div>
        </section>

        {/* Commodity Ticker */}
        <CommodityTicker />

        {/* Pricing List Section */}
        <section className="space-y-4">
          <h3 className="font-extrabold text-sm sm:text-base text-slate-500 dark:text-slate-400 uppercase tracking-wider pl-1">
            {t('todayPrices')} {district ? `— ${district}` : ''}
          </h3>

          {loading ? (
            <div className="py-24 flex flex-col items-center justify-center space-y-3">
              <svg className="animate-spin h-8 w-8 text-emerald-500" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span className="text-slate-400 dark:text-slate-500 text-xs sm:text-sm font-semibold">
                {t('loading')}
              </span>
            </div>
          ) : (
            <PriceList 
              items={filteredPrices} 
              activeDistrict={district} 
            />
          )}
        </section>
      </main>

      {/* Crowdsourced Pricing submissions modal */}
      <CommunitySubmitModal 
        crops={commodities} 
        districts={districts} 
      />

      {/* Threshold Alerts Modal */}
      <AlertsModal 
        crops={commodities} 
        districts={districts} 
      />
    </div>
  );
}
