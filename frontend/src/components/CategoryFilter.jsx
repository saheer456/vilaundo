import React from 'react';
import { useTranslation } from 'react-i18next';
import { useAppStore } from '../store/useAppStore';

export default function CategoryFilter() {
  const { t } = useTranslation();
  const { category, setCategory } = useAppStore();

  const categories = [
    { key: 'all', label: t('allCategories') },
    { key: 'spices', label: t('spices') },
    { key: 'coconut', label: t('coconut') },
    { key: 'rubber', label: t('rubber') },
    { key: 'vegetables', label: t('vegetables') }
  ];

  return (
    <div className="w-full overflow-x-auto no-scrollbar py-1 flex items-center gap-2 border-b border-slate-100 mb-4">
      {categories.map((cat) => {
        const isActive = category === cat.key;
        return (
          <button
            key={cat.key}
            onClick={() => setCategory(cat.key)}
            className={`px-4 py-2 text-xs sm:text-sm font-semibold rounded-full border transition-all duration-200 whitespace-nowrap cursor-pointer select-none ${
              isActive
                ? 'bg-emerald-500 text-white border-emerald-500 shadow-sm shadow-emerald-500/15 font-bold scale-[1.02]'
                : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300 hover:bg-slate-50'
            }`}
          >
            {cat.label}
          </button>
        );
      })}
    </div>
  );
}
