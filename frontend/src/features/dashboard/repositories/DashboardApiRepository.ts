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
    const response = await apiClient.get<{
      total_endpoints: number;
      online: number;
      offline: number;
      active_alerts: number;
      critical_alerts: number;
      pending_commands: number;
      security_score: number;
      compliance_score: number;
    }>('/dashboard/fleet-overview');

    return {
      totalEndpoints: response.total_endpoints,
      online: response.online,
      offline: response.offline,
      activeAlerts: response.active_alerts,
      criticalAlerts: response.critical_alerts,
      pendingCommands: response.pending_commands,
      securityScore: response.security_score,
      complianceScore: response.compliance_score,
    };
  }

  async getFleetHealth(): Promise<HealthDataPoint[]> {
    const response = await apiClient.get<Array<{
      time: string;
      cpu: number;
      memory: number;
      disk: number;
      network_in: number;
      network_out: number;
    }>>('/dashboard/fleet-health');

    return response.map((point) => ({
      time: point.time,
      cpu: point.cpu,
      memory: point.memory,
      disk: point.disk,
      networkIn: point.network_in,
      networkOut: point.network_out,
    }));
  }

  async getActivityFeed(): Promise<ActivityEvent[]> {
    return apiClient.get<ActivityEvent[]>('/dashboard/activity-feed');
  }

  async getSecurityOverview(): Promise<SecurityOverview> {
    const response = await apiClient.get<{
      protected: number;
      at_risk: number;
      critical: number;
      unknown: number;
      score: number;
      compliance_progress: number;
    }>('/dashboard/security-overview');

    return {
      protected: response.protected,
      atRisk: response.at_risk,
      critical: response.critical,
      unknown: response.unknown,
      score: response.score,
      complianceProgress: response.compliance_progress,
    };
  }

  async getRecentAlerts(): Promise<DashboardAlert[]> {
    return apiClient.get<DashboardAlert[]>('/dashboard/recent-alerts');
  }

  async getRecentCommands(): Promise<DashboardCommand[]> {
    const response = await apiClient.get<Array<{
      id: string;
      endpoint: string;
      command: string;
      status: DashboardCommand['status'];
      executed_at: string;
      duration_ms: number | null;
    }>>('/dashboard/recent-commands');

    return response.map((command) => ({
      id: command.id,
      endpoint: command.endpoint,
      command: command.command,
      status: command.status,
      executedAt: command.executed_at,
      durationMs: command.duration_ms,
    }));
  }
}
