from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
from dotenv import load_dotenv

from market_data import get_price_history
from technical_desk import compute_technical_score
from sentiment_desk import compute_sentiment_score


# -------------------------
# LOAD ENVIRONMENT VARIABLES
# -------------------------

load_dotenv()


# -------------------------
# CREATE FASTAPI APP
# -------------------------

app = FastAPI()


# -------------------------
# CORS
# -------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# DATABASE CONNECTION
# -------------------------

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
    )


# -------------------------
# ROOT ENDPOINT
# -------------------------

@app.get("/")
def read_root():
    return {
        "message": "Caliper backend is running"
    }


# -------------------------
# GET STOCKS
# -------------------------

@app.get("/stocks")
def get_stocks():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT stock_id, ticker, company_name, sector
        FROM Stocks;
        """
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


# -------------------------
# GET PRICE HISTORY
# -------------------------

@app.get("/prices/{ticker}")
def get_prices(ticker: str):

    data = get_price_history(ticker)

    if data is None:
        return {
            "error": f"No data found for {ticker}"
        }

    return {
        "ticker": ticker.upper(),
        "history": data
    }


# -------------------------
# TECHNICAL DESK
# -------------------------

@app.get("/technical/{ticker}")
def get_technical(ticker: str):

    result = compute_technical_score(ticker)

    if result is None:
        return {
            "error": f"No technical data found for {ticker}"
        }

    return result


# -------------------------
# SENTIMENT DESK
# -------------------------

@app.get("/sentiment/{ticker}")
def get_sentiment(ticker: str):

    # Temporary ticker-to-company mapping
    company_names = {
        "TCS": "Tata Consultancy Services",
        "INFY": "Infosys",
        "RELIANCE": "Reliance Industries",
        "HDFCBANK": "HDFC Bank",
        "ICICIBANK": "ICICI Bank",
        "SBIN": "State Bank of India",
        "WIPRO": "Wipro",
        "ITC": "ITC Limited",
        "HINDUNILVR": "Hindustan Unilever",
        "BHARTIARTL": "Bharti Airtel",
        "PAYTM": "Paytm",
        "MARUTI": "Maruti Suzuki",
    }

    company_name = company_names.get(
        ticker.upper(),
        ticker
    )

    result = compute_sentiment_score(
        company_name,
        ticker
    )

    if result is None:
        return {
            "error": f"No news found for {ticker}"
        }

    return result