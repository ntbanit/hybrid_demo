import { useState } from "react";
import axios from "axios";

const API = "http://localhost:8000";

export default function App() {
  const [query,   setQuery]   = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState("");

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true); setError("");
    try {
      const { data } = await axios.post(`${API}/search`, { query, top_k: 5 });
      setResults(data.results);
    } catch (e) {
      setError("Search failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "40px auto", fontFamily: "sans-serif", padding: "0 20px" }}>
      <h1>🔍 RAG Hybrid Search</h1>
      <p style={{ color: "#666" }}>Searches PostgreSQL (pgvector) + Elasticsearch + Weaviate — fused with RRF</p>

      <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === "Enter" && search()}
          placeholder="Ask anything about your documents..."
          style={{ flex: 1, padding: "10px 14px", fontSize: 16, borderRadius: 8, border: "1px solid #ccc" }}
        />
        <button
          onClick={search}
          disabled={loading}
          style={{ padding: "10px 24px", background: "#2563eb", color: "#fff",
                   border: "none", borderRadius: 8, fontSize: 16, cursor: "pointer" }}>
          {loading ? "…" : "Search"}
        </button>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {results.map((r, i) => (
        <div key={i} style={{
          border: "1px solid #e5e7eb", borderRadius: 10, padding: 16,
          marginBottom: 12, background: "#fafafa"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
            <span style={{ fontWeight: 600, color: "#374151" }}>📄 {r.source}</span>
            <span style={{ fontSize: 12, color: "#6b7280" }}>
              RRF: {r.rrf_score.toFixed(4)}
            </span>
          </div>
          <p style={{ margin: 0, color: "#1f2937", lineHeight: 1.6 }}>{r.content}</p>
        </div>
      ))}

      {!loading && results.length === 0 && query && (
        <p style={{ color: "#9ca3af" }}>No results found.</p>
      )}
    </div>
  );
}