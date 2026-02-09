import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_VERSION = process.env.REACT_APP_API_VERSION || 'v1';

const api = axios.create({
  baseURL: `${API_URL}/api/${API_VERSION}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const crawl = async (query, restrictions = {}) => {
  try {
    const response = await api.post('/crawl', {
      query,
      restrictions,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const crawlStream = async function* (query, restrictions = {}) {
  const response = await fetch(`${API_URL}/api/${API_VERSION}/crawl/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, restrictions }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.substring(6));
          yield data;
        } catch (e) {
          console.error('Failed to parse SSE data:', e);
        }
      }
    }
  }
};

export const checkHealth = async () => {
  try {
    const response = await axios.get(`${API_URL}/health`);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export default api;