import React from "react"

export default function PriceCard({item}){
  return (
    <div className="p-4 border rounded shadow-sm bg-white">
      <div className="flex justify-between items-center">
        <div>
          <div className="font-semibold">{item.name_en} — {item.name_ml}</div>
          <div className="text-sm text-gray-500">{item.category} • {item.unit}</div>
        </div>
        <div className="text-right">
          <div className="text-lg font-medium">₹{item.price_modal ?? '-'}</div>
          <div className="text-sm">{item.trend || ''}</div>
        </div>
      </div>
    </div>
  )
}
