import { Network, Wifi, Cable, ShieldQuestion } from 'lucide-react';
import { Badge } from '../../../../components/ui/Badge';
import { EndpointDetails } from '../../types';

interface NetworkTabProps {
  endpoint: EndpointDetails;
}

const typeIcon = { Ethernet: Cable, 'Wi-Fi': Wifi, VPN: ShieldQuestion } as const;

export function NetworkTab({ endpoint }: NetworkTabProps) {
  const adapters = endpoint.networkAdapters;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary">Network adapters</h3>
        <span className="text-xs text-text-muted">{adapters.length} adapters</span>
      </div>

      {adapters.length === 0 ? (
        <div className="rounded-lg border border-border bg-surface-secondary/40 py-10 text-center text-sm text-text-muted">
          No network adapters found.
        </div>
      ) : (
        <div className="space-y-3">
          {adapters.map((adapter) => {
            const Icon = typeIcon[adapter.connectionType ?? 'Ethernet'] ?? Network;
            return (
              <div key={adapter.id} className="rounded-lg border border-border bg-surface-secondary/40 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="flex items-center gap-2 text-sm font-semibold text-text-primary">
                    <Icon className="h-4 w-4 text-text-muted" aria-hidden="true" />
                    {adapter.name}
                  </span>
                  <Badge variant={adapter.dhcpEnabled ? 'success' : 'default'}>
                    {adapter.dhcpEnabled ? 'DHCP enabled' : 'Static IP'}
                  </Badge>
                </div>

                <dl className="mt-3 grid grid-cols-2 gap-x-6 gap-y-2 sm:grid-cols-4">
                  <div>
                    <dt className="text-[11px] uppercase tracking-wide text-text-muted">IPv4</dt>
                    <dd className="font-mono text-sm text-text-secondary">{adapter.ipv4}</dd>
                  </div>
                  <div>
                    <dt className="text-[11px] uppercase tracking-wide text-text-muted">MAC address</dt>
                    <dd className="font-mono text-sm text-text-secondary">{adapter.mac}</dd>
                  </div>
                  <div>
                    <dt className="text-[11px] uppercase tracking-wide text-text-muted">Gateway</dt>
                    <dd className="font-mono text-sm text-text-secondary">{adapter.gateway}</dd>
                  </div>
                  <div>
                    <dt className="text-[11px] uppercase tracking-wide text-text-muted">DNS</dt>
                    <dd className="font-mono text-sm text-text-secondary">{adapter.dns.join(', ')}</dd>
                  </div>
                </dl>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
