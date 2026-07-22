import { DashboardRepository } from './DashboardRepository';
import {
  FleetOverviewStats,
  HealthDataPoint,
  ActivityEvent,
  SecurityOverview,
  DashboardAlert,
  DashboardCommand
} from '../types';
import { apiClient } from '../../../api/client';

export class DashboardApiRepository implements DashboardRepository {
  async getFleetOverview(): Promise<FleetOverviewStats> {
    return apiClient.get<FleetOverviewStats>('/dashboard/fleet-overview');
  }

  async getFleetHealth(): Promise<HealthDataPoint[]> {
    return apiClient.get<HealthDataPoint[]>('/dashboard/fleet-health');
  }

  async getActivityFeed(): Promise<ActivityEvent[]> {
    return apiClient.get<ActivityEvent[]>('/dashboard/activity-feed');
  }

  async getSecurityOverview(): Promise<SecurityOverview> {
    return apiClient.get<SecurityOverview>('/dashboard/security-overview');
  }

  async getRecentAlerts(): Promise<DashboardAlert[]> {
    return apiClient.get<DashboardAlert[]>('/dashboard/recent-alerts');
  }

  async getRecentCommands(): Promise<DashboardCommand[]> {
    return apiClient.get<DashboardCommand[]>('/dashboard/recent-commands');
  }
}
