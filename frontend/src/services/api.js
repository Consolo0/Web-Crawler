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
    const response = await api.post('/crawler', {
      query,
      restrictions,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const crawlStream = async function* (query, restrictions = {}) {
  const response = await fetch(`${API_URL}/api/${API_VERSION}/crawler/stream`, {
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
  let buffer = ''; // CRITICAL: Buffer to accumulate incomplete lines

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      // Decode chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });

      // Split by newlines
      const lines = buffer.split('\n');
      
      // Keep the last incomplete line in buffer
      buffer = lines.pop() || '';

      // Process complete lines
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const jsonData = line.substring(6).trim();
            if (jsonData) {
              const data = JSON.parse(jsonData);
              yield data;
            }
          } catch (e) {
            console.error('Failed to parse SSE data:', line, e);
          }
        }
        // Ignore 'event:' lines and empty lines
      }
    }
    
    // Process any remaining data in buffer
    if (buffer.trim() && buffer.startsWith('data: ')) {
      try {
        const jsonData = buffer.substring(6).trim();
        if (jsonData) {
          const data = JSON.parse(jsonData);
          yield data;
        }
      } catch (e) {
        console.error('Failed to parse final SSE data:', buffer, e);
      }
    }
  } finally {
    reader.releaseLock();
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
