import { apiClient } from '@/api/client';
import {
  EndpointSecuritySummary,
  FleetSecuritySummary,
  SecurityTimelineResponse,
} from '../types';

export class SecurityApiRepository {
  async getFleetSummary(): Promise<FleetSecuritySummary> {
    return apiClient.get<FleetSecuritySummary>('/security/fleet-summary');
  }

  async getEndpointSummary(endpointId: number): Promise<EndpointSecuritySummary> {
    return apiClient.get<EndpointSecuritySummary>(`/security/endpoints/${endpointId}/summary`);
  }

  async getTimeline(limit: number = 50): Promise<SecurityTimelineResponse> {
    return apiClient.get<SecurityTimelineResponse>(`/security/timeline?limit=${limit}`);
  }
}

export const securityRepository = new SecurityApiRepository();
