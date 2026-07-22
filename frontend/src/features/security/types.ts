export interface SecurityRecommendation {
  id: string;
  title: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
  category: 'defender' | 'firewall' | 'bitlocker' | 'os';
}

export interface SecurityScore {
  total_score: number;
  max_score: number;
  defender_score: number;
  firewall_score: number;
  bitlocker_score: number;
  tpm_score: number;
  secure_boot_score: number;
  updates_score: number;
}

export interface FleetSecuritySummary {
  average_score: number;
  total_endpoints: number;
  protected_endpoints: number;
  unprotected_endpoints: number;
  high_risk_endpoints: number;
  pending_updates_endpoints: number;
  recent_security_events: number;
}

export interface EndpointSecuritySummary {
  endpoint_id: number;
  score: SecurityScore;
  recommendations: SecurityRecommendation[];
  last_scan: string | null;
}

export interface SecurityEvent {
  id: number;
  endpoint_id: number;
  event_type: string;
  severity: string;
  description: string;
  timestamp: string;
}

export interface SecurityTimelineResponse {
  events: SecurityEvent[];
  total: number;
}
