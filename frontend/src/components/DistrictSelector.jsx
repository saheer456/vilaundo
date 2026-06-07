import React from "react"

export default function DistrictSelector({districts, value, onChange}){
  return (
    <select className="p-2 border rounded" value={value} onChange={e=>onChange(e.target.value)}>
      <option value="">All Districts</option>
      {districts.map(d=> <option key={d.id} value={d.name_en}>{d.name_en}</option>)}
    </select>
  )
}
