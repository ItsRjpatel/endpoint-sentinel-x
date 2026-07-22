import { Activity, ShieldAlert, CheckCircle2, Info } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { useSecurityTimeline } from '../hooks/useSecurity';
import { Skeleton } from '@/components/ui/Skeleton';
import { formatDistanceToNow } from 'date-fns';

export default function SecurityTimeline() {
  const { data, isLoading, isError } = useSecurityTimeline(10);

  if (isLoading) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle>Recent Security Events</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  if (isError || !data) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle>Recent Security Events</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">Failed to load timeline.</p>
        </CardContent>
      </Card>
    );
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'high':
        return <ShieldAlert className="h-4 w-4 text-red-500" />;
      case 'medium':
        return <Activity className="h-4 w-4 text-amber-500" />;
      case 'low':
        return <CheckCircle2 className="h-4 w-4 text-emerald-500" />;
      default:
        return <Info className="h-4 w-4 text-blue-500" />;
    }
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Recent Security Events</CardTitle>
      </CardHeader>
      <CardContent>
        {data.events.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <CheckCircle2 className="h-8 w-8 text-slate-300 dark:text-slate-600 mb-3" />
            <p className="text-sm text-slate-500">No recent security events.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {data.events.map((event, i) => (
              <div key={event.id} className="relative pl-6">
                {/* Timeline line */}
                {i !== data.events.length - 1 && (
                  <div className="absolute left-2 top-6 bottom-[-24px] w-px bg-slate-200 dark:bg-slate-700" />
                )}
                
                {/* Timeline dot */}
                <div className="absolute left-0 top-1 h-4 w-4 rounded-full bg-white dark:bg-slate-900 ring-2 ring-slate-200 dark:ring-slate-700 flex items-center justify-center">
                  {getSeverityIcon(event.severity)}
                </div>

                <div className="flex flex-col space-y-1">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-slate-900 dark:text-white">
                      {event.event_type}
                    </p>
                    <span className="text-xs text-slate-500 whitespace-nowrap">
                      {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                    </span>
                  </div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {event.description}
                  </p>
                  <p className="text-xs text-slate-400">
                    Endpoint ID: {event.endpoint_id}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
