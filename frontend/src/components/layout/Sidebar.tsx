import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { 
  Shield, 
  LayoutDashboard, 
  Monitor, 
  Bell, 
  CheckSquare, 
  History, 
  FileText, 
  Settings as SettingsIcon,
  Activity,
  ChevronLeft,
  ChevronRight
} from "lucide-react";

const menuItems = [
  { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { name: "Endpoints", path: "/endpoints", icon: Monitor },
  { name: "Monitoring", path: "/monitoring", icon: Activity },
  { name: "Alerts", path: "/alerts", icon: Bell },
  { name: "Security", path: "/security", icon: Shield },
  { name: "Compliance", path: "/compliance", icon: CheckSquare },
  { name: "Audit Logs", path: "/audit", icon: History },
  { name: "Reports", path: "/reports", icon: FileText },
  { name: "Settings", path: "/settings", icon: SettingsIcon },
];

export function Sidebar() {
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(() => {
    const saved = localStorage.getItem('sidebarCollapsed');
    return saved ? JSON.parse(saved) : false;
  });

  useEffect(() => {
    localStorage.setItem('sidebarCollapsed', JSON.stringify(isCollapsed));
  }, [isCollapsed]);

  return (
    <aside 
      className={`border-r border-border bg-surface-secondary/50 flex flex-col transition-all duration-300 ease-in-out shrink-0 ${
        isCollapsed ? 'w-[80px]' : 'w-[240px]'
      }`}
    >
      <div className={`h-16 flex items-center border-b border-border ${isCollapsed ? 'justify-center px-0' : 'px-6 gap-2'}`}>
        <Shield className="h-6 w-6 shrink-0 text-primary animate-pulse" />
        {!isCollapsed && (
          <span className="font-bold text-lg tracking-wider text-text-primary whitespace-nowrap overflow-hidden">
            SENTINEL X
          </span>
        )}
      </div>

      <nav className="flex-1 py-6 space-y-1 flex flex-col items-center w-full px-3 overflow-hidden">
        {menuItems.map((item) => {
          const isActive = location.pathname.startsWith(item.path);
          return (
            <Link
              key={item.name}
              to={item.path}
              title={isCollapsed ? item.name : undefined}
              className={`flex items-center gap-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 w-full ${
                isCollapsed ? 'justify-center px-0' : 'px-3'
              } ${
                isActive 
                  ? "bg-accent text-accent-foreground" 
                  : "text-text-secondary hover:text-text-primary hover:bg-surface"
              }`}
            >
              <item.icon className="h-5 w-5 shrink-0" />
              {!isCollapsed && <span className="whitespace-nowrap">{item.name}</span>}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-border flex justify-center">
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-surface transition-colors"
          title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        >
          {isCollapsed ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
        </button>
      </div>
    </aside>
  );
}
