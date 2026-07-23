import React, { useState } from 'react';
import ProductGrid from './ProductGrid';
import FailedPagesGrid from './FailedPagesGrid';

const SourceSection = ({ sourceName, sourceData }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showFailed, setShowFailed] = useState(false);

  const allProducts = [];
  const metadata = {};
  const failedPages = [];

  Object.entries(sourceData).forEach(([pageNum, pageData]) => {
    if (pageData.status === 'failed') {
      failedPages.push({ pageNum, html: pageData.raw_html, metadata: pageData.metadata });
      return;
    }

    if (pageData.metadata && !metadata.stylesheets) {
      metadata.stylesheets = pageData.metadata.stylesheets || [];
      metadata.inline_styles = pageData.metadata.inline_styles || [];
      metadata.base_url = pageData.metadata.base_url || '';
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

  return (
    <div className="source-section">
      <div className="source-header" onClick={() => setIsExpanded(!isExpanded)}>
        <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
        <h3 className="source-name">{sourceName}</h3>
        <span className="product-count">({allProducts.length} products)</span>
        {failedPages.length > 0 && (
          <span style={{ color: 'red', marginLeft: '8px' }}>
            ⚠ {failedPages.length} page(s) failed
          </span>
        )}
      </div>

      {isExpanded && (
        <>
          {/* Successful products section */}
          <div style={{ marginTop: '12px' }}>
            <h4 style={{ color: 'green', margin: '0 0 8px 0' }}>
              ✓ Successfully retrieved ({allProducts.length} products)
            </h4>
            {allProducts.length > 0
              ? <ProductGrid products={allProducts} metadata={metadata} sourceName={sourceName} />
              : <p style={{ color: '#666', fontSize: '14px' }}>No products retrieved.</p>
            }
          </div>

          {/* Failed pages section */}
          {failedPages.length > 0 && (
            <div style={{ marginTop: '16px' }}>
              <div
                style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}
                onClick={() => setShowFailed(!showFailed)}
              >
                <span>{showFailed ? '▼' : '▶'}</span>
                <h4 style={{ color: 'red', margin: 0 }}>
                  ✗ Failed pages ({failedPages.length})
                </h4>
              </div>

              {showFailed && (
                <FailedPagesGrid failedPages={failedPages} sourceName={sourceName} />
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default SourceSection;