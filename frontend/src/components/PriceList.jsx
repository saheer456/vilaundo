import React from "react"
import PriceCard from './PriceCard'

export default function PriceList({items}){
  if(!items || items.length === 0) return <div className="p-4">No prices available</div>
  return (
    <div className="space-y-3">
      {items.map(i=> <PriceCard key={i.commodity_id || i.name_en} item={i} />)}
    </div>
  )
}
