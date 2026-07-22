import { EndpointDetails } from '../types';
import { EndpointDetailsRepository } from './EndpointDetailsRepository';

export class EndpointDetailsApiRepository implements EndpointDetailsRepository {
  async getEndpointDetails(id: string): Promise<EndpointDetails> {
    const response = await fetch(`/api/endpoints/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch endpoint details for ${id}`);
    }
    return response.json();
  }

  async refreshEndpoint(id: string): Promise<void> {
    const response = await fetch(`/api/endpoints/${id}/refresh`, { method: 'POST' });
    if (!response.ok) {
      throw new Error(`Failed to refresh endpoint ${id}`);
    }
  }
}
