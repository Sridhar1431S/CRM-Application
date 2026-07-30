import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuthStore } from "@/store/auth-store";
import { initials, formatDate } from "@/lib/utils";

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user);
  if (!user) return null;

  return (
    <div className="max-w-xl space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-ink-900">Profile</h2>
        <p className="text-sm text-ink-500">Your account information.</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-100 text-lg font-semibold text-brand-700">
              {initials(user.name)}
            </div>
            <div>
              <CardTitle className="text-base">{user.name}</CardTitle>
              <CardDescription>{user.email}</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <dl className="divide-y divide-border border-t border-border text-sm">
            <div className="flex justify-between py-3">
              <dt className="text-ink-500">Role</dt>
              <dd className="font-medium capitalize text-ink-900">{user.role.replace("_", " ")}</dd>
            </div>
            <div className="flex justify-between py-3">
              <dt className="text-ink-500">Status</dt>
              <dd>
                <Badge tone={user.is_active ? "success" : "neutral"} dot>
                  {user.is_active ? "Active" : "Disabled"}
                </Badge>
              </dd>
            </div>
            <div className="flex justify-between py-3">
              <dt className="text-ink-500">Member since</dt>
              <dd className="font-medium text-ink-900">{formatDate(user.created_at)}</dd>
            </div>
          </dl>
        </CardContent>
      </Card>
    </div>
  );
}
