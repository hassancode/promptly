"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { validateLoginForm, getFieldError } from "@/lib/form-validation";
import ErrorToast from "@/components/ErrorToast";
import { APIError } from "@/lib/api-client";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [errors, setErrors] = useState<Array<{ field: string; message: string }>>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors([]);
    setErrorMessage(null);

    // Validate form
    const validationErrors = validateLoginForm(formData);
    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsSubmitting(true);

    try {
      await login(formData.email, formData.password);
      // Redirect to dashboard on successful login
      router.push("/dashboard");
    } catch (error) {
      if (error instanceof APIError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("An unexpected error occurred. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear field error when user types
    setErrors(errors.filter((err) => err.field !== e.target.name));
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-white">Welcome Back</h1>
          <p className="mt-2 text-zinc-400">Sign in to your Promptly account</p>
        </div>

        {/* Login Form */}
        <form
          onSubmit={handleSubmit}
          className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6 backdrop-blur-sm"
        >
          {/* Email Field */}
          <div className="mb-4">
            <label
              htmlFor="email"
              className="mb-2 block text-sm font-medium text-zinc-300"
            >
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={`w-full rounded-lg border ${
                getFieldError(errors, "email")
                  ? "border-red-500"
                  : "border-zinc-700"
              } bg-zinc-800 px-4 py-2 text-white placeholder-zinc-500 focus:border-brand-primary focus:outline-none focus:ring-2 focus:ring-brand-primary/50`}
              placeholder="you@example.com"
              autoComplete="email"
            />
            {getFieldError(errors, "email") && (
              <p className="mt-1 text-sm text-red-400">
                {getFieldError(errors, "email")}
              </p>
            )}
          </div>

          {/* Password Field */}
          <div className="mb-6">
            <label
              htmlFor="password"
              className="mb-2 block text-sm font-medium text-zinc-300"
            >
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={`w-full rounded-lg border ${
                getFieldError(errors, "password")
                  ? "border-red-500"
                  : "border-zinc-700"
              } bg-zinc-800 px-4 py-2 text-white placeholder-zinc-500 focus:border-brand-primary focus:outline-none focus:ring-2 focus:ring-brand-primary/50`}
              placeholder="••••••••"
              autoComplete="current-password"
            />
            {getFieldError(errors, "password") && (
              <p className="mt-1 text-sm text-red-400">
                {getFieldError(errors, "password")}
              </p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-lg bg-brand-primary px-4 py-2 font-semibold text-white shadow-lg shadow-brand-primary/50 transition-all hover:bg-brand-secondary hover:shadow-brand-secondary/50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? "Signing in..." : "Sign In"}
          </button>

          {/* Sign Up Link */}
          <p className="mt-4 text-center text-sm text-zinc-400">
            Don't have an account?{" "}
            <Link
              href="/register"
              className="font-medium text-brand-primary hover:text-brand-secondary"
            >
              Sign up
            </Link>
          </p>
        </form>
      </div>

      {/* Error Toast */}
      {errorMessage && (
        <ErrorToast
          message={errorMessage}
          onClose={() => setErrorMessage(null)}
        />
      )}
    </div>
  );
}
