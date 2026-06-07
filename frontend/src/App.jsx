import React, {useState, useEffect} from "react"
import PriceList from "./components/PriceList"

export default function App(){
  const [items, setItems] = useState([])
  const base = import.meta.env.VITE_API_URL || ''
  useEffect(()=>{
    fetch(`${base}/api/prices/today`).then(r=>r.json()).then(d=>setItems(d.prices || []))
  },[])

  return (
    <div className="container">
      <h1 className="text-2xl font-bold mb-4">VilaUndo</h1>
      <div className="card">
        <PriceList items={items} />
      </div>
    </div>
  )
}
