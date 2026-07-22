import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { EndpointPagination as PaginationType } from '../types';

interface EndpointPaginationProps {
  pagination: PaginationType;
  total: number;
  onPaginationChange: (newPagination: PaginationType) => void;
}

export function EndpointPagination({ pagination, total, onPaginationChange }: EndpointPaginationProps) {
  const { page, pageSize } = pagination;
  
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  
  const startItem = (page - 1) * pageSize + 1;
  const endItem = Math.min(page * pageSize, total);

  const handlePageChange = (newPage: number) => {
    if (newPage < 1 || newPage > totalPages) return;
    onPaginationChange({ ...pagination, page: newPage });
  };

  const handlePageSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onPaginationChange({ page: 1, pageSize: Number(e.target.value) });
  };

  return (
    <div className="flex items-center justify-between px-4 py-3 bg-surface-primary border border-border rounded-lg mt-4">
      <div className="flex flex-1 justify-between sm:hidden">
        <button
          onClick={() => handlePageChange(page - 1)}
          disabled={page === 1}
          className="relative inline-flex items-center rounded-md border border-border bg-surface-secondary px-4 py-2 text-sm font-medium text-text-primary hover:bg-surface-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <button
          onClick={() => handlePageChange(page + 1)}
          disabled={page === totalPages}
          className="relative ml-3 inline-flex items-center rounded-md border border-border bg-surface-secondary px-4 py-2 text-sm font-medium text-text-primary hover:bg-surface-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
      
      <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
        <div className="flex items-center gap-4 text-sm text-text-secondary">
          <p>
            Showing <span className="font-medium text-text-primary">{total === 0 ? 0 : startItem}</span> to <span className="font-medium text-text-primary">{endItem}</span> of{' '}
            <span className="font-medium text-text-primary">{total}</span> results
          </p>
          
          <div className="flex items-center gap-2 border-l border-border pl-4">
            <span>Rows per page:</span>
            <select
              value={pageSize}
              onChange={handlePageSizeChange}
              className="bg-surface-secondary border border-border text-text-primary rounded text-sm focus:ring-primary focus:border-primary py-1 px-2"
              aria-label="Rows per page"
            >
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </div>
        
        <div>
          <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
              className="relative inline-flex items-center rounded-l-md px-2 py-2 text-text-muted hover:text-text-primary hover:bg-surface-secondary border border-border focus:z-20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <span className="sr-only">Previous</span>
              <ChevronLeft className="h-4 w-4" aria-hidden="true" />
            </button>
            <span className="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-text-primary border border-border bg-surface-secondary">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={page === totalPages}
              className="relative inline-flex items-center rounded-r-md px-2 py-2 text-text-muted hover:text-text-primary hover:bg-surface-secondary border border-border focus:z-20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <span className="sr-only">Next</span>
              <ChevronRight className="h-4 w-4" aria-hidden="true" />
            </button>
          </nav>
        </div>
      </div>
    </div>
  );
}
