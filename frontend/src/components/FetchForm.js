// frontend/src/components/FetchForm.js
import React, { useState } from "react";

export default function FetchForm({ onSubmit }) {
  const [subreddit, setSubreddit] = useState("");
  const [keyword, setKeyword] = useState("");
  const [limit, setLimit] = useState(200);

  function handleSubmit(e) {
    e.preventDefault();
    if (!subreddit || !keyword) {
      alert("Enter both subreddit and keyword");
      return;
    }
    onSubmit({ subreddit, keyword, limit: parseInt(limit) });
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <label>Subreddit</label>
      <input value={subreddit} onChange={(e) => setSubreddit(e.target.value)} placeholder="e.g. technology" />
      <label>Keyword</label>
      <input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="e.g. ai" />
      <label>Limit (posts to scan)</label>
      <input type="number" value={limit} onChange={(e) => setLimit(e.target.value)} />
      <button type="submit">Fetch & Analyze</button>
    </form>
  );
}
