import { EndpointRepository } from './EndpointRepository';
import { EndpointApiRepository } from './EndpointApiRepository';
import { EndpointDetailsRepository } from './EndpointDetailsRepository';
import { EndpointDetailsApiRepository } from './EndpointDetailsApiRepository';

export const endpointRepository: EndpointRepository = new EndpointApiRepository();
export const endpointDetailsRepository: EndpointDetailsRepository = new EndpointDetailsApiRepository();

