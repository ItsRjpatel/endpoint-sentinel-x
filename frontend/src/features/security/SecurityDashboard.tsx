import React, { Suspense } from 'react';
import { WidgetErrorBoundary } from '@/components/layout/WidgetErrorBoundary';
import { Skeleton } from '@/components/ui/Skeleton';
import { Card, CardContent } from '@/components/ui/Card';

const FleetSecurity = React.lazy(() => import('./components/FleetSecurity'));
const SecurityTimeline = React.lazy(() => import('./components/SecurityTimeline'));

const WidgetFallback = () => (
  <Card className="h-full">
    <CardContent className="p-6 h-full flex items-center justify-center min-h-[300px]">
      <Skeleton className="h-full w-full" />
    </CardContent>
  </Card>
);

export function SecurityDashboard() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900 dark:text-white">
            Security Center
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Enterprise Fleet Security Overview
          </p>
        </div>
      </div>

      <section>
        <WidgetErrorBoundary title="Fleet Security Overview">
          <Suspense fallback={<WidgetFallback />}>
            <FleetSecurity />
          </Suspense>
        </WidgetErrorBoundary>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="lg:col-span-2 flex flex-col gap-6">
          <WidgetErrorBoundary title="Security Timeline">
            <Suspense fallback={<WidgetFallback />}>
              <SecurityTimeline />
            </Suspense>
          </WidgetErrorBoundary>
        </div>
      </section>
    </div>
  );
}

export default SecurityDashboard;
