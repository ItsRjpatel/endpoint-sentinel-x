import { Link } from 'react-router-dom';
import { useRecentAlerts } from '../hooks/useDashboard';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/Card';
import { Skeleton } from '../../../components/ui/Skeleton';
import { Badge } from '../../../components/ui/Badge';
import { ArrowRight } from 'lucide-react';

export function RecentAlerts() {
  const { data, isLoading } = useRecentAlerts();

  const getSeverityVariant = (sev: string) => {
    switch (sev) {
      case 'critical': return 'danger';
      case 'high': return 'warning';
      case 'medium': return 'info';
      default: return 'default';
    }
  };

  const displayData = data ? data.slice(0, 8) : [];

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3 shrink-0">
        <CardTitle>Recent Alerts</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col">
        {isLoading || !data ? (
          <div className="space-y-3 mt-1" aria-busy="true">
            {[1, 2, 3, 4, 5].map(i => <Skeleton key={i} className="h-8 w-full" />)}
          </div>
        ) : displayData.length === 0 ? (
          <div className="text-center text-text-muted text-sm py-6">No recent alerts.</div>
        ) : (
          <div className="min-w-full overflow-hidden" aria-live="polite">
            <table className="min-w-full divide-y divide-border">
              <thead>
                <tr>
                  <th scope="col" className="px-3 pb-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">Severity</th>
                  <th scope="col" className="px-3 pb-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">Endpoint</th>
                  <th scope="col" className="px-3 pb-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">Alert</th>
                  <th scope="col" className="px-3 pb-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">Time</th>
                  <th scope="col" className="px-3 pb-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {displayData.map((alert) => (
                  <tr key={alert.id} className="hover:bg-surface-secondary/50 cursor-pointer transition-colors group">
                    <td className="px-3 py-3 text-sm whitespace-nowrap">
                      <Badge variant={getSeverityVariant(alert.severity)} className="uppercase text-[10px] px-1.5 py-0 h-4 min-h-4 leading-none inline-flex items-center">
                        <span className="sr-only">Severity: </span>{alert.severity}
                      </Badge>
                    </td>
                    <td className="px-3 py-3 text-sm font-medium whitespace-nowrap">{alert.endpoint}</td>
                    <td className="px-3 py-3 text-sm text-text-secondary truncate max-w-[200px]" title={alert.message}>{alert.message}</td>
                    <td className="px-3 py-3 text-sm text-text-muted whitespace-nowrap">
                      <span className="sr-only">Time: </span>
                      {new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: 'numeric' }).format(new Date(alert.timestamp))}
                    </td>
                    <td className="px-3 py-3 text-sm whitespace-nowrap">
                      <Badge variant={alert.status === 'active' ? 'danger' : 'success'} className="px-1.5 py-0 h-4 min-h-4 leading-none inline-flex items-center text-[10px]">
                        <span className="sr-only">Status: </span>{alert.status}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="pt-3 mt-auto border-t border-border flex justify-end shrink-0">
          <Link to="/alerts" className="text-sm text-primary hover:text-primary-hover font-medium flex items-center gap-1 transition-colors">
            View All Alerts <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
export default RecentAlerts;
