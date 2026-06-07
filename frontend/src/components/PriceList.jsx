import React from 'react';
import PriceCard from './PriceCard';

export default function PriceList({ items, activeDistrict }) {
  if (!items || items.length === 0) {
    return (
      <div className="py-12 flex flex-col items-center justify-center text-slate-400 space-y-2 border border-dashed border-slate-200 rounded-2xl bg-slate-50/50">
        <svg className="w-10 h-10 stroke-current text-slate-300" fill="none" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span className="text-sm font-semibold text-slate-500">No prices available for this selection</span>
        <span className="text-xs text-slate-400">Try changing your filters or searching for something else.</span>
      </div>
    );
  }

  return (
    <div className="space-y-3.5">
      {items.map((item) => (
        <PriceCard 
          key={item.commodity_id || item.name_en} 
          item={item} 
          activeDistrict={activeDistrict} 
        />
      ))}
    </div>
  );
}
