import React from 'react';

export default function TrendBadge({ change, percent, trend }) {
  if (trend === 'up') {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
        <svg className="w-3 h-3 mr-1 fill-current" viewBox="0 0 24 24">
          <path d="M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z" />
        </svg>
        +{change !== null && change !== undefined ? `₹${Math.abs(change)}` : ''}
        {percent !== null && percent !== undefined ? ` (${percent}%)` : ''}
      </span>
    );
  }

  if (trend === 'down') {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
        <svg className="w-3 h-3 mr-1 fill-current" viewBox="0 0 24 24">
          <path d="M20 12l-1.41-1.41L13 16.17V4h-2v12.17l-5.58-5.59L4 12l8 8 8-8z" />
        </svg>
        -{change !== null && change !== undefined ? `₹${Math.abs(change)}` : ''}
        {percent !== null && percent !== undefined ? ` (${percent}%)` : ''}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-slate-50 text-slate-600 border border-slate-200">
      <svg className="w-3 h-3 mr-1 fill-current" viewBox="0 0 24 24">
        <path d="M22 12l-4-4v3H3v2h15v3l4-4z" />
      </svg>
      0.00
    </span>
  );
}
