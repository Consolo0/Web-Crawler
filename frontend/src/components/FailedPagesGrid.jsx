import React, { useState } from 'react';

const FailedPagesGrid = ({ failedPages, sourceName }) => {
  const PAGES_PER_PAGE = 5;
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(failedPages.length / PAGES_PER_PAGE);
  const startIdx = (currentPage - 1) * PAGES_PER_PAGE;
  const endIdx = startIdx + PAGES_PER_PAGE;
  const currentFailedPages = failedPages.slice(startIdx, endIdx);

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  return (
    <div className="failed-pages-container">
      <style>{`
        .failed-pages-wrapper {
          background: #fff5f5;
          padding: 20px;
          border-radius: 8px;
          border: 1px solid #fed7d7;
        }

        .failed-page-item {
          margin-bottom: 16px;
        }

        .failed-page-label {
          color: #c53030;
          font-size: 14px;
          margin: 0 0 6px 0;
          font-weight: 600;
        }

        .failed-page-iframe {
          width: 100%;
          height: 500px;
          border: 1px solid #fc8181;
          border-radius: 4px;
        }

        .failed-page-no-html {
          color: #666;
          font-size: 14px;
          font-style: italic;
        }

        .failed-pagination {
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 10px;
          margin-top: 20px;
          padding: 15px;
          background: white;
          border-radius: 8px;
        }

        .failed-pagination-button {
          padding: 8px 16px;
          border: 1px solid #ddd;
          background: white;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
        }

        .failed-pagination-button:hover:not(:disabled) {
          background: #f0f0f0;
          border-color: #999;
        }

        .failed-pagination-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .failed-page-number {
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

        .failed-page-number.active {
          background: #fc8181;
          color: white;
          border-color: #fc8181;
        }

        .failed-page-number:hover:not(.active) {
          background: #f0f0f0;
        }

        .failed-pagination-info {
          padding: 8px 16px;
          font-size: 14px;
          color: #666;
        }
      `}</style>

      <div className="failed-pages-wrapper">
        <h4 style={{ margin: '0 0 16px 0', color: '#c53030' }}>
          Source: {sourceName} — Failed Pages ({currentPage} of {totalPages})
        </h4>

        {currentFailedPages.map(({ pageNum, html }) => (
          <div key={pageNum} className="failed-page-item">
            <p className="failed-page-label">Page {pageNum}</p>
            {html
              ? <iframe
                  srcDoc={html}
                  title={`Failed page ${pageNum} preview`}
                  className="failed-page-iframe"
                  sandbox="allow-scripts"
                />
              : <p className="failed-page-no-html">No HTML available.</p>
            }
          </div>
        ))}

        {totalPages > 1 && (
          <div className="failed-pagination">
            <button
              className="failed-pagination-button"
              onClick={() => handlePageChange(1)}
              disabled={currentPage === 1}
            >
              First
            </button>

            <button
              className="failed-pagination-button"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </button>

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
                  className={`failed-page-number ${currentPage === pageNum ? 'active' : ''}`}
                  onClick={() => handlePageChange(pageNum)}
                >
                  {pageNum}
                </div>
              );
            })}

            <button
              className="failed-pagination-button"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </button>

            <button
              className="failed-pagination-button"
              onClick={() => handlePageChange(totalPages)}
              disabled={currentPage === totalPages}
            >
              Last
            </button>

            <span className="failed-pagination-info">
              Showing {startIdx + 1}-{Math.min(endIdx, failedPages.length)} of {failedPages.length}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default FailedPagesGrid;