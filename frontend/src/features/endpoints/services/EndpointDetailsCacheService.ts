import { QueryClient } from '@tanstack/react-query';
import { ENDPOINT_DETAILS_QUERY_KEY } from '../hooks/useEndpointDetails';
import { EndpointDetails } from '../types';

export interface IEndpointDetailsCache {
  updateEndpointDetails(id: string, updater: (old: EndpointDetails) => EndpointDetails): void;
}

export class EndpointDetailsCacheService implements IEndpointDetailsCache {
  constructor(private queryClient: QueryClient) {}

  updateEndpointDetails(id: string, updater: (old: EndpointDetails) => EndpointDetails) {
    this.queryClient.setQueryData<EndpointDetails>(
      ENDPOINT_DETAILS_QUERY_KEY(id),
      (oldData) => {
        if (!oldData) return oldData;
        return updater(oldData);
      }
    );
  }
}
