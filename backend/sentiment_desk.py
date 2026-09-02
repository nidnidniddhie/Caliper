from transformers import pipeline
from news_fetch import get_news_headlines

# Load once at module level — reused across requests, avoids reloading the model every call
_finbert = pipeline("sentiment-analysis", model="ProsusAI/finbert")

def compute_sentiment_score(company_name: str, ticker: str):
    headlines = get_news_headlines(company_name)

    if not headlines:
        return None

    results = _finbert(headlines)

    pos_count = sum(1 for r in results if r["label"] == "positive")
    neg_count = sum(1 for r in results if r["label"] == "negative")
    neu_count = sum(1 for r in results if r["label"] == "neutral")
    total = len(results)

    # Score: start neutral, shift based on positive/negative balance
    score = 50 + ((pos_count - neg_count) / total) * 50
    score = max(0, min(100, round(score)))

    explanation = generate_explanation(pos_count, neg_count, neu_count, total)

    return {
        "ticker": ticker.upper(),
        "headlines_analyzed": total,
        "positive": pos_count,
        "negative": neg_count,
        "neutral": neu_count,
        "sentiment_score": score,
        "explanation": explanation,
        "sample_headlines": headlines[:3],
    }


def generate_explanation(pos, neg, neu, total):
    if pos > neg and pos >= total * 0.4:
        return "Recent coverage leans positive. Earnings and business updates are shaping the narrative more than speculative concerns."
    elif neg > pos and neg >= total * 0.4:
        return "Recent coverage leans negative. Concerns are showing up more consistently than reassurance across recent headlines."
    else:
        return "Coverage is mixed, with no dominant narrative pulling sentiment clearly in one direction."


if __name__ == "__main__":
    result = compute_sentiment_score("Tata Consultancy Services", "TCS")
    print(result)