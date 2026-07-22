import { useFleetOverview } from '../hooks/useDashboard';
import { Card, CardContent } from '../../../components/ui/Card';
import { Skeleton } from '../../../components/ui/Skeleton';
import { 
  Server, MonitorPlay, MonitorOff, BellRing, 
  AlertTriangle, Terminal, ShieldCheck, CheckCircle2 
} from 'lucide-react';
import React from 'react';

interface KpiCardProps {
  title: string;
  value?: number | string;
  icon: React.ElementType;
  loading: boolean;
}

const KpiCard = React.memo(({ title, value, icon: Icon, loading }: KpiCardProps) => {
  return (
    <Card>
      <CardContent className="p-4 flex items-center justify-between">
        <div className="space-y-0.5">
          <p className="text-xs font-medium text-text-muted">{title}</p>
          {loading ? (
            <Skeleton className="h-6 w-16" aria-busy="true" />
          ) : (
            <p className="text-xl font-bold text-text-primary leading-tight">{value ?? 'N/A'}</p>
          )}
        </div>
        <div className="p-2.5 bg-surface-secondary rounded-full">
          <Icon className="h-4 w-4 text-text-secondary" aria-hidden="true" />
          <span className="sr-only">{title} icon</span>
        </div>
      </CardContent>
    </Card>
  );
});

export function FleetOverview() {
  const { data, isLoading } = useFleetOverview();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <KpiCard title="Total Endpoints" value={data?.totalEndpoints} icon={Server} loading={isLoading} />
      <KpiCard title="Online" value={data?.online} icon={MonitorPlay} loading={isLoading} />
      <KpiCard title="Offline" value={data?.offline} icon={MonitorOff} loading={isLoading} />
      <KpiCard title="Active Alerts" value={data?.activeAlerts} icon={BellRing} loading={isLoading} />
      <KpiCard title="Critical Alerts" value={data?.criticalAlerts} icon={AlertTriangle} loading={isLoading} />
      <KpiCard title="Pending Commands" value={data?.pendingCommands} icon={Terminal} loading={isLoading} />
      <KpiCard title="Security Score" value={data?.securityScore ? `${data.securityScore}%` : undefined} icon={ShieldCheck} loading={isLoading} />
      <KpiCard title="Compliance Score" value={data?.complianceScore ? `${data.complianceScore}%` : undefined} icon={CheckCircle2} loading={isLoading} />
    </div>
  );
}
