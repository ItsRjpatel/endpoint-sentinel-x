import {
  FleetOverviewStats,
  HealthDataPoint,
  ActivityEvent,
  SecurityOverview,
  DashboardAlert,
  DashboardCommand
} from '../types';

export interface DashboardRepository {
  getFleetOverview(): Promise<FleetOverviewStats>;
  getFleetHealth(): Promise<HealthDataPoint[]>;
  getActivityFeed(): Promise<ActivityEvent[]>;
  getSecurityOverview(): Promise<SecurityOverview>;
  getRecentAlerts(): Promise<DashboardAlert[]>;
  getRecentCommands(): Promise<DashboardCommand[]>;
}
