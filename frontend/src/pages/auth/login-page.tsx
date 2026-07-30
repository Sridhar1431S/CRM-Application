import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@tanstack/react-query";
import { useNavigate, useLocation } from "react-router-dom";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/store/auth-store";
import { Button } from "@/components/ui/button";
import { Input, Label, FieldError } from "@/components/ui/input";
import { extractErrorMessage } from "@/lib/api-client";
import { useToast } from "@/components/ui/toast";
import { useMemo, useState } from "react";
import { Eye, EyeOff } from "lucide-react";

const loginSchema = z.object({
  email: z.string().min(1, "Email is required").email("Enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

const registerSchema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().min(1, "Email is required").email("Enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  password_confirm: z.string().min(1, "Confirm your password"),
  role: z.enum(["admin", "sales_rep"]),
}).refine((data) => data.password === data.password_confirm, {
  path: ["password_confirm"],
  message: "Passwords do not match",
});

type LoginForm = z.infer<typeof loginSchema>;
type RegisterForm = z.infer<typeof registerSchema>;

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const setAuth = useAuthStore((s) => s.setAuth);
  const { toast } = useToast();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const selectedRole = useMemo(() => {
    return (location.state as { role?: "admin" | "sales_rep" } | null)?.role ?? null;
  }, [location.state]);

  const loginForm = useForm<LoginForm>({ resolver: zodResolver(loginSchema) });
  const registerForm = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      role: selectedRole ?? "sales_rep",
    },
  });

  const loginMutation = useMutation({
    mutationFn: (data: LoginForm) => authApi.login(data.email, data.password),
    onSuccess: (data) => {
      setAuth(data.user, data.access);
      const from = (location.state as { from?: Location })?.from?.pathname || "/dashboard";
      navigate(from, { replace: true });
    },
    onError: (error) => {
      toast({ title: "Login failed", description: extractErrorMessage(error), variant: "error" });
    },
  });

  const registerMutation = useMutation({
    mutationFn: (data: RegisterForm) => authApi.register(data),
    onSuccess: () => {
      toast({ title: "Account created", description: "You can now sign in with your new credentials.", variant: "success" });
      setMode("login");
      registerForm.reset();
    },
    onError: (error) => {
      toast({ title: "Sign up failed", description: extractErrorMessage(error), variant: "error" });
    },
  });

  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center">
          <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-xl bg-brand-600 text-lg font-bold text-white">
            C
          </div>
          <h1 className="text-xl font-semibold text-ink-900">Welcome to CRM Lite</h1>
          <p className="mt-1 text-sm text-ink-500">Sign in to manage your pipeline</p>
        </div>

        <div className="rounded-[var(--radius-card)] border border-border bg-surface p-6 shadow-[var(--shadow-card)]">
          <div className="mb-4 grid grid-cols-2 rounded-lg border border-border bg-canvas p-1">
            <button
              type="button"
              onClick={() => setMode("login")}
              className={`rounded-md px-3 py-2 text-sm font-medium transition ${mode === "login" ? "bg-brand-600 text-white shadow-sm" : "text-ink-600"}`}
            >
              Login
            </button>
            <button
              type="button"
              onClick={() => setMode("signup")}
              className={`rounded-md px-3 py-2 text-sm font-medium transition ${mode === "signup" ? "bg-brand-600 text-white shadow-sm" : "text-ink-600"}`}
            >
              Sign up
            </button>
          </div>

          {mode === "login" ? (
            <form onSubmit={loginForm.handleSubmit((data) => loginMutation.mutate(data))} className="space-y-4">
              <div>
                <Label htmlFor="email">Email address</Label>
                <Input id="email" type="email" placeholder="you@company.com" {...loginForm.register("email")} />
                <FieldError message={loginForm.formState.errors.email?.message} />
              </div>
              <div>
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    className="pr-9"
                    {...loginForm.register("password")}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-ink-400 hover:text-ink-700"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                <FieldError message={loginForm.formState.errors.password?.message} />
              </div>
              <Button type="submit" className="w-full" disabled={loginMutation.isPending}>
                {loginMutation.isPending ? "Signing in..." : "Sign in"}
              </Button>
            </form>
          ) : (
            <form onSubmit={registerForm.handleSubmit((data) => registerMutation.mutate(data))} className="space-y-4">
              <div>
                <Label htmlFor="name">Full name</Label>
                <Input id="name" placeholder="Jane Doe" {...registerForm.register("name")} />
                <FieldError message={registerForm.formState.errors.name?.message} />
              </div>
              <div>
                <Label htmlFor="signup-email">Email address</Label>
                <Input id="signup-email" type="email" placeholder="you@company.com" {...registerForm.register("email")} />
                <FieldError message={registerForm.formState.errors.email?.message} />
              </div>
              <div>
                <Label htmlFor="role">Role</Label>
                <select
                  id="role"
                  className="flex h-9 w-full rounded-lg border border-border-strong bg-surface px-3 text-sm text-ink-900 shadow-sm transition-all duration-200"
                  {...registerForm.register("role")}
                >
                  <option value="sales_rep">Sales Rep</option>
                  <option value="admin">Admin</option>
                </select>
                <FieldError message={registerForm.formState.errors.role?.message} />
              </div>
              <div>
                <Label htmlFor="signup-password">Password</Label>
                <div className="relative">
                  <Input
                    id="signup-password"
                    type={showPassword ? "text" : "password"}
                    placeholder="At least 8 characters"
                    className="pr-9"
                    {...registerForm.register("password")}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-ink-400 hover:text-ink-700"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                <FieldError message={registerForm.formState.errors.password?.message} />
              </div>
              <div>
                <Label htmlFor="confirm-password">Confirm password</Label>
                <div className="relative">
                  <Input
                    id="confirm-password"
                    type={showConfirmPassword ? "text" : "password"}
                    placeholder="Re-enter password"
                    className="pr-9"
                    {...registerForm.register("password_confirm")}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword((v) => !v)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-ink-400 hover:text-ink-700"
                  >
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                <FieldError message={registerForm.formState.errors.password_confirm?.message} />
              </div>
              <Button type="submit" className="w-full" disabled={registerMutation.isPending}>
                {registerMutation.isPending ? "Creating account..." : "Create account"}
              </Button>
            </form>
          )}
        </div>

        {selectedRole ? (
          <div className="mt-4 rounded-lg border border-brand-200 bg-brand-50 px-3 py-2 text-sm text-brand-700 dark:border-brand-900 dark:bg-brand-950/40 dark:text-brand-300">
            Signing in as <span className="font-semibold capitalize">{selectedRole === "admin" ? "Admin" : "Sales Rep"}</span>
          </div>
        ) : null}

        <div className="mt-5 rounded-lg border border-border bg-surface/70 p-3.5 text-xs text-ink-500">
          <p className="mb-1 font-medium text-ink-700">Demo credentials</p>
          <p>Admin: admin@crmlite.com / Admin@12345</p>
          <p>Sales rep: priya@crmlite.com / Rep@12345</p>
        </div>
      </div>
    </div>
  );
}
