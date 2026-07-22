import { IEndpointCache } from '../services/EndpointCacheService';

export class EndpointEventAdapter {
  constructor(private cache: IEndpointCache) {}

  handleEndpointOnline(data: { endpointId: string; hostname: string; timestamp: string }) {
    this.cache.updateEndpoint(data.endpointId, (old) => ({
      ...old,
      status: 'online',
      lastSeen: data.timestamp
    }));
  }

  handleEndpointOffline(data: { endpointId: string; hostname: string; timestamp: string }) {
    this.cache.updateEndpoint(data.endpointId, (old) => ({
      ...old,
      status: 'offline',
      lastSeen: data.timestamp
    }));
  }

  handleSecurityUpdate(data: { endpointId: string; hostname: string; status: string; timestamp: string }) {
    // Basic mapping for demo purposes. Real implementation would parse status to compute score.
    const newScore = data.status === 'secure' ? 95 : 65;
    const newCompliance = data.status === 'secure' ? 'compliant' : 'non-compliant';
    
    this.cache.updateEndpoint(data.endpointId, (old) => ({
      ...old,
      securityScore: newScore,
      compliance: newCompliance,
      lastSeen: data.timestamp
    }));
  }

  handleAlertCreated(data: { endpointId: string; severity: string; timestamp: string }) {
    this.cache.updateEndpoint(data.endpointId, (old) => ({
      ...old,
      alerts: old.alerts + 1,
      lastSeen: data.timestamp
    }));
  }

  handleAlertResolved(data: { alertId: string; endpointId: string; timestamp: string }) {
    this.cache.updateEndpoint(data.endpointId, (old) => ({
      ...old,
      alerts: Math.max(0, old.alerts - 1),
      lastSeen: data.timestamp
    }));
  }
}
