import { useState } from 'react';
import { Search } from 'lucide-react';
import { Badge } from '../../../../components/ui/Badge';
import { EndpointDetails } from '../../types';

interface ServicesTabProps {
  endpoint: EndpointDetails;
}

const statusVariant = { Running: 'success', Stopped: 'default', Paused: 'warning', Unknown: 'default' } as const;

export function ServicesTab({ endpoint }: ServicesTabProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const filtered = endpoint.services.filter(
    (s) =>
      s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.displayName.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h3 className="text-sm font-semibold text-text-primary">
          Windows services <span className="font-normal text-text-muted">({endpoint.services.length})</span>
        </h3>
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" aria-hidden="true" />
          <input
            type="text"
            placeholder="Search services"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-md border border-border bg-surface-secondary py-2 pl-9 pr-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
      </div>

      <div className="max-h-[440px] overflow-y-auto rounded-lg border border-border">
        <table className="min-w-full divide-y divide-border">
          <thead className="sticky top-0 z-10 bg-surface-secondary/95 backdrop-blur">
            <tr>
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">Service name</th>
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">Display name</th>
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">Status</th>
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">Startup</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border bg-card">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-10 text-center text-sm text-text-muted">No services match your search.</td>
              </tr>
            ) : (
              filtered.map((service) => (
                <tr key={service.name} className="hover:bg-surface-secondary/50 transition-colors">
                  <td className="px-4 py-2.5 text-sm font-medium text-text-primary">{service.name}</td>
                  <td className="px-4 py-2.5 text-sm text-text-secondary max-w-md">{service.displayName}</td>
                  <td className="px-4 py-2.5">
                    <Badge variant={statusVariant[service.status]}>{service.status}</Badge>
                  </td>
                  <td className="px-4 py-2.5 text-sm text-text-muted">{service.startupType}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
