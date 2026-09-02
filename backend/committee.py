import numpy as np
import psycopg2
import os
from datetime import date
from dotenv import load_dotenv
from technical_desk import compute_technical_score
from sentiment_desk import compute_sentiment_score
from fundamental_desk import compute_fundamental_score
from market_data import get_price_history

load_dotenv()

COMPANY_NAMES = {
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

WEIGHTS = {
    "technical": 0.35,
    "fundamental": 0.30,
    "sentiment": 0.20,
    "risk": 0.15,
}

DISAGREEMENT_THRESHOLD = 25


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
    )


def save_signal_to_db(ticker: str, verdict: dict):
    """Persist today's Committee verdict into the Signals table."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT stock_id FROM Stocks WHERE ticker = %s;", (ticker.upper(),))
    row = cur.fetchone()
    if row is None:
        cur.close()
        conn.close()
        return

    stock_id = row[0]
    today = date.today()

    cur.execute("""
        INSERT INTO Signals
        (stock_id, date, technical_score, sentiment_score, fundamental_score, risk_score, caliper_score, verdict_tier, explanation_text)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        stock_id,
        today,
        verdict["desk_scores"]["technical"],
        verdict["desk_scores"]["sentiment"],
        verdict["desk_scores"]["fundamental"],
        verdict["desk_scores"]["risk"],
        verdict["caliper_score"],
        verdict["verdict_tier"],
        verdict["committee_explanation"],
    ))

    conn.commit()
    cur.close()
    conn.close()


def compute_risk_score(ticker: str):
    history = get_price_history(ticker, period="3mo")
    if not history or len(history) < 10:
        return 50

    closes = [h["close"] for h in history]
    returns = np.diff(closes) / np.array(closes[:-1])
    volatility = np.std(returns) * 100

    if volatility < 1.0:
        return 80
    elif volatility < 2.0:
        return 60
    elif volatility < 3.5:
        return 40
    else:
        return 20


def get_committee_verdict(ticker: str):
    company_name = COMPANY_NAMES.get(ticker.upper(), ticker)

    technical = compute_technical_score(ticker)
    sentiment = compute_sentiment_score(company_name, ticker)
    fundamental = compute_fundamental_score(ticker)
    risk_score = compute_risk_score(ticker)

    if technical is None or fundamental is None:
        return {"error": f"Not enough data to form a Committee view on {ticker}"}

    sentiment_score = sentiment["sentiment_score"] if sentiment else 50

    scores = {
        "technical": technical["technical_score"],
        "fundamental": fundamental["fundamental_score"],
        "sentiment": sentiment_score,
        "risk": risk_score,
    }

    caliper_score = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
    caliper_score = round(caliper_score, 1)

    evidence_scores = {
        "technical": scores["technical"],
        "fundamental": scores["fundamental"],
        "sentiment": scores["sentiment"],
    }
    spread = max(evidence_scores.values()) - min(evidence_scores.values())
    disagreement = spread >= DISAGREEMENT_THRESHOLD

    if disagreement:
        verdict_tier = "No Trade"
    elif caliper_score >= 75:
        verdict_tier = "High Conviction Buy"
    elif caliper_score >= 60:
        verdict_tier = "Watchlist"
    elif caliper_score >= 40:
        verdict_tier = "Exit Candidate"
    else:
        verdict_tier = "Risk Alert"

    explanation = generate_committee_explanation(verdict_tier, evidence_scores, disagreement)

    result = {
        "ticker": ticker.upper(),
        "desk_scores": scores,
        "caliper_score": caliper_score,
        "verdict_tier": verdict_tier,
        "committee_explanation": explanation,
        "desk_details": {
            "technical": technical,
            "sentiment": sentiment,
            "fundamental": fundamental,
        },
    }

    save_signal_to_db(ticker, result)

    return result


def generate_committee_explanation(verdict_tier, evidence_scores, disagreement):
    if verdict_tier == "No Trade":
        strongest = max(evidence_scores, key=evidence_scores.get)
        weakest = min(evidence_scores, key=evidence_scores.get)
        return (
            f"{strongest.capitalize()} evidence is notably stronger than {weakest} evidence right now. "
            "The picture is improving in places, but it hasn't converged. Conviction is earned through "
            "agreement — not optimism."
        )
    elif verdict_tier == "High Conviction Buy":
        return (
            "Independent desks identified different angles, but none found a structural reason to avoid "
            "the position. The evidence is unusually aligned."
        )
    elif verdict_tier == "Watchlist":
        return (
            "The setup is reasonable but not yet strong enough across all desks to warrant high conviction. "
            "Worth tracking as the picture develops."
        )
    elif verdict_tier == "Exit Candidate":
        return (
            "Evidence quality has weakened across the board. This isn't a panic signal, but the case for "
            "holding is no longer strong."
        )
    else:
        return (
            "Multiple desks are flagging concern simultaneously. This warrants caution rather than a "
            "wait-and-see approach."
        )


if __name__ == "__main__":
    result = get_committee_verdict("TCS")
    print(result)