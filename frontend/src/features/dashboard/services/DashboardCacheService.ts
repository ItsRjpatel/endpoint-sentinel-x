import { QueryClient } from '@tanstack/react-query';
import { DASHBOARD_QUERY_KEYS } from '../hooks/useDashboard';
import { FleetOverviewStats, HealthDataPoint, ActivityEvent, DashboardAlert, DashboardCommand } from '../types';

export interface IDashboardCache {
  updateFleetOverview(updater: (old: FleetOverviewStats | undefined) => FleetOverviewStats | undefined): void;
  invalidateFleetOverview(): void;
  addActivityEvent(event: ActivityEvent): void;
  addPerformancePoint(data: HealthDataPoint): void;
  invalidateSecurityOverview(): void;
  updateRecentAlerts(updater: (old: DashboardAlert[] | undefined) => DashboardAlert[] | undefined): void;
  updateRecentCommands(updater: (old: DashboardCommand[] | undefined) => DashboardCommand[] | undefined): void;
}

export class DashboardCacheService implements IDashboardCache {
  constructor(private queryClient: QueryClient) {}

  updateFleetOverview(updater: (old: FleetOverviewStats | undefined) => FleetOverviewStats | undefined) {
    this.queryClient.setQueryData<FleetOverviewStats>(DASHBOARD_QUERY_KEYS.fleetOverview, updater);
  }
  
  invalidateFleetOverview() {
    this.queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEYS.fleetOverview });
  }

  addActivityEvent(event: ActivityEvent) {
    this.queryClient.setQueryData<ActivityEvent[]>(DASHBOARD_QUERY_KEYS.activityFeed, (old) => {
      if (!old) return [event];
      return [event, ...old].slice(0, 100);
    });
  }

  addPerformancePoint(data: HealthDataPoint) {
    this.queryClient.setQueryData<HealthDataPoint[]>(DASHBOARD_QUERY_KEYS.fleetHealth, (old) => {
      if (!old) return [data];
      return [...old, data].slice(-25);
    });
  }

  invalidateSecurityOverview() {
    this.queryClient.invalidateQueries({ queryKey: DASHBOARD_QUERY_KEYS.securityOverview });
  }

  updateRecentAlerts(updater: (old: DashboardAlert[] | undefined) => DashboardAlert[] | undefined) {
    this.queryClient.setQueryData<DashboardAlert[]>(DASHBOARD_QUERY_KEYS.recentAlerts, updater);
  }

  updateRecentCommands(updater: (old: DashboardCommand[] | undefined) => DashboardCommand[] | undefined) {
    this.queryClient.setQueryData<DashboardCommand[]>(DASHBOARD_QUERY_KEYS.recentCommands, updater);
  }
}
