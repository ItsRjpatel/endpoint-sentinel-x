import React, { Suspense } from 'react';
import { useDashboardWebSocket } from './hooks/useDashboardWebSocket';
import { FleetOverview } from './components/FleetOverview';
import { WidgetErrorBoundary } from '../../components/layout/WidgetErrorBoundary';
import { Skeleton } from '../../components/ui/Skeleton';
import { Card, CardContent } from '../../components/ui/Card';

const FleetPulse = React.lazy(() => import('./components/FleetPulse'));
const ActivityFeed = React.lazy(() => import('./components/ActivityFeed'));
const SecurityPanel = React.lazy(() => import('./components/SecurityPanel'));
const RecentAlerts = React.lazy(() => import('./components/RecentAlerts'));

const WidgetFallback = () => (
  <Card className="h-full">
    <CardContent className="p-6 h-full flex items-center justify-center min-h-[300px]">
      <Skeleton className="h-full w-full" />
    </CardContent>
  </Card>
);

export function Dashboard() {
  // Initialize WebSocket subscriptions for dashboard events
  useDashboardWebSocket();

  return (
    <div className="flex flex-col gap-6">
      {/* Top Section - KPI Cards */}
      <section>
        <WidgetErrorBoundary title="Fleet Overview">
          <FleetOverview />
        </WidgetErrorBoundary>
      </section>

      {/* Main Grid Workspace */}
      <section className="grid grid-cols-1 lg:grid-cols-[5fr_5fr_3fr] gap-6">
        
        {/* Left Workspace (2 columns) */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <WidgetErrorBoundary title="Fleet Pulse">
            <Suspense fallback={<WidgetFallback />}>
              <FleetPulse />
            </Suspense>
          </WidgetErrorBoundary>

          <WidgetErrorBoundary title="Recent Alerts">
            <Suspense fallback={<WidgetFallback />}>
              <RecentAlerts />
            </Suspense>
          </WidgetErrorBoundary>
        </div>

        {/* Right Panel (1 column) */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          <WidgetErrorBoundary title="Security Overview">
            <Suspense fallback={<WidgetFallback />}>
              <SecurityPanel />
            </Suspense>
          </WidgetErrorBoundary>

          <WidgetErrorBoundary title="Activity Feed">
            <Suspense fallback={<WidgetFallback />}>
              <ActivityFeed />
            </Suspense>
          </WidgetErrorBoundary>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;
