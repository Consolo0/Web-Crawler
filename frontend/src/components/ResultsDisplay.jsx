import React from 'react';
import SourceSection from './SourceSection';

const ResultsDisplay = ({ results }) => {
  if (!results || !results.results || !results.results.results) {
    return null;
  }

  const sources = results.results.results;

  return (
    <div className="results-display">
      <h2>Search Results</h2>
      {Object.entries(sources).map(([sourceName, sourceData]) => (
        <SourceSection key={sourceName} sourceName={sourceName} sourceData={sourceData} />
      ))}
    </div>
  );
};

export default ResultsDisplay;
