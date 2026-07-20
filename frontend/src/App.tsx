import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { 
  Shield, 
  LayoutDashboard, 
  Monitor, 
  Bell, 
  Lock, 
  CheckSquare, 
  History, 
  FileText, 
  Settings as SettingsIcon,
  Activity
} from 'lucide-react';

const queryClient = new QueryClient();

// Shell Layout Component
const DashboardShell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const menuItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Endpoints', path: '/endpoints', icon: Monitor },
    { name: 'Monitoring', path: '/monitoring', icon: Activity },
    { name: 'Alerts', path: '/alerts', icon: Bell },
    { name: 'Security', path: '/security', icon: Shield },
    { name: 'Compliance', path: '/compliance', icon: CheckSquare },
    { name: 'Audit Logs', path: '/audit', icon: History },
    { name: 'Reports', path: '/reports', icon: FileText },
    { name: 'Settings', path: '/settings', icon: SettingsIcon },
  ];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 bg-slate-900/50 flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-2">
          <Shield className="h-6 w-6 text-blue-500 animate-pulse" />
          <span className="font-bold text-lg tracking-wider bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
            SENTINEL X
          </span>
        </div>
        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          {menuItems.map((item) => (
            <Link
              key={item.name}
              to={item.path}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-400 hover:text-slate-100 hover:bg-slate-800/60 transition-all duration-200"
            >
              <item.icon className="h-4 w-4" />
              {item.name}
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center font-bold text-xs text-slate-950">
              AD
            </div>
            <div className="text-xs">
              <p className="font-semibold text-slate-200">Administrator</p>
              <p className="text-slate-500">admin@sentinelx.local</p>
            </div>
          </div>
          <Link to="/login" className="text-xs text-slate-500 hover:text-slate-300">
            <Lock className="h-3.5 w-3.5" />
          </Link>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden bg-slate-950">
        <header className="h-16 border-b border-slate-800 flex items-center justify-between px-8 bg-slate-900/30">
          <h2 className="text-sm font-semibold text-slate-400 tracking-wider">ENTERPRISE SYSTEM FOUNDATION</h2>
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-ping"></span>
              API Connected
            </span>
          </div>
        </header>
        <div className="flex-1 overflow-auto p-8">
          {children}
        </div>
      </main>
    </div>
  );
};

// Feature Skeletons Components
const PlaceholderView: React.FC<{ name: string }> = ({ name }) => (
  <div className="space-y-6">
    <div>
      <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent">
        {name}
      </h1>
      <p className="text-slate-400 mt-2 text-sm">
        Enterprise monitoring platform sub-module foundation active.
      </p>
    </div>
    
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/30 backdrop-blur-sm space-y-2">
        <h3 className="font-semibold text-slate-200">Subsystem Status</h3>
        <p className="text-sm text-slate-500">Monitoring hooks ready to register event streams.</p>
      </div>
      <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/30 backdrop-blur-sm space-y-2">
        <h3 className="font-semibold text-slate-200">Agent Pipelines</h3>
        <p className="text-sm text-slate-500">Pre-allocated buffers configured for 10k+ concurrent hosts.</p>
      </div>
      <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/30 backdrop-blur-sm space-y-2">
        <h3 className="font-semibold text-slate-200">Audit Compliance</h3>
        <p className="text-sm text-slate-500">Security policies mapped to centralized event logs.</p>
      </div>
    </div>

    <div className="border border-slate-800 bg-slate-900/20 rounded-xl p-8 flex items-center justify-center h-64">
      <div className="text-center space-y-3">
        <Activity className="h-8 w-8 text-blue-500/50 mx-auto animate-pulse" />
        <p className="text-slate-400 text-sm">Waiting for agent telemetry ingestion streams...</p>
      </div>
    </div>
  </div>
);

const LoginView: React.FC = () => (
  <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
    <div className="w-full max-w-md p-8 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur-md space-y-6">
      <div className="text-center space-y-2">
        <div className="inline-flex p-3 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-500 mb-2">
          <Shield className="h-8 w-8" />
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-100">Endpoint Sentinel X</h1>
        <p className="text-xs text-slate-500">Access requires organizational single-sign-on or token credentials</p>
      </div>
      
      <div className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1.5">USER ACCOUNT</label>
          <input 
            type="text" 
            disabled 
            placeholder="admin@sentinelx.local" 
            className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-400 text-sm focus:outline-none"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1.5">PASSWORD</label>
          <input 
            type="password" 
            disabled 
            placeholder="••••••••" 
            className="w-full px-3.5 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-400 text-sm focus:outline-none"
          />
        </div>
        <button 
          disabled 
          className="w-full py-2.5 rounded-lg bg-blue-600 text-slate-950 text-sm font-semibold hover:bg-blue-500 transition-colors"
        >
          Single Sign On (SSO)
        </button>
      </div>
    </div>
  </div>
);

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginView />} />
          
          <Route path="/dashboard" element={<DashboardShell><PlaceholderView name="Executive System Dashboard" /></DashboardShell>} />
          <Route path="/endpoints" element={<DashboardShell><PlaceholderView name="Endpoints Assets Registry" /></DashboardShell>} />
          <Route path="/monitoring" element={<DashboardShell><PlaceholderView name="Real-time Metrics Monitoring" /></DashboardShell>} />
          <Route path="/alerts" element={<DashboardShell><PlaceholderView name="System Trigger Alerts" /></DashboardShell>} />
          <Route path="/security" element={<DashboardShell><PlaceholderView name="Security Posture Analytics" /></DashboardShell>} />
          <Route path="/compliance" element={<DashboardShell><PlaceholderView name="CIS Baseline Compliance" /></DashboardShell>} />
          <Route path="/audit" element={<DashboardShell><PlaceholderView name="Security Audit Trails" /></DashboardShell>} />
          <Route path="/reports" element={<DashboardShell><PlaceholderView name="Operational Status Reports" /></DashboardShell>} />
          <Route path="/settings" element={<DashboardShell><PlaceholderView name="Platform Settings" /></DashboardShell>} />

          {/* Root path redirects to dashboard */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
};
export default App;
