// frontend/src/components/ResultModal.js
import React from "react";

export default function ResultModal({ open, onClose, result, preview }) {
  if (!open) return null;

  const BACKEND_URL =
    process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

  // Ensure paths are absolute URLs
  const topWordsChart = result?.charts?.top_words_chart
    ? BACKEND_URL + result.charts.top_words_chart
    : null;

  const postsByDateChart = result?.charts?.posts_by_date_chart
    ? BACKEND_URL + result.charts.posts_by_date_chart
    : null;

  const sentimentCSV = result?.sentiment_csv
    ? BACKEND_URL + result.sentiment_csv
    : null;

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <h3>Fetch & Analysis Complete</h3>
        <p>
          Fetched posts: <strong>{result.fetched}</strong>
        </p>
        <p>
          Analyzed posts: <strong>{result.analyzed}</strong>
        </p>
        <p>
          Average sentiment: <strong>{result.avg_sentiment}</strong>
        </p>

        <h4>Top words</h4>
        <ul>
          {result.top_words &&
            result.top_words.map((w, idx) => (
              <li key={idx}>
                {w[0]} — {w[1]}
              </li>
            ))}
        </ul>

        <h4>Charts</h4>

        {topWordsChart && (
          <img
            src={topWordsChart}
            alt="Top words chart"
            style={{ maxWidth: "100%", borderRadius: 6 }}
          />
        )}

        {postsByDateChart && (
          <img
            src={postsByDateChart}
            alt="Posts by date"
            style={{ maxWidth: "100%", marginTop: 12, borderRadius: 6 }}
          />
        )}

        <h4>Preview (first rows)</h4>
        <div className="preview">
          <table>
            <thead>
              <tr>
                <th>title</th>
                <th>score</th>
                <th>num_comments</th>
                <th>created_utc</th>
              </tr>
            </thead>
            <tbody>
              {preview &&
                preview.preview &&
                preview.preview.map((r, i) => (
                  <tr key={i}>
                    <td>{r.title}</td>
                    <td>{r.score}</td>
                    <td>{r.num_comments}</td>
                    <td>{r.created_utc}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>

        <div style={{ marginTop: 12 }}>
          {sentimentCSV && (
            <a href={sentimentCSV} target="_blank" rel="noreferrer">
              Download CSV with sentiment
            </a>
          )}
        </div>

        <div style={{ marginTop: 14 }}>
          <button onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
