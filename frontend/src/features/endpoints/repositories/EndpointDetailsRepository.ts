import { EndpointDetails } from '../types';

export interface EndpointDetailsRepository {
  getEndpointDetails(id: string): Promise<EndpointDetails>;
  refreshEndpoint(id: string): Promise<void>;
}
