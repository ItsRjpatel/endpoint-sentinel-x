import { DashboardMockRepository } from './DashboardMockRepository';
import { DashboardRepository } from './DashboardRepository';

// Exporting mock repository for Sprint 5.2 as endpoints are not yet available.
// Switch to DashboardApiRepository once endpoints are live.
export const dashboardRepository: DashboardRepository = new DashboardMockRepository();
