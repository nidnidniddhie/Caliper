import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator

from market_data import get_price_history


def generate_explanation(rsi, macd_bullish, ema_bullish):
    """Generate a concise explanation in the Caliper voice."""

    if rsi < 30:
        rsi_note = "RSI has moved into oversold territory"
    elif rsi > 70:
        rsi_note = "RSI is currently in overbought territory"
    else:
        rsi_note = "RSI is holding in a neutral range"

    if macd_bullish and ema_bullish:
        confirmation = (
            "MACD and the EMA trend both support bullish momentum, "
            "adding confirmation to the signal"
        )
    elif macd_bullish or ema_bullish:
        confirmation = (
            "momentum signals are mixed, with only one of MACD or "
            "the EMA trend providing confirmation"
        )
    else:
        confirmation = (
            "MACD and the EMA trend are not currently confirming "
            "a bullish reversal"
        )

    return f"{rsi_note}. {confirmation}."


def compute_technical_score(ticker: str):

    # Fetch 6 months of historical data
    history = get_price_history(ticker, period="6mo")

    if not history:
        return None

    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(history)

    # Ensure close prices are numeric
    df["close"] = pd.to_numeric(
        df["close"],
        errors="coerce"
    )

    df = df.dropna(subset=["close"])

    # Need enough data for EMA-50
    if len(df) < 60:
        return None

    # -------------------------
    # RSI
    # -------------------------

    rsi_indicator = RSIIndicator(
        close=df["close"],
        window=14
    )

    df["rsi"] = rsi_indicator.rsi()

    latest_rsi = float(df["rsi"].iloc[-1])

    # -------------------------
    # MACD
    # -------------------------

    macd_indicator = MACD(
        close=df["close"]
    )

    df["macd"] = macd_indicator.macd()
    df["macd_signal"] = macd_indicator.macd_signal()

    latest_macd = float(df["macd"].iloc[-1])
    latest_macd_signal = float(df["macd_signal"].iloc[-1])

    macd_bullish = latest_macd > latest_macd_signal

    # -------------------------
    # EMA CROSSOVER
    # -------------------------

    ema20_series = EMAIndicator(
        close=df["close"],
        window=20
    ).ema_indicator()

    ema50_series = EMAIndicator(
        close=df["close"],
        window=50
    ).ema_indicator()

    latest_ema20 = float(ema20_series.iloc[-1])
    latest_ema50 = float(ema50_series.iloc[-1])

    ema_bullish = latest_ema20 > latest_ema50

    # -------------------------
    # TECHNICAL SCORE
    # -------------------------

    score = 50

    # RSI contribution
    if latest_rsi < 30:
        score += 20
    elif latest_rsi > 70:
        score -= 20

    # MACD contribution
    if macd_bullish:
        score += 15
    else:
        score -= 15

    # EMA contribution
    if ema_bullish:
        score += 15
    else:
        score -= 15

    # Keep score between 0 and 100
    score = max(0, min(100, score))

    # -------------------------
    # EXPLANATION
    # -------------------------

    explanation = generate_explanation(
        latest_rsi,
        macd_bullish,
        ema_bullish
    )

    # -------------------------
    # RETURN RESULT
    # -------------------------

    return {
        "ticker": ticker.upper(),

        "rsi": round(latest_rsi, 2),

        "macd": {
            "value": round(latest_macd, 4),
            "signal": round(latest_macd_signal, 4),
            "bullish": macd_bullish
        },

        "ema": {
            "ema20": round(latest_ema20, 2),
            "ema50": round(latest_ema50, 2),
            "bullish": ema_bullish
        },

        "technical_score": score,

        "explanation": explanation
    }


# -------------------------
# STANDALONE TEST
# -------------------------

if __name__ == "__main__":

    result = compute_technical_score("TCS")

    print("\nTECHNICAL DESK RESULT")
    print("======================")

    if result:
        print(result)
    else:
        print("No data found.")