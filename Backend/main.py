from fastapi import FastAPI, HTTPException
import httpx
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for Dash frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://covid-dashboard.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fetch real-time COVID data from a public API
COVID_API_URL = "https://disease.sh/v3/covid-19/all"

@app.get("/covid-data")
async def get_covid_data():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(COVID_API_URL)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch COVID data")
