import { useQuery } from '@tanstack/react-query';
import { endpointRepository } from '../repositories';
import { EndpointFilters, EndpointSort, EndpointPagination } from '../types';

export const ENDPOINT_QUERY_KEYS = {
  all: ['endpoints'] as const,
  list: (filters: EndpointFilters, sort: EndpointSort, pagination: EndpointPagination) => 
    [...ENDPOINT_QUERY_KEYS.all, { filters, sort, pagination }] as const,
};

export function useEndpoints(
  filters: EndpointFilters,
  sort: EndpointSort,
  pagination: EndpointPagination
) {
  return useQuery({
    queryKey: ENDPOINT_QUERY_KEYS.list(filters, sort, pagination),
    queryFn: () => endpointRepository.getEndpoints(filters, sort, pagination),
    staleTime: 60000,
    throwOnError: true,
  });
}
