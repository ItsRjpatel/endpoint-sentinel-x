import { IEndpointDetailsCache } from '../services/EndpointDetailsCacheService';

export class EndpointDetailsEventAdapter {
  constructor(private cache: IEndpointDetailsCache) { }

  handlePerformanceUpdate(data: { endpointId: string; cpu: number; ram: number; disk: number; networkIn: number; networkOut: number; timestamp: string }) {
    this.cache.updateEndpointDetails(data.endpointId, (old) => {
      const newPoint = {
        time: data.timestamp,
        cpu: data.cpu,
        memory: data.ram,
        disk: data.disk,
        networkIn: data.networkIn,
        networkOut: data.networkOut
      };

      const newHistory = [...old.performance.history, newPoint].slice(-24); // Keep last 24 points

      return {
        ...old,
        performance: {
          currentCpuUsage: data.cpu,
          currentRamUsage: data.ram,
          currentDiskUsage: data.disk,
          history: newHistory
        }
      };
    });
  }

  handleStatusChange(data: { endpointId: string; status: 'online' | 'offline' | 'inactive'; timestamp: string }) {
    this.cache.updateEndpointDetails(data.endpointId, (old) => ({
      ...old,
      status: data.status,
      lastSeen: data.timestamp
    }));
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  handleTimelineEvent(data: { endpointId: string; eventId: string; type: any; message: string; severity: any; timestamp: string }) {
    this.cache.updateEndpointDetails(data.endpointId, (old) => {
      const newEvent = {
        id: data.eventId,
        type: data.type,
        message: data.message,
        severity: data.severity,
        timestamp: data.timestamp
      };
      return {
        ...old,
        timeline: [newEvent, ...old.timeline]
      };
    });
  }
}
