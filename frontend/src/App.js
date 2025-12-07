// frontend/src/App.js
import React, { useState } from "react";
import FetchForm from "./components/FetchForm";
import ResultModal from "./components/ResultModal";
import { fetchAndAnalyze, getPreview } from "./api";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [preview, setPreview] = useState(null);
  const [open, setOpen] = useState(false);

  async function handleFetch(payload) {
    setLoading(true);
    try {
      const res = await fetchAndAnalyze(payload);
      const prev = await getPreview(10);
      setResult(res);
      setPreview(prev);
      setOpen(true);
    } catch (err) {
      console.error(err);
      alert("Error fetching/analyzing. See console.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1>Reddit Fetch & Analyze</h1>
      <p>Enter subreddit and keyword — backend will fetch posts, analyze, and save results in Docker volume.</p>

      <FetchForm onSubmit={handleFetch} />

      {loading && <div className="loading">Fetching & Analyzing... (this may take a few seconds)</div>}

      <ResultModal open={open} onClose={() => setOpen(false)} result={result || {}} preview={preview}/>

      <footer style={{marginTop: 24}}>
        <small>Shadow — FastAPI backend + React frontend. Docker volume stores data.</small>
      </footer>
    </div>
  );
}
