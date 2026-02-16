import React, { useState } from 'react';
import ProductGrid from './ProductGrid';

const SourceSection = ({ sourceName, sourceData }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Collect all products from all pages
  const allProducts = [];
  const metadata = {};

  Object.entries(sourceData).forEach(([pageNum, pageData]) => {
    if (pageData.metadata) {
      // Store metadata from first page (or merge if needed)
      if (!metadata.stylesheets) {
        metadata.stylesheets = pageData.metadata.stylesheets || [];
        metadata.inline_styles = pageData.metadata.inline_styles || [];
        metadata.base_url = pageData.metadata.base_url || '';
      }
    }
    
    if (pageData.products) {
      Object.entries(pageData.products).forEach(([productKey, productHtml]) => {
        allProducts.push({
          key: `${pageNum}_${productKey}`,
          html: productHtml,
          page: pageNum
        });
      });
    }
  });

  const totalProducts = allProducts.length;

  return (
    <div className="source-section">
      <div 
        className="source-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
        <h3 className="source-name">{sourceName}</h3>
        <span className="product-count">({totalProducts} products)</span>
      </div>
      
      {isExpanded && (
        <ProductGrid products={allProducts} metadata={metadata} sourceName={sourceName} />
      )}
    </div>
  );
};

export default SourceSection;
