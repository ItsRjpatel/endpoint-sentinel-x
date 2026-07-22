import React from 'react';
import { Search, Filter, RefreshCw, Download, Settings } from 'lucide-react';
import { EndpointFilters } from '../types';

interface EndpointToolbarProps {
  filters: EndpointFilters;
  onFilterChange: (newFilters: EndpointFilters) => void;
  onRefresh: () => void;
}

export function EndpointToolbar({ filters, onFilterChange, onRefresh }: EndpointToolbarProps) {
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({ ...filters, search: e.target.value });
  };

  const handleSelectChange = (field: keyof EndpointFilters) => (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFilterChange({ ...filters, [field]: e.target.value });
  };

  return (
    <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center bg-surface-primary p-4 rounded-lg border border-border">
      {/* Search */}
      <div className="relative w-full md:w-96">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-4 w-4 text-text-muted" aria-hidden="true" />
        </div>
        <input
          type="text"
          className="block w-full pl-10 pr-3 py-2 border border-border rounded-md leading-5 bg-surface-secondary text-text-primary placeholder-text-muted focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary sm:text-sm"
          placeholder="Search hostname, user, IP..."
          value={filters.search || ''}
          onChange={handleSearchChange}
        />
      </div>

      {/* Filters & Actions */}
      <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
        <select 
          className="bg-surface-secondary border border-border text-text-primary text-sm rounded-md focus:ring-primary focus:border-primary block p-2"
          value={filters.status || 'all'}
          onChange={handleSelectChange('status')}
          aria-label="Filter by Status"
        >
          <option value="all">All Statuses</option>
          <option value="online">Online</option>
          <option value="offline">Offline</option>
          <option value="inactive">Inactive</option>
        </select>

        <select 
          className="bg-surface-secondary border border-border text-text-primary text-sm rounded-md focus:ring-primary focus:border-primary block p-2"
          value={filters.deviceType || 'all'}
          onChange={handleSelectChange('deviceType')}
          aria-label="Filter by Device Type"
        >
          <option value="all">All Devices</option>
          <option value="desktop">Desktop</option>
          <option value="laptop">Laptop</option>
          <option value="server">Server</option>
        </select>

        <select 
          className="bg-surface-secondary border border-border text-text-primary text-sm rounded-md focus:ring-primary focus:border-primary block p-2"
          value={filters.compliance || 'all'}
          onChange={handleSelectChange('compliance')}
          aria-label="Filter by Compliance"
        >
          <option value="all">All Compliance</option>
          <option value="compliant">Compliant</option>
          <option value="non-compliant">Non-Compliant</option>
          <option value="unknown">Unknown</option>
        </select>
        
        <button className="flex items-center gap-2 px-3 py-2 border border-border bg-surface-secondary hover:bg-surface-secondary/80 rounded-md text-sm font-medium transition-colors">
          <Filter className="h-4 w-4" aria-hidden="true" />
          <span className="hidden sm:inline">More</span>
        </button>

        <div className="h-6 w-px bg-border mx-1 hidden sm:block" />

        <button 
          onClick={onRefresh}
          className="p-2 text-text-muted hover:text-text-primary border border-transparent hover:border-border hover:bg-surface-secondary rounded-md transition-all"
          aria-label="Refresh Data"
        >
          <RefreshCw className="h-4 w-4" />
        </button>

        <button 
          className="p-2 text-text-muted hover:text-text-primary border border-transparent hover:border-border hover:bg-surface-secondary rounded-md transition-all"
          aria-label="Export Data"
        >
          <Download className="h-4 w-4" />
        </button>
        
        <button 
          className="p-2 text-text-muted hover:text-text-primary border border-transparent hover:border-border hover:bg-surface-secondary rounded-md transition-all"
          aria-label="Bulk Actions"
        >
          <Settings className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
