import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useWebSocket } from '../../../contexts/WebSocketProvider';
import { EndpointDetailsEventAdapter } from '../adapters/EndpointDetailsEventAdapter';
import { EndpointDetailsCacheService } from '../services/EndpointDetailsCacheService';

export function useEndpointDetailsWebSocket(endpointId: string) {
  const { subscribe } = useWebSocket();
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!endpointId) return;

    const cacheService = new EndpointDetailsCacheService(queryClient);
    const adapter = new EndpointDetailsEventAdapter(cacheService);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const unsubPerf = subscribe('endpoint_performance_update', (data: any) => {
      if (data.endpointId === endpointId) adapter.handlePerformanceUpdate(data);
    });
    
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const unsubStatus = subscribe('endpoint_status_change', (data: any) => {
      if (data.endpointId === endpointId) adapter.handleStatusChange(data);
    });
    
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const unsubTimeline = subscribe('endpoint_timeline_event', (data: any) => {
      if (data.endpointId === endpointId) adapter.handleTimelineEvent(data);
    });

    return () => {
      unsubPerf();
      unsubStatus();
      unsubTimeline();
    };
  }, [subscribe, queryClient, endpointId]);
}
