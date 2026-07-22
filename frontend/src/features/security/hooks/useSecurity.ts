import { useQuery } from '@tanstack/react-query';
import { securityRepository } from '../api/securityApi';

export const useFleetSecurity = () => {
  return useQuery({
    queryKey: ['security', 'fleet'],
    queryFn: () => securityRepository.getFleetSummary(),
    refetchInterval: 30000,
  });
};

export const useEndpointSecurity = (endpointId: number) => {
  return useQuery({
    queryKey: ['security', 'endpoint', endpointId],
    queryFn: () => securityRepository.getEndpointSummary(endpointId),
    enabled: !!endpointId,
    refetchInterval: 30000,
  });
};

export const useSecurityTimeline = (limit: number = 50) => {
  return useQuery({
    queryKey: ['security', 'timeline', limit],
    queryFn: () => securityRepository.getTimeline(limit),
    refetchInterval: 30000,
  });
};
