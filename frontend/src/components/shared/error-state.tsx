import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { extractErrorMessage } from "@/lib/api-client";

interface ErrorStateProps {
  title?: string;
  error: unknown;
  onRetry?: () => void;
}

export function ErrorState({ title = "Couldn't load this data", error, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 px-6 py-16 text-center">
      <div className="mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-canvas">
        <AlertTriangle className="h-6 w-6 text-danger-600" />
      </div>
      <p className="text-sm font-medium text-ink-900">{title}</p>
      <p className="max-w-sm text-sm text-ink-500">{extractErrorMessage(error)}</p>
      {onRetry && (
        <Button variant="secondary" size="sm" className="mt-3" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  );
}
