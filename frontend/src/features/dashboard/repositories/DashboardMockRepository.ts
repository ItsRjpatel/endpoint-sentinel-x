import { DashboardRepository } from './DashboardRepository';
import {
  FleetOverviewStats,
  HealthDataPoint,
  ActivityEvent,
  SecurityOverview,
  DashboardAlert,
  DashboardCommand
} from '../types';

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export class DashboardMockRepository implements DashboardRepository {
  async getFleetOverview(): Promise<FleetOverviewStats> {
    await delay(500);
    return {
      totalEndpoints: 1542,
      online: 1489,
      offline: 53,
      activeAlerts: 12,
      criticalAlerts: 3,
      pendingCommands: 45,
      securityScore: 87,
      complianceScore: 92,
    };
  }

  async getFleetHealth(): Promise<HealthDataPoint[]> {
    await delay(600);
    const data: HealthDataPoint[] = [];
    const now = new Date();
    for (let i = 24; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000);
      data.push({
        time: time.toISOString(),
        cpu: Math.floor(Math.random() * 40) + 20,
        memory: Math.floor(Math.random() * 30) + 40,
        disk: Math.floor(Math.random() * 10) + 60,
        networkIn: Math.floor(Math.random() * 1000),
        networkOut: Math.floor(Math.random() * 1000),
      });
    }
    return data;
  }

  async getActivityFeed(): Promise<ActivityEvent[]> {
    await delay(400);
    return [
      { id: '1', type: 'info', message: 'DESKTOP-001 came online', timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString() },
      { id: '2', type: 'success', message: 'Windows Defender updated on SRV-01', timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString() },
      { id: '3', type: 'warning', message: 'High CPU detected on DB-MASTER', timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString() },
      { id: '4', type: 'error', message: 'Agent disconnected: LPT-404', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString() },
    ];
  }

  async getSecurityOverview(): Promise<SecurityOverview> {
    await delay(500);
    return {
      protected: 1400,
      atRisk: 100,
      critical: 30,
      unknown: 12,
      score: 87,
      complianceProgress: 92,
    };
  }

  async getRecentAlerts(): Promise<DashboardAlert[]> {
    await delay(700);
    return [
      { id: '1', severity: 'critical', endpoint: 'DB-MASTER', message: 'Unauthorized access attempt', timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(), status: 'active' },
      { id: '2', severity: 'high', endpoint: 'LPT-404', message: 'Malware signature detected', timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(), status: 'active' },
      { id: '3', severity: 'medium', endpoint: 'SRV-01', message: 'Failed login attempts', timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(), status: 'resolved' },
    ];
  }

  async getRecentCommands(): Promise<DashboardCommand[]> {
    await delay(450);
    return [
      { id: '1', endpoint: 'DESKTOP-001', command: 'Force Defender Scan', status: 'pending', executedAt: new Date(Date.now() - 1000 * 30).toISOString(), durationMs: null },
      { id: '2', endpoint: 'SRV-01', command: 'Restart Service (IIS)', status: 'completed', executedAt: new Date(Date.now() - 1000 * 60 * 10).toISOString(), durationMs: 4500 },
      { id: '3', endpoint: 'DB-MASTER', command: 'Collect Memory Dump', status: 'failed', executedAt: new Date(Date.now() - 1000 * 60 * 60).toISOString(), durationMs: 12000 },
    ];
  }
}
