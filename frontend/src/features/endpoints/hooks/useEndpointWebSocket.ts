import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useWebSocket } from '../../../contexts/WebSocketProvider';
import { EndpointEventAdapter } from '../adapters/EndpointEventAdapter';
import { EndpointCacheService } from '../services/EndpointCacheService';

export function useEndpointWebSocket() {
  const { subscribe } = useWebSocket();
  const queryClient = useQueryClient();

  useEffect(() => {
    const cacheService = new EndpointCacheService(queryClient);
    const adapter = new EndpointEventAdapter(cacheService);

    const unsubOnline = subscribe('endpoint_online', (data: unknown) => adapter.handleEndpointOnline(data as { endpointId: string; hostname: string; timestamp: string }));
    const unsubOffline = subscribe('endpoint_offline', (data: unknown) => adapter.handleEndpointOffline(data as { endpointId: string; hostname: string; timestamp: string }));
    const unsubSec = subscribe('security_update', (data: unknown) => adapter.handleSecurityUpdate(data as { endpointId: string; hostname: string; status: string; timestamp: string }));
    const unsubAlertCreated = subscribe('alert_created', (data: unknown) => adapter.handleAlertCreated(data as { endpointId: string; severity: string; timestamp: string }));
    const unsubAlertResolved = subscribe('alert_resolved', (data: unknown) => adapter.handleAlertResolved(data as { alertId: string; endpointId: string; timestamp: string }));

    return () => {
      unsubOnline();
      unsubOffline();
      unsubSec();
      unsubAlertCreated();
      unsubAlertResolved();
    };
  }, [subscribe, queryClient]);
}
