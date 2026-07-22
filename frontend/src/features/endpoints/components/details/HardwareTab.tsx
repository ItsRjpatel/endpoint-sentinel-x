import { Cpu, MemoryStick, CircuitBoard, Layers, MonitorCheck } from 'lucide-react';
import { EndpointDetails } from '../../types';

interface HardwareTabProps {
  endpoint: EndpointDetails;
}

export function HardwareTab({ endpoint }: HardwareTabProps) {
  const { hardware } = endpoint;

  const specs = [
    { label: 'Processor', value: hardware.cpu, icon: Cpu },
    { label: 'Logical cores', value: hardware.cpuCores, icon: Layers },
    { label: 'Installed memory (RAM)', value: `${hardware.ramTotalGB} GB`, icon: MemoryStick },
    { label: 'Motherboard', value: hardware.motherboard, icon: CircuitBoard },
    { label: 'BIOS version', value: hardware.biosVersion, icon: CircuitBoard },
    { label: 'Graphics adapter', value: hardware.graphics, icon: MonitorCheck },
  ];

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary">System components</h3>
        <span className="text-xs text-text-muted">Last inventoried a few minutes ago</span>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {specs.map(({ label, value, icon: Icon }) => (
          <div key={label} className="flex items-start gap-3 rounded-lg border border-border bg-surface-secondary/40 p-4">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-border bg-card text-text-muted">
              <Icon className="h-4 w-4" aria-hidden="true" />
            </span>
            <div className="min-w-0">
              <p className="text-xs text-text-muted">{label}</p>
              <p className="mt-0.5 truncate text-sm font-semibold text-text-primary">{value}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
