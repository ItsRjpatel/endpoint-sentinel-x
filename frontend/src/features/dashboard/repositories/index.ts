import { DashboardApiRepository } from './DashboardApiRepository';
import { DashboardRepository } from './DashboardRepository';

export const dashboardRepository: DashboardRepository = new DashboardApiRepository();
