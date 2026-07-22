// EXAMPLE ONLY — shows how your existing data layer plugs into the new
// presentational EndpointDetailsPage. Not part of the UI deliverable;
// delete or adapt this to match your actual hooks/router.
//
// import { useParams } from 'react-router-dom';
// import { useEndpointDetails } from '../../hooks/useEndpointDetails';
// import { useEndpointDetailsWebSocket } from '../../hooks/useEndpointDetailsWebSocket';
// import { WidgetErrorBoundary } from '../../../../components/layout/WidgetErrorBoundary';
// import { EndpointDetailsPage } from './EndpointDetailsPage';
//
// function EndpointDetailsRoute() {
//   const { id } = useParams<{ id: string }>();
//   const { data: endpoint, isLoading } = useEndpointDetails(id || '');
//   useEndpointDetailsWebSocket(id || '');
//
//   return (
//     <WidgetErrorBoundary title={`Endpoint Details Error (${id})`}>
//       <EndpointDetailsPage endpoint={endpoint} isLoading={isLoading} />
//     </WidgetErrorBoundary>
//   );
// }
//
// export default EndpointDetailsRoute;
