import { useParams } from 'react-router-dom';
import { useEndpointDetails } from '../../hooks/useEndpointDetails';
import { useEndpointDetailsWebSocket } from '../../hooks/useEndpointDetailsWebSocket';
import { WidgetErrorBoundary } from '../../../../components/layout/WidgetErrorBoundary';
import { EndpointDetailsPage } from './EndpointDetailsPage';

export function EndpointDetailsRoute() {
  const { id } = useParams<{ id: string }>();

  // Use the real hooks for data fetching and real-time updates
  const { data: endpoint, isLoading } = useEndpointDetails(id || '');
  useEndpointDetailsWebSocket(id || '');

  return (
    <WidgetErrorBoundary title={`Endpoint Details Error (${id})`}>
      <EndpointDetailsPage endpoint={endpoint} isLoading={isLoading} />
    </WidgetErrorBoundary>
  );
}

export default EndpointDetailsRoute;
