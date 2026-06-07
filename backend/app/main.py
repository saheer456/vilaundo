from fastapi import FastAPI
from datetime import date

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/prices/today")
async def prices_today(district: str = None):
    """Stub endpoint: replace with real DB query later."""
    return {
        "date": date.today().isoformat(),
        "district": district or "All",
        "prices": []
    }
