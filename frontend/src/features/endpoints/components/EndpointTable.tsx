
import { ArrowUp, ArrowDown, ArrowRight, Terminal, Shield, PowerOff } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Endpoint, EndpointSort } from '../types';
import { Badge } from '../../../components/ui/Badge';
import { Skeleton } from '../../../components/ui/Skeleton';

interface EndpointTableProps {
  endpoints: Endpoint[];
  isLoading: boolean;
  sort: EndpointSort;
  onSort: (field: keyof Endpoint) => void;
}

export function EndpointTable({ endpoints, isLoading, sort, onSort }: EndpointTableProps) {
  const navigate = useNavigate();
  const getSortIcon = (field: keyof Endpoint) => {
    if (sort.field !== field) return null;
    return sort.direction === 'asc' ? <ArrowUp className="h-3 w-3 ml-1 inline" aria-hidden="true" /> : <ArrowDown className="h-3 w-3 ml-1 inline" aria-hidden="true" />;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-success';
      case 'offline': return 'bg-danger';
      case 'inactive': return 'bg-warning';
      default: return 'bg-border';
    }
  };

  const getComplianceVariant = (comp: string) => {
    switch (comp) {
      case 'compliant': return 'success';
      case 'non-compliant': return 'danger';
      default: return 'default';
    }
  };

  const getSecurityVariant = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
  };

  const renderSortableHeader = (label: string, field: keyof Endpoint, screenReaderLabel?: string) => (
    <th
      scope="col"
      className="px-4 py-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider cursor-pointer hover:bg-surface-secondary/50 transition-colors group"
      onClick={() => onSort(field)}
      aria-label={screenReaderLabel || `Sort by ${label}`}
    >
      <div className="flex items-center">
        {label}
        <span className="text-text-muted group-hover:text-text-primary transition-colors">
          {getSortIcon(field)}
        </span>
      </div>
    </th>
  );

  return (
    <div className="overflow-x-auto rounded-lg border border-border bg-surface-primary shadow-sm" aria-live="polite">
      <table className="min-w-full divide-y divide-border">
        <thead className="bg-surface-secondary/30">
          <tr>
            {renderSortableHeader('Status', 'status')}
            {renderSortableHeader('Hostname', 'hostname')}
            {renderSortableHeader('Device Type', 'deviceType')}
            {renderSortableHeader('User', 'user')}
            {renderSortableHeader('OS', 'os')}
            {renderSortableHeader('IP Address', 'ipAddress')}
            {renderSortableHeader('Score', 'securityScore', 'Sort by Security Score')}
            {renderSortableHeader('Compliance', 'compliance')}
            {renderSortableHeader('Last Seen', 'lastSeen')}
            {renderSortableHeader('Alerts', 'alerts')}
            <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-text-muted uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-surface-primary divide-y divide-border">
          {isLoading ? (
            Array.from({ length: 10 }).map((_, i) => (
              <tr key={`skeleton-${i}`} aria-busy="true">
                <td className="px-4 py-3"><Skeleton className="h-4 w-4 rounded-full" /></td>
                <td className="px-4 py-3"><Skeleton className="h-4 w-24" /></td>
                <td className="px-4 py-3"><Skeleton className="h-4 w-16" /></td>
                <td className="px-4 py-3"><Skeleton className="h-4 w-24" /></td>
                <td className="px-4 py-3"><Skeleton className="h-4 w-32" /></td>
                <td className="px-4 py-3"><Skeleton className="h-4 w-24" /></td>
                <td className="px-4 py-3"><Skeleton className="h-6 w-12" /></td>
                <td className="px-4 py-3"><Skeleton className="h-6 w-20" /></td>
                <td className="px-4 py-3"><Skeleton className="h-4 w-16" /></td>
                <td className="px-4 py-3"><Skeleton className="h-4 w-6" /></td>
                <td className="px-4 py-3 text-right"><Skeleton className="h-4 w-16 ml-auto" /></td>
              </tr>
            ))
          ) : endpoints.length === 0 ? (
            <tr>
              <td colSpan={11} className="px-4 py-12 text-center text-sm text-text-muted">
                No endpoints found matching your criteria.
              </td>
            </tr>
          ) : (
            endpoints.map((ep) => (
              <tr 
                key={ep.id} 
                onClick={() => navigate(`/endpoints/${ep.id}`)}
                className="hover:bg-surface-secondary/50 transition-colors group cursor-pointer"
              >
                <td className="px-4 py-3 whitespace-nowrap">
                  <div className="flex items-center">
                    <span className={`h-2.5 w-2.5 rounded-full ${getStatusColor(ep.status)}`} aria-hidden="true" />
                    <span className="sr-only">Status: {ep.status}</span>
                    <span className="ml-2 text-sm text-text-primary capitalize hidden 2xl:inline-block">{ep.status}</span>
                  </div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm font-semibold text-text-primary">
                  {ep.hostname}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-text-secondary capitalize">
                  {ep.deviceType}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-text-secondary">
                  {ep.user || <span className="text-text-muted italic">System</span>}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-text-secondary">
                  {ep.os}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm font-mono text-text-secondary">
                  {ep.ipAddress}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <Badge variant={getSecurityVariant(ep.securityScore)}>
                    <Shield className="h-3 w-3 mr-1" aria-hidden="true" />
                    {ep.securityScore}
                    <span className="sr-only">Security Score: {ep.securityScore}</span>
                  </Badge>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <Badge variant={getComplianceVariant(ep.compliance)} className="capitalize">
                    {ep.compliance}
                  </Badge>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-text-muted">
                  {new Intl.DateTimeFormat(undefined, {
                    month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric'
                  }).format(new Date(ep.lastSeen))}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  {ep.alerts > 0 ? (
                    <Badge variant="danger" className="rounded-full px-2 py-0.5 text-xs">
                      {ep.alerts}
                      <span className="sr-only">{ep.alerts} Alerts</span>
                    </Badge>
                  ) : (
                    <span className="text-text-muted text-xs">-</span>
                  )}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button 
                      onClick={(e) => { e.stopPropagation(); /* TODO: Shell */ }}
                      className="p-1.5 text-text-muted hover:text-primary hover:bg-primary/10 rounded" 
                      title="Remote Shell"
                    >
                      <Terminal className="h-4 w-4" />
                    </button>
                    <button 
                      onClick={(e) => { e.stopPropagation(); /* TODO: Restart */ }}
                      className="p-1.5 text-text-muted hover:text-warning hover:bg-warning/10 rounded" 
                      title="Restart"
                    >
                      <PowerOff className="h-4 w-4" />
                    </button>
                    <button 
                      className="p-1.5 text-text-muted hover:text-primary hover:bg-primary/10 rounded" 
                      title="View Details"
                      aria-label="View Details"
                    >
                      <ArrowRight className="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
