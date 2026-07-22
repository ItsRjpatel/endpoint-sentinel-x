import { EndpointFilters, EndpointListResponse, EndpointPagination, EndpointSort } from '../types';

export interface EndpointRepository {
  getEndpoints(
    filters: EndpointFilters,
    sort: EndpointSort,
    pagination: EndpointPagination
  ): Promise<EndpointListResponse>;
}
