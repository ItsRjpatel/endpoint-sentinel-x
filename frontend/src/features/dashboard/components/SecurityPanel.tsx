
import { useSecurityOverview } from '../hooks/useDashboard';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/Card';
import { Skeleton } from '../../../components/ui/Skeleton';
import { ShieldCheck, ShieldAlert, ShieldX, HelpCircle } from 'lucide-react';

export function SecurityPanel() {
  const { data, isLoading } = useSecurityOverview();

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-4 shrink-0">
        <CardTitle>Security Overview</CardTitle>
      </CardHeader>
      <CardContent className="flex-1">
        {isLoading || !data ? (
          <div className="space-y-4" aria-busy="true">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <div className="grid grid-cols-2 gap-3 mt-4">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-5">
            {/* High-level scores */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1 p-3 rounded-lg border border-border bg-surface-secondary/30">
                <span className="text-xs font-medium text-text-muted">Security Score</span>
                <div className="flex items-baseline gap-1">
                  <span className="text-2xl font-bold text-success">{data.score}</span>
                  <span className="text-xs text-text-muted">/100</span>
                </div>
              </div>
              <div className="flex flex-col gap-1 p-3 rounded-lg border border-border bg-surface-secondary/30">
                <span className="text-xs font-medium text-text-muted">Compliance</span>
                <div className="flex items-baseline gap-1">
                  <span className="text-2xl font-bold text-primary">{data.complianceProgress}%</span>
                </div>
              </div>
            </div>

            {/* Status breakdown */}
            <div className="grid grid-cols-2 gap-3">
              <div className="flex items-center justify-between p-2.5 rounded-lg border border-border bg-surface-secondary/20">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-success" />
                  <span className="text-xs font-medium text-text-secondary">Protected</span>
                </div>
                <span className="text-sm font-semibold">{data.protected}</span>
              </div>
              
              <div className="flex items-center justify-between p-2.5 rounded-lg border border-border bg-surface-secondary/20">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="h-4 w-4 text-warning" />
                  <span className="text-xs font-medium text-text-secondary">At Risk</span>
                </div>
                <span className="text-sm font-semibold">{data.atRisk}</span>
              </div>

              <div className="flex items-center justify-between p-2.5 rounded-lg border border-border bg-surface-secondary/20">
                <div className="flex items-center gap-2">
                  <ShieldX className="h-4 w-4 text-danger" />
                  <span className="text-xs font-medium text-text-secondary">Critical</span>
                </div>
                <span className="text-sm font-semibold">{data.critical}</span>
              </div>

              <div className="flex items-center justify-between p-2.5 rounded-lg border border-border bg-surface-secondary/20">
                <div className="flex items-center gap-2">
                  <HelpCircle className="h-4 w-4 text-text-muted" />
                  <span className="text-xs font-medium text-text-secondary">Unknown</span>
                </div>
                <span className="text-sm font-semibold">{data.unknown}</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default SecurityPanel;
