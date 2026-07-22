import { useAuth } from "../../contexts/AuthContext";
import { useWebSocket } from "../../contexts/WebSocketProvider";
import { useTheme } from "../theme/ThemeProvider";
import { Moon, Sun, Laptop } from "lucide-react";

export function Header() {
  const { user, logout } = useAuth();
  const { status } = useWebSocket();
  const { theme, setTheme } = useTheme();

  return (
    <header className="h-16 border-b border-border flex items-center justify-between px-8 bg-surface-secondary/50">
      <h2 className="text-sm font-semibold text-text-secondary tracking-wider uppercase">
        Endpoint Console
      </h2>
      
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          {status === "connected" ? (
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-success/10 text-success border border-success/20">
              <span className="w-1.5 h-1.5 rounded-full bg-success mr-1.5 animate-ping"></span>
              Live Sync
            </span>
          ) : (
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-warning/10 text-warning border border-warning/20">
              <span className="w-1.5 h-1.5 rounded-full bg-warning mr-1.5"></span>
              {status}
            </span>
          )}
        </div>

        <div className="flex items-center gap-1 border-l border-border pl-6">
          <button onClick={() => setTheme("light")} className={`p-1.5 rounded-md ${theme === 'light' ? 'bg-surface text-primary' : 'text-text-muted hover:text-text-primary'}`}>
            <Sun className="h-4 w-4" />
          </button>
          <button onClick={() => setTheme("dark")} className={`p-1.5 rounded-md ${theme === 'dark' ? 'bg-surface text-primary' : 'text-text-muted hover:text-text-primary'}`}>
            <Moon className="h-4 w-4" />
          </button>
          <button onClick={() => setTheme("system")} className={`p-1.5 rounded-md ${theme === 'system' ? 'bg-surface text-primary' : 'text-text-muted hover:text-text-primary'}`}>
            <Laptop className="h-4 w-4" />
          </button>
        </div>

        <div className="flex items-center gap-3 border-l border-border pl-6">
          <div className="text-right">
            <p className="text-sm font-semibold text-text-primary">{user?.email}</p>
            <p className="text-xs text-text-muted capitalize">{user?.role}</p>
          </div>
          <button 
            onClick={logout}
            className="text-xs text-danger hover:text-danger-foreground hover:bg-danger px-3 py-1.5 rounded transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
