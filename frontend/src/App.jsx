import React, {useState, useEffect} from "react"
import PriceList from "./components/PriceList"

export default function App(){
  const [items, setItems] = useState([])
  // Normalize base URL (remove trailing slash) so concatenation is safe
  const base = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

  useEffect(() => {
    const controller = new AbortController()

    const load = async () => {
      try {
        const res = await fetch(`${base}/api/prices/today`, { signal: controller.signal })
        if (!res.ok) {
          // handle non-2xx responses gracefully
          console.error('Failed to fetch prices:', res.status, res.statusText)
          setItems([])
          return
        }
        const d = await res.json()
        setItems(d.prices || [])
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Error fetching prices:', err)
          setItems([])
        }
      }
    }

    load()
    return () => controller.abort()
  }, [base])

  return (
    <div className="container">
      <h1 className="text-2xl font-bold mb-4">VilaUndo</h1>
      <div className="card">
        <PriceList items={items} />
      </div>
    </div>
  )
}
