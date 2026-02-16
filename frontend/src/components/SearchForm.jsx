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
  const [streamProgress, setStreamProgress] = useState(null);
  const [useStreaming, setUseStreaming] = useState(true);

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
    setStreamProgress(null);

    try {
      if (useStreaming) {
        await handleStreamingCrawl();
      } else {
        await handleRegularCrawl();
      }
    } catch (error) {
      // Errors are handled within each handler, this is just a safety net
      console.error('Unexpected crawl error:', error);
    } finally {
      setIsLoading(false);
      setStreamProgress(null);
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
      // Dismiss ALL toasts
      toast.dismiss();
      
      // Show error toast
      toast.error(`Crawl failed: ${error.message || 'Something went wrong'}`, {
        duration: 5000,
        position: 'top-center',
      });
      
      // Don't re-throw to avoid duplicate error handling
      console.error('Regular crawl error:', error);
    }
  };

  const handleStreamingCrawl = async () => {
    const toastId = toast.loading('Starting streaming crawl...', {
      position: 'top-center',
    });

    // Initialize results structure to match regular API format
    const streamingResults = {
      results: {
        results: {}
      }
    };

    let totalProductsReceived = 0;

    try {
      for await (const event of crawlStream(query, restrictions)) {
        
        if (event.type === 'status') {
          // Update progress toast
          setStreamProgress({
            message: event.message,
            submitted: event.submitted,
            completed: event.completed
          });
          toast.loading(`${event.message} (${event.completed}/${event.submitted})`, { id: toastId });
        } 
        
        else if (event.type === 'listing_result') {
          // Add listing results to the structure
          const { source_id, level, data } = event;
          
          // Initialize source if doesn't exist
          if (!streamingResults.results.results[source_id]) {
            streamingResults.results.results[source_id] = {};
          }
          
          // Add data at the appropriate level
          streamingResults.results.results[source_id][level] = data;
          
          // Count products
          const productsCount = Object.keys(data.products || {}).length;
          totalProductsReceived += productsCount;
          
          // Update results to trigger re-render
          setResults({ ...streamingResults });
          
          // Show toast for products received
          toast.success(`${source_id}: ${productsCount} products received`, {
            id: `${source_id}-${level}`,
            duration: 2000,
            position: 'top-center',
          });
        } 
        
        else if (event.type === 'error') {
          // Show error toast
          console.error('Stream error:', event);
          toast.error(`Error from ${event.data?.source_id || 'crawler'}: ${event.data?.error || event.message}`, {
            duration: 4000,
            position: 'top-center',
          });
        } 
        
        else if (event.type === 'done') {
          //Dismiss all toasts
          toast.dismiss()
          // Crawl complete
          toast.success(
            `Streaming completed! ${event.total_products || totalProductsReceived} products found`, 
            {
              id: toastId,
              duration: 3000,
              position: 'top-center',
            }
          );
        }
      }
      
      // Set final results
      setResults(streamingResults);
      
    } catch (error) {
      // Dismiss ALL toasts - this clears everything
      toast.dismiss();
      
      // Show the error toast
      toast.error(`Stream failed: ${error.message || 'Something went wrong'}`, {
        duration: 5000,
        position: 'top-center',
      });

    }
  };

  const handleReset = () => {
    setQuery('');
    setResults(null);
    setStreamProgress(null);
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

      {/* Stream Progress Display */}
      {streamProgress && isLoading && (
        <div className="stream-progress" style={{
          marginTop: '20px',
          padding: '15px',
          background: '#f0f9ff',
          border: '1px solid #0ea5e9',
          borderRadius: '8px',
        }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#0369a1' }}>Streaming Progress</h3>
          <p style={{ margin: '5px 0', color: '#075985' }}>{streamProgress.message}</p>
          <div style={{
            display: 'flex',
            gap: '20px',
            marginTop: '10px',
            fontSize: '14px',
            color: '#0c4a6e'
          }}>
            <span>Submitted: {streamProgress.submitted}</span>
            <span>Completed: {streamProgress.completed}</span>
          </div>
        </div>
      )}

      {/* Results Display - Works same as before! */}
      {results && <ResultsDisplay results={results} />}
    </div>
  );
};

export default SearchForm;