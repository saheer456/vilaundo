import React, {useState, useEffect} from "react"
import PriceList from "./components/PriceList"

export default function App(){
  const [items, setItems] = useState([])
  useEffect(()=>{
    fetch('/api/prices/today').then(r=>r.json()).then(d=>setItems(d.prices || []))
  },[])

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">VilaUndo</h1>
      <PriceList items={items} />
    </div>
  )
}
