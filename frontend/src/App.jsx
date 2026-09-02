import { useEffect, useState } from "react";

function App() {
  const [stocks, setStocks] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState("");
  const [priceData, setPriceData] = useState(null);
  const [committee, setCommittee] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/stocks")
      .then((res) => res.json())
      .then((data) => setStocks(data))
      .catch((err) => console.error("Failed to fetch stocks:", err));
  }, []);

  const handleSearch = (ticker) => {
    if (!ticker) return;
    setLoading(true);
    setSelectedTicker(ticker);
    setCommittee(null);
    setPriceData(null);

    fetch(`http://127.0.0.1:8000/prices/${ticker}`)
      .then((res) => res.json())
      .then((data) => setPriceData(data))
      .catch((err) => console.error("Failed to fetch prices:", err));

    fetch(`http://127.0.0.1:8000/committee/${ticker}`)
      .then((res) => res.json())
      .then((data) => {
        setCommittee(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch committee verdict:", err);
        setLoading(false);
      });
  };

  const tierColor = (tier) => {
    switch (tier) {
      case "High Conviction Buy": return "#10b981"; // emerald
      case "Watchlist": return "#3b82f6";
      case "Exit Candidate": return "#f59e0b";
      case "Risk Alert": return "#ef4444";
      case "No Trade": return "#9ca3af";
      default: return "#9ca3af";
    }
  };

  return (
    <div style={{
      padding: "2rem",
      fontFamily: "sans-serif",
      backgroundColor: "#0f1115",
      color: "#e5e7eb",
      minHeight: "100vh"
    }}>
      <h1 style={{ marginBottom: "0.25rem" }}>Caliper</h1>
      <p style={{ color: "#9ca3af", marginBottom: "1.5rem" }}>
        Measure conviction. Not speculation.
      </p>

      <h2 style={{ fontSize: "1rem", color: "#9ca3af" }}>Search a stock</h2>
      <select
        onChange={(e) => handleSearch(e.target.value)}
        defaultValue=""
        style={{ padding: "0.5rem", fontSize: "1rem", marginBottom: "1.5rem" }}
      >
        <option value="" disabled>Select a stock</option>
        {stocks.map((s) => (
          <option key={s.stock_id} value={s.ticker}>
            {s.ticker} — {s.company_name}
          </option>
        ))}
      </select>

      {loading && <p>Consulting the Committee...</p>}

      {committee && !committee.error && (
        <div style={{
          border: `1px solid ${tierColor(committee.verdict_tier)}`,
          borderRadius: "8px",
          padding: "1.5rem",
          maxWidth: "600px",
          marginBottom: "2rem",
          backgroundColor: "#161922"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h2 style={{ margin: 0 }}>{committee.ticker} · Investment Committee</h2>
            <span style={{
              color: tierColor(committee.verdict_tier),
              fontWeight: "bold",
              fontSize: "1.1rem"
            }}>
              {committee.verdict_tier}
            </span>
          </div>

          <p style={{ color: "#9ca3af", margin: "0.5rem 0 1rem 0" }}>
            Caliper Score: <strong style={{ color: "#e5e7eb" }}>{committee.caliper_score}</strong>
          </p>

          <p style={{ lineHeight: "1.6" }}>{committee.committee_explanation}</p>

          <hr style={{ borderColor: "#2a2e3a", margin: "1rem 0" }} />

          <h3 style={{ fontSize: "0.95rem", color: "#9ca3af" }}>Desk Opinions</h3>

          <div style={{ marginBottom: "0.75rem" }}>
            <strong>Technical Desk</strong> — {committee.desk_scores.technical}
            <p style={{ margin: "0.25rem 0", color: "#d1d5db" }}>
              {committee.desk_details.technical.explanation}
            </p>
          </div>

          <div style={{ marginBottom: "0.75rem" }}>
            <strong>Fundamental Research</strong> — {committee.desk_scores.fundamental}
            <p style={{ margin: "0.25rem 0", color: "#d1d5db" }}>
              {committee.desk_details.fundamental.explanation}
            </p>
          </div>

          <div style={{ marginBottom: "0.75rem" }}>
            <strong>Market Sentiment</strong> — {committee.desk_scores.sentiment}
            <p style={{ margin: "0.25rem 0", color: "#d1d5db" }}>
              {committee.desk_details.sentiment
                ? committee.desk_details.sentiment.explanation
                : "No sentiment data available."}
            </p>
          </div>
        </div>
      )}

      {committee && committee.error && (
        <p style={{ color: "#ef4444" }}>{committee.error}</p>
      )}

      {priceData && priceData.history && (
        <div style={{ marginTop: "1rem" }}>
          <h3>{priceData.ticker} — Recent Prices</h3>
          <table border="1" cellPadding="6" style={{ borderCollapse: "collapse", color: "#e5e7eb" }}>
            <thead>
              <tr>
                <th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th>
              </tr>
            </thead>
            <tbody>
              {priceData.history.slice(-10).reverse().map((row) => (
                <tr key={row.date}>
                  <td>{row.date}</td>
                  <td>{row.open}</td>
                  <td>{row.high}</td>
                  <td>{row.low}</td>
                  <td>{row.close}</td>
                  <td>{row.volume}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;