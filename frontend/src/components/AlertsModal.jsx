import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAppStore } from '../store/useAppStore';

export default function AlertsModal({ crops, districts }) {
  const { t } = useTranslation();
  const { showAlertModal, setShowAlertModal } = useAppStore();

  const [cropId, setCropId] = useState('');
  const [districtId, setDistrictId] = useState('');
  const [thresholdPrice, setThresholdPrice] = useState('');
  const [direction, setDirection] = useState('above');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  if (!showAlertModal) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!cropId || !districtId || !thresholdPrice) {
      setError('Please fill out all required fields.');
      return;
    }
    setError('');
    setLoading(true);

    try {
      const res = await fetch('/api/alerts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          commodity_id: cropId,
          district_id: districtId,
          threshold_price: parseFloat(thresholdPrice),
          direction: direction,
        }),
      });

      if (!res.ok) {
        throw new Error('Failed to create price alert');
      }

      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        setCropId('');
        setDistrictId('');
        setThresholdPrice('');
        setDirection('above');
        setShowAlertModal(false);
      }, 3000);
    } catch (err) {
      setError(err.message || 'Error occurred while saving alert.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-md bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-100 flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-gradient-to-r from-emerald-500 to-teal-600 text-white">
          <div>
            <h3 className="font-bold text-lg">{t('alertFormTitle')}</h3>
            <p className="text-xs text-emerald-100/90 mt-0.5">{t('alertFormSubtitle')}</p>
          </div>
          <button 
            onClick={() => { setShowAlertModal(false); setError(''); }}
            className="text-white/80 hover:text-white transition-colors p-1 bg-white/10 hover:bg-white/25 rounded-full"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto">
          {success ? (
            <div className="flex flex-col items-center justify-center py-8 text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center border border-emerald-100 animate-bounce">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <p className="text-sm font-semibold text-slate-800">{t('alertSuccess')}</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="p-3 text-xs bg-rose-50 text-rose-600 border border-rose-100 rounded-lg font-medium">
                  {error}
                </div>
              )}

              {/* Crop select */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">
                  {t('selectCrop')} *
                </label>
                <select
                  required
                  value={cropId}
                  onChange={(e) => setCropId(e.target.value)}
                  className="w-full p-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all bg-slate-50"
                >
                  <option value="">-- {t('selectCrop')} --</option>
                  {crops.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name_en} ({c.name_ml})
                    </option>
                  ))}
                </select>
              </div>

              {/* District select */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">
                  {t('selectDistrict')} *
                </label>
                <select
                  required
                  value={districtId}
                  onChange={(e) => setDistrictId(e.target.value)}
                  className="w-full p-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all bg-slate-50"
                >
                  <option value="">-- {t('selectDistrict')} --</option>
                  {districts.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name_en} ({d.name_ml})
                    </option>
                  ))}
                </select>
              </div>

              {/* Condition / Direction selection */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">
                  {t('alertCondition')}
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setDirection('above')}
                    className={`p-3 text-sm font-semibold rounded-xl border transition-all cursor-pointer ${
                      direction === 'above'
                        ? 'border-emerald-500 bg-emerald-50 text-emerald-700 font-bold'
                        : 'border-slate-200 bg-slate-50 text-slate-600'
                    }`}
                  >
                    {t('alertAbove').split(' (')[0]}
                  </button>
                  <button
                    type="button"
                    onClick={() => setDirection('below')}
                    className={`p-3 text-sm font-semibold rounded-xl border transition-all cursor-pointer ${
                      direction === 'below'
                        ? 'border-emerald-500 bg-emerald-50 text-emerald-700 font-bold'
                        : 'border-slate-200 bg-slate-50 text-slate-600'
                    }`}
                  >
                    {t('alertBelow').split(' (')[0]}
                  </button>
                </div>
              </div>

              {/* Threshold Price Input */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">
                  {t('alertFormTitle').split('Alert')[0] || t('alertFormTitle')} {t('enterPrice').toLowerCase()} *
                </label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 font-semibold text-sm">
                    ₹
                  </span>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    required
                    placeholder="0.00"
                    value={thresholdPrice}
                    onChange={(e) => setThresholdPrice(e.target.value)}
                    className="w-full pl-8 p-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all bg-slate-50 font-medium"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white font-semibold rounded-xl text-sm shadow-md transition-all duration-200 hover:shadow-emerald-500/10 cursor-pointer disabled:opacity-50 flex items-center justify-center"
              >
                {loading ? (
                  <svg className="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                ) : (
                  t('setAlertAction')
                )}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
