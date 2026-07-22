import { Component, ErrorInfo, ReactNode } from "react";
import { Shield } from "lucide-react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4 font-sans text-text-primary">
          <div className="w-full max-w-md p-8 rounded-2xl border border-danger/50 bg-card shadow-lg space-y-6 text-center">
            <div className="inline-flex p-3 rounded-full bg-danger/10 border border-danger/20 text-danger mb-2">
              <Shield className="h-8 w-8" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-danger">System Fault Detected</h1>
              <p className="text-sm text-text-muted mt-2">
                The console encountered an unexpected rendering error. 
              </p>
            </div>
            
            <div className="bg-surface-secondary p-4 rounded-lg text-left overflow-auto border border-border">
              <p className="text-xs font-mono text-danger break-words">
                {this.state.error?.message || "Unknown Application Error"}
              </p>
            </div>
            
            <button
              onClick={() => window.location.reload()}
              className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 transition-colors"
            >
              Restart Application
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
