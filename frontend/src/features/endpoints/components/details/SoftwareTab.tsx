import { useState } from 'react';
import { Search, Package } from 'lucide-react';
import { EndpointDetails } from '../../types';

interface SoftwareTabProps {
  endpoint: EndpointDetails;
}

export function SoftwareTab({ endpoint }: SoftwareTabProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const filtered = endpoint.software.filter(
    (s) =>
      s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.publisher.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h3 className="text-sm font-semibold text-text-primary">
          Installed applications <span className="font-normal text-text-muted">({endpoint.software.length})</span>
        </h3>
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" aria-hidden="true" />
          <input
            type="text"
            placeholder="Search by name or publisher"
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
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">Name</th>
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">Version</th>
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">Publisher</th>
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">Installed</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border bg-card">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-10 text-center text-sm text-text-muted">
                  No software matches “{searchTerm}”.
                </td>
              </tr>
            ) : (
              filtered.map((sw) => (
                <tr key={sw.id} className="hover:bg-surface-secondary/50 transition-colors">
                  <td className="px-4 py-2.5 text-sm font-medium text-text-primary">
                    <span className="flex items-center gap-2">
                      <Package className="h-3.5 w-3.5 shrink-0 text-text-muted" aria-hidden="true" />
                      {sw.name}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-sm tabular-nums text-text-secondary">{sw.version}</td>
                  <td className="px-4 py-2.5 text-sm text-text-secondary">{sw.publisher}</td>
                  <td className="px-4 py-2.5 text-sm text-text-muted">
                    {new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(sw.installDate))}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
