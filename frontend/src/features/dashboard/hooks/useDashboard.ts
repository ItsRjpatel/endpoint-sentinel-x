import { useQuery } from '@tanstack/react-query';
import { dashboardRepository } from '../repositories';

export const DASHBOARD_QUERY_KEYS = {
  fleetOverview: ['dashboard', 'fleetOverview'],
  fleetHealth: ['dashboard', 'fleetHealth'],
  activityFeed: ['dashboard', 'activityFeed'],
  securityOverview: ['dashboard', 'securityOverview'],
  recentAlerts: ['dashboard', 'recentAlerts'],
  recentCommands: ['dashboard', 'recentCommands'],
};

export function useFleetOverview() {
  return useQuery({
    queryKey: DASHBOARD_QUERY_KEYS.fleetOverview,
    queryFn: () => dashboardRepository.getFleetOverview(),
    staleTime: 60000, // 1 minute
    throwOnError: true,
  });
}

export function useFleetHealth() {
  return useQuery({
    queryKey: DASHBOARD_QUERY_KEYS.fleetHealth,
    queryFn: () => dashboardRepository.getFleetHealth(),
    staleTime: 60000,
    throwOnError: true,
  });
}

export function useActivityFeed() {
  return useQuery({
    queryKey: DASHBOARD_QUERY_KEYS.activityFeed,
    queryFn: () => dashboardRepository.getActivityFeed(),
    staleTime: 30000,
    throwOnError: true,
  });
}

export function useSecurityOverview() {
  return useQuery({
    queryKey: DASHBOARD_QUERY_KEYS.securityOverview,
    queryFn: () => dashboardRepository.getSecurityOverview(),
    staleTime: 300000, // 5 minutes
    throwOnError: true,
  });
}

export function useRecentAlerts() {
  return useQuery({
    queryKey: DASHBOARD_QUERY_KEYS.recentAlerts,
    queryFn: () => dashboardRepository.getRecentAlerts(),
    staleTime: 30000,
    throwOnError: true,
  });
}

export function useRecentCommands() {
  return useQuery({
    queryKey: DASHBOARD_QUERY_KEYS.recentCommands,
    queryFn: () => dashboardRepository.getRecentCommands(),
    staleTime: 15000,
    throwOnError: true,
  });
}
