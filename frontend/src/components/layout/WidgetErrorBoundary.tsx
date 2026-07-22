import { Component, ErrorInfo, ReactNode } from "react";
import { Card, CardContent } from "../ui/Card";
import { AlertCircle } from "lucide-react";
import { useQueryErrorResetBoundary } from "@tanstack/react-query";

interface Props {
  children: ReactNode;
  title?: string;
  onReset: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class WidgetErrorBoundaryInner extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Widget error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <Card className="h-full border-danger/20 bg-danger/5 flex items-center justify-center p-6">
          <CardContent className="flex flex-col items-center text-center space-y-4 pt-6">
            <AlertCircle className="h-8 w-8 text-danger" />
            <div>
              <h3 className="font-semibold text-danger">
                {this.props.title ? `${this.props.title} Failed` : "Widget Error"}
              </h3>
              <p className="text-xs text-danger/80 mt-1 max-w-[250px] truncate">
                {this.state.error?.message || "Failed to load widget data."}
              </p>
            </div>
            <button
              onClick={() => {
                this.props.onReset();
                this.setState({ hasError: false, error: null });
              }}
              className="text-xs font-medium text-danger hover:underline focus:outline-none focus:ring-2 focus:ring-danger focus:ring-offset-2 rounded"
            >
              Retry
            </button>
          </CardContent>
        </Card>
      );
    }

    return this.props.children;
  }
}

export function WidgetErrorBoundary({ children, title }: Omit<Props, "onReset">) {
  const { reset } = useQueryErrorResetBoundary();
  return (
    <WidgetErrorBoundaryInner title={title} onReset={reset}>
      {children}
    </WidgetErrorBoundaryInner>
  );
}
