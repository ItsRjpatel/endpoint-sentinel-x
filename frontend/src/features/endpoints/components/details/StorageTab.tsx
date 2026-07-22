import { HardDrive } from 'lucide-react';
import { Badge } from '../../../../components/ui/Badge';
import { EndpointDetails } from '../../types';

interface StorageTabProps {
  endpoint: EndpointDetails;
}

const healthVariant = { Healthy: 'success', Warning: 'warning', Critical: 'danger' } as const;

export function StorageTab({ endpoint }: StorageTabProps) {
  const { storageDevices } = endpoint.hardware;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary">Storage devices</h3>
        <span className="text-xs text-text-muted">{storageDevices.length} volumes</span>
      </div>

      {storageDevices.length === 0 ? (
        <div className="rounded-lg border border-border bg-surface-secondary/40 py-10 text-center text-sm text-text-muted">
          No storage devices found.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
          {storageDevices.map((disk) => {
            const usedPct = Math.round((disk.usedSpaceGB / disk.totalSpaceGB) * 100);
            return (
              <div key={disk.driveLetter} className="rounded-lg border border-border bg-surface-secondary/40 p-4">
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-2 text-sm font-semibold text-text-primary">
                    <HardDrive className="h-4 w-4 text-text-muted" aria-hidden="true" />
                    {disk.driveLetter}
                    <span className="font-normal text-text-muted">{disk.fileSystem}</span>
                  </span>
                  <Badge variant={healthVariant[disk.healthStatus]}>{disk.healthStatus}</Badge>
                </div>

                <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-border">
                  <div
                    className={`h-full rounded-full ${usedPct > 90 ? 'bg-danger' : usedPct > 75 ? 'bg-warning' : 'bg-primary'}`}
                    style={{ width: `${usedPct}%` }}
                  />
                </div>

                <div className="mt-2 flex justify-between text-xs text-text-muted tabular-nums">
                  <span>{disk.usedSpaceGB} GB used ({usedPct}%)</span>
                  <span>{disk.freeSpaceGB} GB free</span>
                  <span>{disk.totalSpaceGB} GB total</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
