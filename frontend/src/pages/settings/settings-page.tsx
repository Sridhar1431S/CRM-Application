import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { LogOut } from "lucide-react";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/store/auth-store";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";

export default function SettingsPage() {
  const navigate = useNavigate();
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const { toast } = useToast();

  const logoutMutation = useMutation({
    mutationFn: authApi.logout,
    onSettled: () => {
      clearAuth();
      navigate("/login", { replace: true });
      toast({ title: "Logged out", variant: "info" });
    },
  });

  return (
    <div className="max-w-xl space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-ink-900">Settings</h2>
        <p className="text-sm text-ink-500">Manage your session and preferences.</p>
      </div>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>Session</CardTitle>
            <CardDescription>Sign out of CRM Lite on this device.</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <Button variant="secondary" onClick={() => logoutMutation.mutate()} disabled={logoutMutation.isPending}>
            <LogOut className="h-4 w-4" />
            {logoutMutation.isPending ? "Signing out..." : "Log out"}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>About</CardTitle>
            <CardDescription>CRM Lite — take-home assignment build.</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-ink-500">
            Additional preferences (notifications, theme, and language) are planned for a future release. See the
            README's "Future Improvements" section for the full roadmap.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
