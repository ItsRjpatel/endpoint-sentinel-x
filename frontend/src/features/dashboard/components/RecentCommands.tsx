
import { useRecentCommands } from '../hooks/useDashboard';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/Card';
import { Skeleton } from '../../../components/ui/Skeleton';
import { Badge } from '../../../components/ui/Badge';

export function RecentCommands() {
  const { data, isLoading } = useRecentCommands();

  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'failed': return 'danger';
      case 'running': return 'info';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle>Recent Commands</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-auto">
        {isLoading || !data ? (
          <div className="space-y-4 mt-2" aria-busy="true" aria-live="polite">
            {[1, 2, 3].map(i => <Skeleton key={i} className="h-10 w-full" />)}
          </div>
        ) : data.length === 0 ? (
          <div className="text-center text-text-muted text-sm py-8">No recent commands.</div>
        ) : (
          <div className="min-w-full inline-block align-middle" aria-live="polite">
            <table className="min-w-full divide-y divide-border">
              <thead>
                <tr>
                  <th scope="col" className="px-3 py-3 text-left text-xs font-medium text-text-muted uppercase">Endpoint</th>
                  <th scope="col" className="px-3 py-3 text-left text-xs font-medium text-text-muted uppercase">Command</th>
                  <th scope="col" className="px-3 py-3 text-left text-xs font-medium text-text-muted uppercase">Status</th>
                  <th scope="col" className="px-3 py-3 text-left text-xs font-medium text-text-muted uppercase">Executed</th>
                  <th scope="col" className="px-3 py-3 text-left text-xs font-medium text-text-muted uppercase">Duration</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {data.map((cmd) => (
                  <tr key={cmd.id} className="hover:bg-surface-secondary/50 transition-colors">
                    <td className="px-3 py-3 text-sm font-medium whitespace-nowrap">{cmd.endpoint}</td>
                    <td className="px-3 py-3 text-sm text-text-secondary whitespace-nowrap">{cmd.command}</td>
                    <td className="px-3 py-3 text-sm whitespace-nowrap">
                      <Badge variant={getStatusVariant(cmd.status)} className="capitalize">
                        <span className="sr-only">Status: </span>{cmd.status}
                      </Badge>
                    </td>
                    <td className="px-3 py-3 text-sm text-text-muted whitespace-nowrap">
                      <span className="sr-only">Executed At: </span>
                      {new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: 'numeric', second: 'numeric' }).format(new Date(cmd.executedAt))}
                    </td>
                    <td className="px-3 py-3 text-sm text-text-muted whitespace-nowrap">
                      <span className="sr-only">Duration: </span>
                      {cmd.durationMs ? `${(cmd.durationMs / 1000).toFixed(1)}s` : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
export default RecentCommands;
