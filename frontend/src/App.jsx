import { useEffect, useState } from "react";

function App() {
  const [stocks, setStocks] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState("");
  const [priceData, setPriceData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch stocks from database
  useEffect(() => {
    fetch("http://127.0.0.1:8000/stocks")
      .then((res) => res.json())
      .then((data) => setStocks(data))
      .catch((err) => console.error("Failed to fetch stocks:", err));
  }, []);

  // Fetch price history
  const handleSearch = (ticker) => {
    if (!ticker) return;

    setSelectedTicker(ticker);
    setLoading(true);
    setPriceData(null);

    fetch(`http://127.0.0.1:8000/prices/${ticker}`)
      .then((res) => res.json())
      .then((data) => {
        setPriceData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch prices:", err);
        setLoading(false);
      });
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Caliper</h1>
      <p>Measure conviction. Not speculation.</p>

      <h2>Search a Stock</h2>

      <select
        value={selectedTicker}
        onChange={(e) => handleSearch(e.target.value)}
      >
        <option value="">Select a stock</option>

        {stocks.map((s) => (
          <option key={s.stock_id} value={s.ticker}>
            {s.ticker} — {s.company_name}
          </option>
        ))}
      </select>

      {loading && <p>Loading price data...</p>}

      {priceData && priceData.error && (
        <p style={{ color: "red" }}>
          {priceData.error}
        </p>
      )}

      {priceData && priceData.history && (
        <div style={{ marginTop: "1.5rem" }}>
          <h3>{priceData.ticker} — Recent Prices</h3>

          <table
            border="1"
            cellPadding="6"
            style={{ borderCollapse: "collapse" }}
          >
            <thead>
              <tr>
                <th>Date</th>
                <th>Open</th>
                <th>High</th>
                <th>Low</th>
                <th>Close</th>
                <th>Volume</th>
              </tr>
            </thead>

            <tbody>
              {priceData.history
                .slice(-10)
                .reverse()
                .map((row) => (
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

      <h2 style={{ marginTop: "2rem" }}>Stocks in DB</h2>

      <ul>
        {stocks.map((s) => (
          <li key={s.stock_id}>
            {s.ticker} — {s.company_name} ({s.sector})
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;