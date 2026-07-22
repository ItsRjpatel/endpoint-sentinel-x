import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useWebSocket } from '../../../contexts/WebSocketProvider';
import { DashboardEventAdapter } from '../adapters/DashboardEventAdapter';
import { HealthDataPoint, DashboardAlert, DashboardCommand } from '../types';
import { DashboardCacheService } from '../services/DashboardCacheService';

export function useDashboardWebSocket() {
  const { subscribe } = useWebSocket();
  const queryClient = useQueryClient();

  useEffect(() => {
    const cacheService = new DashboardCacheService(queryClient);
    const adapter = new DashboardEventAdapter(cacheService);

    const unsubOnline = subscribe('endpoint_online', (data: unknown) => adapter.handleEndpointOnline(data as { endpointId: string; hostname: string; timestamp: string }));
    const unsubOffline = subscribe('endpoint_offline', (data: unknown) => adapter.handleEndpointOffline(data as { endpointId: string; hostname: string; timestamp: string }));
    const unsubPerf = subscribe('performance_update', (data: unknown) => adapter.handlePerformanceUpdate(data as HealthDataPoint));
    const unsubSec = subscribe('security_update', (data: unknown) => adapter.handleSecurityUpdate(data as { endpointId: string; hostname: string; status: string; timestamp: string }));
    const unsubAlertCreated = subscribe('alert_created', (data: unknown) => adapter.handleAlertCreated(data as DashboardAlert));
    const unsubAlertResolved = subscribe('alert_resolved', (data: unknown) => adapter.handleAlertResolved(data as { alertId: string; endpoint: string; timestamp: string }));
    const unsubCmd = subscribe('command_completed', (data: unknown) => adapter.handleCommandCompleted(data as DashboardCommand));

    return () => {
      unsubOnline();
      unsubOffline();
      unsubPerf();
      unsubSec();
      unsubAlertCreated();
      unsubAlertResolved();
      unsubCmd();
    };
  }, [subscribe, queryClient]);
}
