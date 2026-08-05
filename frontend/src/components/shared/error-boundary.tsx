import * as React from "react";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorBoundaryState {
  error: Error | null;
}

/**
 * Catches render-time errors that would otherwise unmount the whole app
 * and leave the user staring at a blank page with the failure only visible
 * in the console.
 */
export class ErrorBoundary extends React.Component<{ children: React.ReactNode }, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("Unhandled UI error", error, info.componentStack);
  }

  render() {
    const { error } = this.state;
    if (!error) return this.props.children;

    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-3 px-6 text-center">
        <AlertTriangle className="h-8 w-8 text-danger-600" />
        <p className="text-base font-semibold text-ink-900">Something went wrong</p>
        <p className="max-w-md text-sm text-ink-500">{error.message}</p>
        <Button className="mt-2" onClick={() => window.location.reload()}>
          Reload page
        </Button>
      </div>
    );
  }
}
