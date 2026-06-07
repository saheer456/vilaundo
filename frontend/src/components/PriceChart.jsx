import React, { useState, useRef } from 'react';

export default function PriceChart({ history }) {
  if (!history || history.length === 0) {
    return <div className="h-48 flex items-center justify-center text-slate-400 text-sm">No price history available</div>;
  }

  const [hoveredIndex, setHoveredIndex] = useState(null);
  const containerRef = useRef(null);

  const width = 500;
  const height = 220;
  const padding = { top: 20, right: 20, bottom: 40, left: 55 };

  const prices = history.map((h) => h.price_modal || 0);
  const maxPrice = Math.max(...prices);
  const minPrice = Math.min(...prices);
  const range = maxPrice - minPrice;
  
  // y-axis limits with 10% padding
  const paddingY = range * 0.1 || 10;
  const minY = Math.max(0, minPrice - paddingY);
  const maxY = maxPrice + paddingY;

  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const getX = (i) => padding.left + (i / (history.length - 1)) * chartWidth;
  const getY = (val) => padding.top + chartHeight - ((val - minY) / (maxY - minY)) * chartHeight;

  // Path data
  const points = history.map((h, i) => ({
    x: getX(i),
    y: getY(h.price_modal || 0),
    price: h.price_modal,
    date: h.date,
  }));

  const lineD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  const areaD = `${lineD} L ${getX(history.length - 1)} ${padding.top + chartHeight} L ${getX(0)} ${padding.top + chartHeight} Z`;

  // Handle Mouse Hover to find the closest data point
  const handleMouseMove = (e) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const mouseX = ((e.clientX - rect.left) / rect.width) * width;
    
    // Find closest point by x coordinate
    let closestIndex = 0;
    let minDiff = Infinity;
    points.forEach((p, idx) => {
      const diff = Math.abs(p.x - mouseX);
      if (diff < minDiff) {
        minDiff = diff;
        closestIndex = idx;
      }
    });
    setHoveredIndex(closestIndex);
  };

  const handleMouseLeave = () => {
    setHoveredIndex(null);
  };

  // Y-axis grid lines
  const gridCount = 4;
  const gridLines = [];
  for (let i = 0; i <= gridCount; i++) {
    const val = minY + (i / gridCount) * (maxY - minY);
    gridLines.push(val);
  }

  // Format dates for X-axis (e.g. "Jun 05")
  const formatDate = (dateStr) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="w-full bg-slate-50/50 rounded-xl p-4 border border-slate-100/50">
      <div 
        ref={containerRef}
        className="relative cursor-crosshair"
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
        <svg 
          viewBox={`0 0 ${width} ${height}`} 
          className="w-full h-auto overflow-visible"
        >
          {/* Gradients */}
          <defs>
            <linearGradient id="chart-area-grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#10b981" stopOpacity="0.00" />
            </linearGradient>
          </defs>

          {/* Grid lines & Y-axis labels */}
          {gridLines.map((val, idx) => {
            const y = getY(val);
            return (
              <g key={idx} className="opacity-40">
                <line 
                  x1={padding.left} 
                  y1={y} 
                  x2={width - padding.right} 
                  y2={y} 
                  stroke="#cbd5e1" 
                  strokeDasharray="2 4"
                  strokeWidth="1"
                />
                <text 
                  x={padding.left - 8} 
                  y={y + 4} 
                  textAnchor="end" 
                  fill="#64748b" 
                  className="text-[10px] font-medium"
                >
                  ₹{Math.round(val)}
                </text>
              </g>
            );
          })}

          {/* Area fill */}
          <path d={areaD} fill="url(#chart-area-grad)" />

          {/* Line stroke */}
          <path 
            d={lineD} 
            fill="none" 
            stroke="#10b981" 
            strokeWidth="2.5" 
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* X-axis labels */}
          {points.length > 1 && (
            <>
              {/* Start Date */}
              <text 
                x={points[0].x} 
                y={height - padding.bottom + 18} 
                textAnchor="start" 
                fill="#64748b" 
                className="text-[10px] font-medium"
              >
                {formatDate(points[0].date)}
              </text>
              {/* Mid Date */}
              <text 
                x={points[Math.floor(points.length / 2)].x} 
                y={height - padding.bottom + 18} 
                textAnchor="middle" 
                fill="#64748b" 
                className="text-[10px] font-medium"
              >
                {formatDate(points[Math.floor(points.length / 2)].date)}
              </text>
              {/* End Date */}
              <text 
                x={points[points.length - 1].x} 
                y={height - padding.bottom + 18} 
                textAnchor="end" 
                fill="#64748b" 
                className="text-[10px] font-medium"
              >
                {formatDate(points[points.length - 1].date)}
              </text>
            </>
          )}

          {/* Interactive Hover Line and Info Dot */}
          {hoveredIndex !== null && (
            <g>
              <line 
                x1={points[hoveredIndex].x} 
                y1={padding.top} 
                x2={points[hoveredIndex].x} 
                y2={height - padding.bottom} 
                stroke="#10b981" 
                strokeWidth="1.5" 
                strokeDasharray="3 3"
              />
              <circle 
                cx={points[hoveredIndex].x} 
                cy={points[hoveredIndex].y} 
                r="6" 
                fill="#10b981" 
                stroke="#ffffff" 
                strokeWidth="2"
              />
            </g>
          )}
        </svg>

        {/* Floating Tooltip in HTML for absolute flexibility */}
        {hoveredIndex !== null && points[hoveredIndex] && (
          <div 
            className="absolute z-10 bg-slate-900 text-white text-xs rounded-lg px-2.5 py-1.5 shadow-md pointer-events-none transform -translate-x-1/2 -translate-y-full border border-slate-700/50"
            style={{
              left: `${(points[hoveredIndex].x / width) * 100}%`,
              top: `${(points[hoveredIndex].y / height) * 100 - 8}%`,
            }}
          >
            <div className="font-semibold">₹{points[hoveredIndex].price}</div>
            <div className="text-[10px] text-slate-300 font-medium whitespace-nowrap">
              {formatDate(points[hoveredIndex].date)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
