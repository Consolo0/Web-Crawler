import React, { useState } from 'react';

const ProductGrid = ({ products, metadata, sourceName }) => {
  const PRODUCTS_PER_PAGE = 10;
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(products.length / PRODUCTS_PER_PAGE);
  const startIdx = (currentPage - 1) * PRODUCTS_PER_PAGE;
  const endIdx = startIdx + PRODUCTS_PER_PAGE;
  const currentProducts = products.slice(startIdx, endIdx);

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  return (
    <div className="product-grid-container">
      {/* Inject CSS */}
      <style>
        {`
          /* Import external stylesheets */
          ${metadata.stylesheets?.map(url => `@import url('${url}');`).join('\n')}
          
          /* Inline styles */
          ${metadata.inline_styles?.join('\n')}
          
          /* Grid layout styles */
          .product-grid-wrapper {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
          }
          
          .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 250px));
            gap: 16px;
            width: 100%;
            max-width: 1400px;
            margin: 0 auto;
            justify-content: start;
          }
          
          .product-grid > * {
            width: 242px !important;
            max-width: 242px !important;
            min-width: 242px !important;
            height: auto !important;
            max-height: none !important;
            overflow: visible !important;
          }
          
          @media (max-width: 1200px) {
            .product-grid {
              grid-template-columns: repeat(auto-fill, minmax(240px, 250px));
            }
          }
          
          @media (max-width: 768px) {
            .product-grid {
              grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            }
            
            .product-grid > * {
              width: 100% !important;
              max-width: 100% !important;
              min-width: 200px !important;
            }
          }
          
          .pagination {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            margin-top: 20px;
            padding: 15px;
            background: white;
            border-radius: 8px;
          }
          
          .pagination-button {
            padding: 8px 16px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
          }
          
          .pagination-button:hover:not(:disabled) {
            background: #f0f0f0;
            border-color: #999;
          }
          
          .pagination-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
          }
          
          .pagination-info {
            padding: 8px 16px;
            font-size: 14px;
            color: #666;
          }
          
          .page-number {
            padding: 8px 12px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            min-width: 36px;
            text-align: center;
            transition: all 0.2s;
          }
          
          .page-number.active {
            background: #007bff;
            color: white;
            border-color: #007bff;
          }
          
          .page-number:hover:not(.active) {
            background: #f0f0f0;
          }
        `}
      </style>

      <div className="product-grid-wrapper">
        <h4>Source: {sourceName} (Page {currentPage} of {totalPages})</h4>
        
        <div 
          className="product-grid"
          dangerouslySetInnerHTML={{
            __html: currentProducts.map(p => p.html).join('')
          }}
        />

        {totalPages > 1 && (
          <div className="pagination">
            <button
              className="pagination-button"
              onClick={() => handlePageChange(1)}
              disabled={currentPage === 1}
            >
              First
            </button>
            
            <button
              className="pagination-button"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </button>

            {/* Page numbers */}
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = currentPage - 2 + i;
              }

              return (
                <div
                  key={pageNum}
                  className={`page-number ${currentPage === pageNum ? 'active' : ''}`}
                  onClick={() => handlePageChange(pageNum)}
                >
                  {pageNum}
                </div>
              );
            })}

            <button
              className="pagination-button"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </button>

            <button
              className="pagination-button"
              onClick={() => handlePageChange(totalPages)}
              disabled={currentPage === totalPages}
            >
              Last
            </button>

            <span className="pagination-info">
              Showing {startIdx + 1}-{Math.min(endIdx, products.length)} of {products.length}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductGrid;
