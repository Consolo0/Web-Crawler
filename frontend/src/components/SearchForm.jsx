import React, { useState } from 'react';
import toast from 'react-hot-toast';
import AdvancedSettings from './AdvancedSettings';
import ResultsDisplay from './ResultsDisplay';
import { crawl, crawlStream } from '../services/api';

const SearchForm = () => {
  const [query, setQuery] = useState('');
  const [restrictions, setRestrictions] = useState({
    stop_criteria: {
      maximum_errors: 5,
    },
    navigation_strategy: {
      type: 'BFS',
      maximum_depth: 5,
      maximum_products_per_source: 10,
    },
  });
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [streamEvents, setStreamEvents] = useState([]);
  const [useStreaming, setUseStreaming] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (!query.trim()) {
      toast.error('Please insert a query, be as specific as possible', {
        duration: 4000,
        position: 'top-center',
        style: {
          background: '#ef4444',
          color: '#fff',
        },
      });
      return;
    }

    setIsLoading(true);
    setResults(null);
    setStreamEvents([]);

    try {
      if (useStreaming) {
        await handleStreamingCrawl();
      } else {
        await handleRegularCrawl();
      }
    } catch (error) {
      console.error('Crawl error:', error);
      toast.error(`Error: ${error.message || 'Something went wrong'}`, {
        duration: 5000,
        position: 'top-center',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegularCrawl = async () => {
    const toastId = toast.loading('Crawling in progress...', {
      position: 'top-center',
    });

    try {
      const data = await crawl(query, restrictions);
      setResults(data);
      
      toast.success('Crawl completed successfully!', {
        id: toastId,
        duration: 3000,
        position: 'top-center',
      });
    } catch (error) {
      toast.error('Crawl failed', { id: toastId });
      throw error;
    }
  };

  const handleStreamingCrawl = async () => {
    const toastId = toast.loading('Starting streaming crawl...', {
      position: 'top-center',
    });

    try {
      const events = [];
      
      for await (const event of crawlStream(query, restrictions)) {
        events.push(event);
        setStreamEvents([...events]);

        if (event.type === 'status') {
          toast.loading(event.message, { id: toastId });
        } else if (event.type === 'result') {
          toast.success('Results received!', { id: toastId, duration: 2000 });
        } else if (event.type === 'done') {
          toast.success('Streaming completed!', { id: toastId, duration: 3000 });
        }
      }
    } catch (error) {
      toast.error('Stream failed', { id: toastId });
      throw error;
    }
  };

  const handleReset = () => {
    setQuery('');
    setResults(null);
    setStreamEvents([]);
    setRestrictions({
      stop_criteria: {
        maximum_errors: 5,
      },
      navigation_strategy: {
        type: 'BFS',
        maximum_depth: 5,
        maximum_products_per_source: 10,
      },
    });
  };

  return (
    <div className="search-form-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-group">
          <label htmlFor="query">Search Query</label>
          <input
            id="query"
            type="text"
            placeholder="e.g., gaming laptop RTX 4070"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
            className="query-input"
          />
          <p className="hint">Be as specific as possible for better results</p>
        </div>

        <AdvancedSettings
          restrictions={restrictions}
          onChange={setRestrictions}
        />

        <div className="streaming-toggle">
          <label>
            <input
              type="checkbox"
              checked={useStreaming}
              onChange={(e) => setUseStreaming(e.target.checked)}
              disabled={isLoading}
            />
            Use streaming (real-time results)
          </label>
        </div>

        <div className="button-group">
          <button
            type="submit"
            disabled={isLoading}
            className="submit-button"
          >
            {isLoading ? 'Crawling...' : 'Start Crawl'}
          </button>

          <button
            type="button"
            onClick={handleReset}
            disabled={isLoading}
            className="reset-button"
          >
            Reset
          </button>
        </div>
      </form>

      {/* Results Display */}
      {results && <ResultsDisplay results={results} />}

      {/* Streaming Events Display */}
      {streamEvents.length > 0 && (
        <div className="results-container">
          <h2>Stream Events</h2>
          {streamEvents.map((event, index) => (
            <div key={index} className="stream-event">
              <span className="event-type">{event.type}</span>
              <pre>{JSON.stringify(event, null, 2)}</pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchForm;
