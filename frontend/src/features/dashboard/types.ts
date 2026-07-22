export interface FleetOverviewStats {
  totalEndpoints: number;
  online: number;
  offline: number;
  activeAlerts: number;
  criticalAlerts: number;
  pendingCommands: number;
  securityScore: number;
  complianceScore: number;
}

export interface HealthDataPoint {
  time: string;
  cpu: number;
  memory: number;
  disk: number;
  networkIn: number;
  networkOut: number;
}

export interface ActivityEvent {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  message: string;
  timestamp: string;
}

export interface SecurityOverview {
  protected: number;
  atRisk: number;
  critical: number;
  unknown: number;
  score: number;
  complianceProgress: number;
}

export interface DashboardAlert {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  endpoint: string;
  message: string;
  timestamp: string;
  status: 'active' | 'resolved';
}

export interface DashboardCommand {
  id: string;
  endpoint: string;
  command: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  executedAt: string;
  durationMs: number | null;
}
