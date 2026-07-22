import { QueryClient } from '@tanstack/react-query';
import { ENDPOINT_QUERY_KEYS } from '../hooks/useEndpoints';
import { Endpoint, EndpointListResponse } from '../types';

export interface IEndpointCache {
  updateEndpoint(id: string, updater: (old: Endpoint) => Endpoint): void;
}

export class EndpointCacheService implements IEndpointCache {
  constructor(private queryClient: QueryClient) {}

  updateEndpoint(id: string, updater: (old: Endpoint) => Endpoint) {
    this.queryClient.setQueriesData<EndpointListResponse>(
      { queryKey: ENDPOINT_QUERY_KEYS.all },
      (oldData) => {
        if (!oldData) return oldData;
        
        // Find if the endpoint exists in this page of data
        const endpointIndex = oldData.data.findIndex(ep => ep.id === id);
        if (endpointIndex === -1) return oldData; // Not on this page, ignore

        // Update it
        const newData = [...oldData.data];
        newData[endpointIndex] = updater(newData[endpointIndex]);

        return {
          ...oldData,
          data: newData
        };
      }
    );
  }
}
