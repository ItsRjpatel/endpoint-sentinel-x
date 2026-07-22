import { useState } from 'react';
import { useEndpoints } from '../hooks/useEndpoints';
import { useEndpointWebSocket } from '../hooks/useEndpointWebSocket';
import { EndpointToolbar } from './EndpointToolbar';
import { EndpointTable } from './EndpointTable';
import { EndpointPagination as PaginationControls } from './EndpointPagination';
import { WidgetErrorBoundary } from '../../../components/layout/WidgetErrorBoundary';
import { EndpointFilters, EndpointSort, EndpointPagination, Endpoint } from '../types';

export function EndpointInventory() {
  // Initialize WebSocket connection for live row updates
  useEndpointWebSocket();

  // State Management
  const [filters, setFilters] = useState<EndpointFilters>({});
  const [sort, setSort] = useState<EndpointSort>({ field: 'status', direction: 'asc' });
  const [pagination, setPagination] = useState<EndpointPagination>({ page: 1, pageSize: 25 });

  // Data Fetching
  const { data, isLoading, refetch } = useEndpoints(filters, sort, pagination);

  const handleSort = (field: keyof Endpoint) => {
    setSort(prev => {
      if (prev.field === field) {
        return { field, direction: prev.direction === 'asc' ? 'desc' : 'asc' };
      }
      return { field, direction: 'asc' };
    });
    // Reset to page 1 on sort change
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleFilterChange = (newFilters: EndpointFilters) => {
    setFilters(newFilters);
    // Reset to page 1 on filter change
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  return (
    <div className="flex flex-col gap-6 p-6 min-h-screen bg-surface-primary">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-text-primary">Endpoint Inventory</h1>
        <p className="text-text-muted mt-1 text-sm">View, monitor and manage all enrolled endpoints.</p>
      </div>

      <WidgetErrorBoundary title="Endpoint Inventory Table">
        <div className="flex flex-col gap-4">
          <EndpointToolbar 
            filters={filters} 
            onFilterChange={handleFilterChange} 
            onRefresh={() => refetch()}
          />
          
          <EndpointTable 
            endpoints={data?.data || []} 
            isLoading={isLoading} 
            sort={sort} 
            onSort={handleSort}
          />
          
          <PaginationControls 
            pagination={pagination}
            total={data?.total || 0}
            onPaginationChange={setPagination}
          />
        </div>
      </WidgetErrorBoundary>
    </div>
  );
}

export default EndpointInventory;
