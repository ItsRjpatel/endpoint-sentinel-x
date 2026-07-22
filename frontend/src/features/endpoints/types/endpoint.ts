import { HardwareInfo } from './hardware';
import { PerformanceInfo } from './performance';
import { SecurityInfo } from './security';
import { NetworkAdapter } from './network';
import { InstalledSoftware } from './software';
import { WindowsUpdate } from './updates';
import { WindowsService } from './services';
import { LocalUser } from './users';
import { TimelineEvent } from './timeline';

export interface Endpoint {
  id: string;
  status: 'online' | 'offline' | 'inactive';
  hostname: string;
  deviceType: 'desktop' | 'laptop' | 'server';
  user: string | null;
  os: string;
  ipAddress: string;
  securityScore: number;
  compliance: 'compliant' | 'non-compliant' | 'unknown';
  lastSeen: string;
  alerts: number;
}

export interface EndpointFilters {
  search?: string;
  status?: string;
  deviceType?: string;
  os?: string;
  security?: string;
  compliance?: string;
  alerts?: 'hasAlerts' | 'criticalAlerts' | 'all';
}

export interface EndpointSort {
  field: keyof Endpoint;
  direction: 'asc' | 'desc';
}

export interface EndpointPagination {
  page: number;
  pageSize: number;
}

export interface EndpointListResponse {
  data: Endpoint[];
  total: number;
}

// Sprint 5.4 - Detailed Endpoint Types

export interface OperatingSystemInfo {
  name: string;
  version: string;
  build: string;
  architecture: string;
  installDate: string;
}

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface RiskFactor {
  label: string;
  weight: 'high' | 'medium' | 'low';
}

export interface EndpointDetails extends Endpoint {
  manufacturer: string;
  model: string;
  serialNumber: string;
  assetTag: string;
  domain: string;
  macAddress: string;
  operatingSystem: OperatingSystemInfo;
  isolated?: boolean;
  riskScore?: number;
  riskLevel?: 'low' | 'medium' | 'high' | 'critical';
  riskFactors?: { label: string; weight: 'high' | 'medium' | 'low'; }[];
  openAlertsCount?: number;
  
  hardware: HardwareInfo;
  performance: PerformanceInfo;
  security: SecurityInfo;
  networkAdapters: NetworkAdapter[];
  software: InstalledSoftware[];
  updates: WindowsUpdate[];
  services: WindowsService[];
  users: LocalUser[];
  timeline: TimelineEvent[];
}
