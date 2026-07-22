import { EndpointFilters, EndpointListResponse, EndpointPagination, EndpointSort } from '../types';
import { EndpointRepository } from './EndpointRepository';
import { apiClient } from '../../../api/client';

export class EndpointApiRepository implements EndpointRepository {
  async getEndpoints(
    filters?: EndpointFilters,
    sort?: EndpointSort,
    pagination?: EndpointPagination
  ): Promise<EndpointListResponse> {
    const params = new URLSearchParams();
    if (filters?.search) params.append('search', filters.search);
    if (filters?.status) params.append('status', filters.status);
    if (sort) {
      params.append('sort_field', sort.field);
      params.append('sort_direction', sort.direction);
    }
    if (pagination) {
      params.append('page', pagination.page.toString());
      params.append('page_size', pagination.pageSize.toString());
    }

    const response = await apiClient.get<EndpointListResponse>(`/endpoints?${params.toString()}`);
    return response;
  }
}
