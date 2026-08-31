from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
from dotenv import load_dotenv

from market_data import get_price_history

load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database connection
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
    )


# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Caliper backend is running"}


# Get stocks from database
@app.get("/stocks")
def get_stocks():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT stock_id, ticker, company_name, sector FROM Stocks;"
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "stock_id": r[0],
            "ticker": r[1],
            "company_name": r[2],
            "sector": r[3]
        }
        for r in rows
    ]


# Get price history
@app.get("/prices/{ticker}")
def get_prices(ticker: str):
    data = get_price_history(ticker)

    if data is None:
        return {"error": f"No data found for {ticker}"}

    return {
        "ticker": ticker.upper(),
        "history": data
    }