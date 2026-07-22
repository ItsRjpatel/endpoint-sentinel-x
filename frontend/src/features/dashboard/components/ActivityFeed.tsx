import { Link } from 'react-router-dom';
import { useActivityFeed } from '../hooks/useDashboard';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/Card';
import { Skeleton } from '../../../components/ui/Skeleton';
import { Info, CheckCircle2, AlertTriangle, XCircle, ArrowRight } from 'lucide-react';
import { ActivityEvent } from '../types';

const EventIcon = ({ type }: { type: ActivityEvent['type'] }) => {
  switch (type) {
    case 'info': return <Info className="h-4 w-4 text-primary" />;
    case 'success': return <CheckCircle2 className="h-4 w-4 text-success" />;
    case 'warning': return <AlertTriangle className="h-4 w-4 text-warning" />;
    case 'error': return <XCircle className="h-4 w-4 text-danger" />;
    default: return <Info className="h-4 w-4" />;
  }
};

export function ActivityFeed() {
  const { data, isLoading } = useActivityFeed();

  const displayData = data ? data.slice(0, 8) : [];

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3 shrink-0">
        <CardTitle>Live Activity Feed</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col overflow-hidden">
        {isLoading ? (
          <div className="space-y-3" aria-busy="true">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="flex gap-3 items-start">
                <Skeleton className="h-4 w-4 rounded-full mt-1 shrink-0" />
                <div className="space-y-1.5 flex-1">
                  <Skeleton className="h-3 w-3/4" />
                  <Skeleton className="h-2 w-1/4" />
                </div>
              </div>
            ))}
          </div>
        ) : displayData.length === 0 ? (
          <div className="text-center text-text-muted text-sm py-6">No recent activity.</div>
        ) : (
          <div className="space-y-3.5" aria-live="polite">
            {displayData.map((event) => (
              <div 
                key={event.id} 
                className="flex gap-2.5 items-start text-sm transition-all duration-300 ease-in-out animate-in fade-in slide-in-from-top-2"
              >
                <div className="mt-0.5 shrink-0" aria-hidden="true">
                  <EventIcon type={event.type} />
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="text-text-primary break-words text-[13px] leading-tight">
                    <span className="sr-only">{event.type} event: </span>
                    {event.message}
                  </span>
                  <span className="text-[11px] text-text-muted mt-0.5">
                    {new Intl.DateTimeFormat(undefined, {
                      hour: 'numeric',
                      minute: 'numeric',
                      second: 'numeric'
                    }).format(new Date(event.timestamp))}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
        
        <div className="pt-3 mt-auto border-t border-border flex justify-end shrink-0">
          <Link to="/activity" className="text-sm text-primary hover:text-primary-hover font-medium flex items-center gap-1 transition-colors">
            View All Activity <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
export default ActivityFeed;
