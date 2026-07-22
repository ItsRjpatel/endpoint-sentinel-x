import { useQuery } from '@tanstack/react-query';
import { endpointDetailsRepository } from '../repositories';

export const ENDPOINT_DETAILS_QUERY_KEY = (id: string) => ['endpoint-details', id] as const;

export function useEndpointDetails(id: string) {
  return useQuery({
    queryKey: ENDPOINT_DETAILS_QUERY_KEY(id),
    queryFn: () => endpointDetailsRepository.getEndpointDetails(id),
    staleTime: 60000,
    throwOnError: true,
  });
}
