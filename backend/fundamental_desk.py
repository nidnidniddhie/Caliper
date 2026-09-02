import yfinance as yf

def compute_fundamental_score(ticker: str):
    nse_ticker = f"{ticker.upper()}.NS"
    stock = yf.Ticker(nse_ticker)
    info = stock.info

    pe_ratio = info.get("trailingPE")
    roe = info.get("returnOnEquity")  # comes as a decimal, e.g. 0.18 = 18%
    eps = info.get("trailingEps")
    debt_to_equity = info.get("debtToEquity")

    if pe_ratio is None and roe is None and eps is None:
        return None  # not enough data to score meaningfully

    score = 50  # neutral baseline

    # PE ratio: lower is generally more attractive (very rough heuristic)
    if pe_ratio is not None:
        if pe_ratio < 20:
            score += 15
        elif pe_ratio > 40:
            score -= 15

    # ROE: higher is better
    if roe is not None:
        if roe > 0.15:
            score += 15
        elif roe < 0.05:
            score -= 15

    # Debt to equity: lower is safer
    if debt_to_equity is not None:
        if debt_to_equity < 50:
            score += 10
        elif debt_to_equity > 150:
            score -= 10

    score = max(0, min(100, score))

    explanation = generate_explanation(pe_ratio, roe, debt_to_equity)

    return {
        "ticker": ticker.upper(),
        "pe_ratio": round(pe_ratio, 2) if pe_ratio else None,
        "roe": round(roe * 100, 2) if roe else None,  # show as %
        "eps": round(eps, 2) if eps else None,
        "debt_to_equity": round(debt_to_equity, 2) if debt_to_equity else None,
        "fundamental_score": score,
        "explanation": explanation,
    }


def generate_explanation(pe_ratio, roe, debt_to_equity):
    parts = []

    if pe_ratio is not None:
        if pe_ratio < 20:
            parts.append("the company continues to trade below typical valuation levels for its sector")
        elif pe_ratio > 40:
            parts.append("valuation is elevated relative to historical norms")
        else:
            parts.append("valuation sits within a reasonable range")

    if roe is not None:
        if roe > 0.15:
            parts.append("return on equity remains strong, reflecting efficient use of capital")
        elif roe < 0.05:
            parts.append("return on equity is weaker than what we'd want to see")

    if not parts:
        return "Limited fundamental data is available for a confident read."

    return " — ".join(parts).capitalize() + "."


if __name__ == "__main__":
    result = compute_fundamental_score("TCS")
    print(result)