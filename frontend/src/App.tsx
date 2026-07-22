import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { RequireAuth } from './components/auth/RequireAuth';
import { useAuth } from './contexts/AuthContext';
import { Shield } from 'lucide-react';
import { Skeleton } from './components/ui/Skeleton';

const Dashboard = lazy(() => import('./features/dashboard/Dashboard'));
const EndpointInventory = lazy(() => import('./features/endpoints/components/EndpointInventory'));
const EndpointDetailsRoute = lazy(() => import('./features/endpoints/components/details/EndpointDetailsRoute'));

const SecurityDashboard = lazy(() => import('./features/security/SecurityDashboard'));
const PoliciesDashboard = lazy(() => import('./features/policies/PoliciesDashboard'));
// Temporary placeholder for features to be implemented in Sprint 5.2
const PlaceholderView: React.FC<{ name: string }> = ({ name }) => (
  <div className="space-y-6">
    <div>
      <h1 className="text-3xl font-extrabold tracking-tight text-text-primary">
        {name}
      </h1>
      <p className="text-text-muted mt-2 text-sm">
        Enterprise module foundation active. UI pending Sprint 5.2.
      </p>
    </div>
  </div>
);

// Temporary Login View
const LoginView: React.FC = () => {
  const { login, isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md p-8 rounded-2xl border border-border bg-card shadow-lg space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 rounded-full bg-primary/10 border border-primary/20 text-primary mb-2">
            <Shield className="h-8 w-8" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Endpoint Sentinel X</h1>
          <p className="text-xs text-text-muted">Enterprise Access Portal</p>
        </div>
        <button
          onClick={() => login("dev-token-123")}
          className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 transition-colors"
        >
          Developer Login (Sprint 5.1)
        </button>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginView />} />

      <Route path="/" element={
        <RequireAuth>
          <AppLayout />
        </RequireAuth>
      }>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="endpoints">
          <Route index element={
            <Suspense fallback={<div className="p-6 min-h-screen bg-surface-primary flex items-center justify-center"><Skeleton className="h-[400px] w-full max-w-4xl" /></div>}>
              <EndpointInventory />
            </Suspense>
          } />
          <Route path=":id" element={
            <Suspense fallback={<div className="p-6 min-h-screen bg-surface-primary flex items-center justify-center"><Skeleton className="h-[400px] w-full max-w-4xl" /></div>}>
              <EndpointDetailsRoute />
            </Suspense>
          } />
        </Route>
        <Route path="security" element={
          <Suspense fallback={<div className="p-6 min-h-screen bg-surface-primary flex items-center justify-center"><Skeleton className="h-[400px] w-full max-w-4xl" /></div>}>
            <SecurityDashboard />
          </Suspense>
        } />
        <Route path="monitoring" element={<PlaceholderView name="Real-time Metrics Monitoring" />} />
        <Route path="policies" element={
          <Suspense fallback={<div className="p-6 min-h-screen bg-surface-primary flex items-center justify-center"><Skeleton className="h-[400px] w-full max-w-4xl" /></div>}>
            <PoliciesDashboard />
          </Suspense>
        } />
        <Route path="alerts" element={<PlaceholderView name="System Trigger Alerts" />} />
        <Route path="compliance" element={<PlaceholderView name="CIS Baseline Compliance" />} />
        <Route path="audit" element={<PlaceholderView name="Security Audit Trails" />} />
        <Route path="reports" element={<PlaceholderView name="Operational Status Reports" />} />
        <Route path="settings" element={<PlaceholderView name="Platform Settings" />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

export default App;
