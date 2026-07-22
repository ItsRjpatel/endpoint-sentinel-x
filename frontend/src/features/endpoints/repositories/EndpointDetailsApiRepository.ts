import { EndpointDetails } from '../types';
import { EndpointDetailsRepository } from './EndpointDetailsRepository';
import { apiClient } from '../../../api/client';

export class EndpointDetailsApiRepository implements EndpointDetailsRepository {
  async getEndpointDetails(id: string): Promise<EndpointDetails> {
    return apiClient.get<EndpointDetails>(`/endpoints/${id}`);
  }

  async refreshEndpoint(id: string): Promise<void> {
    await apiClient.post(`/endpoints/${id}/refresh`, {});
  }
}
