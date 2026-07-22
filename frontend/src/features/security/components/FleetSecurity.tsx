import { Shield, ShieldCheck, Download, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { useFleetSecurity } from '../hooks/useSecurity';
import { Skeleton } from '@/components/ui/Skeleton';
import clsx from 'clsx';

export default function FleetSecurity() {
  const { data, isLoading, isError } = useFleetSecurity();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-32 w-full" />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <Card className="border-red-200 bg-red-50 dark:border-red-900/50 dark:bg-red-900/10">
        <CardContent className="p-6">
          <p className="text-sm text-red-600 dark:text-red-400">Failed to load security metrics.</p>
        </CardContent>
      </Card>
    );
  }

  const metrics = [
    {
      title: 'Average Security Score',
      value: `${Math.round(data.average_score)}/100`,
      icon: Shield,
      color: data.average_score >= 80 ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400',
      bg: data.average_score >= 80 ? 'bg-emerald-100 dark:bg-emerald-900/30' : 'bg-amber-100 dark:bg-amber-900/30',
    },
    {
      title: 'Protected Endpoints',
      value: data.protected_endpoints,
      icon: ShieldCheck,
      color: 'text-blue-600 dark:text-blue-400',
      bg: 'bg-blue-100 dark:bg-blue-900/30',
    },
    {
      title: 'High Risk Endpoints',
      value: data.high_risk_endpoints,
      icon: AlertTriangle,
      color: data.high_risk_endpoints > 0 ? 'text-red-600 dark:text-red-400' : 'text-slate-600 dark:text-slate-400',
      bg: data.high_risk_endpoints > 0 ? 'bg-red-100 dark:bg-red-900/30' : 'bg-slate-100 dark:bg-slate-800',
    },
    {
      title: 'Pending Updates',
      value: data.pending_updates_endpoints,
      icon: Download,
      color: data.pending_updates_endpoints > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-slate-600 dark:text-slate-400',
      bg: data.pending_updates_endpoints > 0 ? 'bg-amber-100 dark:bg-amber-900/30' : 'bg-slate-100 dark:bg-slate-800',
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((metric, i) => (
        <Card key={i}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-500 dark:text-slate-400">
              {metric.title}
            </CardTitle>
            <div className={clsx('p-2 rounded-md', metric.bg)}>
              <metric.icon className={clsx('h-4 w-4', metric.color)} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">
              {metric.value}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
