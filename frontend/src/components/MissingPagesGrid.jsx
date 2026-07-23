import React, { useState } from 'react';

const MissingPagesGrid = ({ missingPages, sourceName }) => {
  const PAGES_PER_PAGE = 5;
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(missingPages.length / PAGES_PER_PAGE);
  const startIdx = (currentPage - 1) * PAGES_PER_PAGE;
  const endIdx = startIdx + PAGES_PER_PAGE;
  const currentMissingPages = missingPages.slice(startIdx, endIdx);

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  return (
    <div className="missing-pages-container">
      <style>{`
        .missing-pages-wrapper {
          background: #fffbf0;
          padding: 20px;
          border-radius: 8px;
          border: 1px solid #f6e05e;
        }

        .missing-page-item {
          margin-bottom: 16px;
        }

        .missing-page-label {
          color: #744210;
          font-size: 14px;
          margin: 0 0 6px 0;
          font-weight: 600;
        }

        .missing-page-reason {
          color: #666;
          font-size: 14px;
          font-style: italic;
        }

        .missing-pagination {
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 10px;
          margin-top: 20px;
          padding: 15px;
          background: white;
          border-radius: 8px;
        }

        .missing-pagination-button {
          padding: 8px 16px;
          border: 1px solid #ddd;
          background: white;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
        }

        .missing-pagination-button:hover:not(:disabled) {
          background: #f0f0f0;
          border-color: #999;
        }

        .missing-pagination-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .missing-page-number {
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

        .missing-page-number.active {
          background: #f6e05e;
          color: #744210;
          border-color: #f6e05e;
        }

        .missing-page-number:hover:not(.active) {
          background: #f0f0f0;
        }

        .missing-pagination-info {
          padding: 8px 16px;
          font-size: 14px;
          color: #666;
        }
      `}</style>

      <div className="missing-pages-wrapper">
        <h4 style={{ margin: '0 0 16px 0', color: '#744210' }}>
          Source: {sourceName} — Missing Pages ({currentPage} of {totalPages})
        </h4>

        {currentMissingPages.map(({ pageNum }) => (
          <div key={pageNum} className="missing-page-item">
            <p className="missing-page-label">Page {pageNum}</p>
            <p className="missing-page-reason">Reason: HTML not available</p>
          </div>
        ))}

        {totalPages > 1 && (
          <div className="missing-pagination">
            <button
              className="missing-pagination-button"
              onClick={() => handlePageChange(1)}
              disabled={currentPage === 1}
            >
              First
            </button>

            <button
              className="missing-pagination-button"
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
                  className={`missing-page-number ${currentPage === pageNum ? 'active' : ''}`}
                  onClick={() => handlePageChange(pageNum)}
                >
                  {pageNum}
                </div>
              );
            })}

            <button
              className="missing-pagination-button"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </button>

            <button
              className="missing-pagination-button"
              onClick={() => handlePageChange(totalPages)}
              disabled={currentPage === totalPages}
            >
              Last
            </button>

            <span className="missing-pagination-info">
              Showing {startIdx + 1}-{Math.min(endIdx, missingPages.length)} of {missingPages.length}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default MissingPagesGrid;