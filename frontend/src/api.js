// frontend/src/api.js
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

export async function fetchAndAnalyze({ subreddit, keyword, limit }) {
  const resp = await axios.post(`${BACKEND_URL}/api/fetch`, { subreddit, keyword, limit });
  return resp.data;
}

export async function getPreview(nrows = 10) {
  const resp = await axios.get(`${BACKEND_URL}/api/preview?nrows=${nrows}`);
  return resp.data;
}
