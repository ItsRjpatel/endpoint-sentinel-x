import { HealthDataPoint, DashboardAlert, DashboardCommand } from '../types';
import { IDashboardCache } from '../services/DashboardCacheService';

export class DashboardEventAdapter {
  constructor(private cache: IDashboardCache) {}

  handleEndpointOnline(data: { endpointId: string; hostname: string; timestamp: string }) {
    // 1. Update Fleet Overview
    this.cache.updateFleetOverview((old) => {
      if (!old) return old;
      return { ...old, online: old.online + 1, offline: Math.max(0, old.offline - 1) };
    });

    // 2. Add to Activity Feed
    this.cache.addActivityEvent({
      id: crypto.randomUUID(),
      type: 'success',
      message: `${data.hostname} came online`,
      timestamp: data.timestamp,
    });
  }

  handleEndpointOffline(data: { endpointId: string; hostname: string; timestamp: string }) {
    this.cache.updateFleetOverview((old) => {
      if (!old) return old;
      return { ...old, online: Math.max(0, old.online - 1), offline: old.offline + 1 };
    });

    this.cache.addActivityEvent({
      id: crypto.randomUUID(),
      type: 'error',
      message: `Agent disconnected: ${data.hostname}`,
      timestamp: data.timestamp,
    });
  }

  handlePerformanceUpdate(data: HealthDataPoint) {
    this.cache.addPerformancePoint(data);
  }

  handleSecurityUpdate(data: { endpointId: string; hostname: string; status: string; timestamp: string }) {
    this.cache.invalidateSecurityOverview();
    
    this.cache.addActivityEvent({
      id: crypto.randomUUID(),
      type: 'info',
      message: `Security update received from ${data.hostname}`,
      timestamp: data.timestamp,
    });
  }

  handleAlertCreated(alert: DashboardAlert) {
    this.cache.updateRecentAlerts((old) => {
      if (!old) return [alert];
      return [alert, ...old].slice(0, 10);
    });

    this.cache.updateFleetOverview((old) => {
      if (!old) return old;
      return { 
        ...old, 
        activeAlerts: old.activeAlerts + 1,
        criticalAlerts: alert.severity === 'critical' ? old.criticalAlerts + 1 : old.criticalAlerts
      };
    });

    this.cache.addActivityEvent({
      id: crypto.randomUUID(),
      type: 'warning',
      message: `New ${alert.severity} alert on ${alert.endpoint}: ${alert.message}`,
      timestamp: alert.timestamp,
    });
  }

  handleAlertResolved(data: { alertId: string; endpoint: string; timestamp: string }) {
    this.cache.updateRecentAlerts((old) => {
      if (!old) return old;
      return old.map(a => a.id === data.alertId ? { ...a, status: 'resolved' as const } : a);
    });

    this.cache.invalidateFleetOverview();

    this.cache.addActivityEvent({
      id: crypto.randomUUID(),
      type: 'success',
      message: `Alert resolved on ${data.endpoint}`,
      timestamp: data.timestamp,
    });
  }

  handleCommandCompleted(command: DashboardCommand) {
    this.cache.updateRecentCommands((old) => {
      if (!old) return [command];
      return [command, ...old.filter(c => c.id !== command.id)].slice(0, 10);
    });

    this.cache.invalidateFleetOverview();

    this.cache.addActivityEvent({
      id: crypto.randomUUID(),
      type: command.status === 'failed' ? 'error' : 'success',
      message: `Command '${command.command}' ${command.status} on ${command.endpoint}`,
      timestamp: new Date().toISOString(),
    });
  }
}
