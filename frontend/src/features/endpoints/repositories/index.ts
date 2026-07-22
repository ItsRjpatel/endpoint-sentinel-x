import { EndpointRepository } from './EndpointRepository';
import { EndpointMockRepository } from './EndpointMockRepository';
import { EndpointDetailsRepository } from './EndpointDetailsRepository';
import { EndpointDetailsMockRepository } from './EndpointDetailsMockRepository';

// For Sprint 5.3, we use the Mock Repository.
export const endpointRepository: EndpointRepository = new EndpointMockRepository();

// For Sprint 5.4, we use the Mock Repository.
export const endpointDetailsRepository: EndpointDetailsRepository = new EndpointDetailsMockRepository();

