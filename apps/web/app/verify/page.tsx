"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { verifyEmail } from "@/lib/auth-api";
import { APIError } from "@/lib/api-client";

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState<string>("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setErrorMessage("Verification token is missing");
      return;
    }

    const verify = async () => {
      try {
        await verifyEmail({ token });
        setStatus("success");

        // Redirect to login after 3 seconds
        setTimeout(() => {
          router.push("/login");
        }, 3000);
      } catch (error) {
        setStatus("error");
        if (error instanceof APIError) {
          setErrorMessage(error.message);
        } else {
          setErrorMessage("Failed to verify email. Please try again.");
        }
      }
    };

    verify();
  }, [token, router]);

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-4">
      <div className="w-full max-w-md text-center">
        {status === "loading" && (
          <div>
            {/* Loading Spinner */}
            <div className="mx-auto mb-6 h-16 w-16 animate-spin rounded-full border-4 border-zinc-700 border-t-brand-primary"></div>
            <h1 className="text-2xl font-bold text-white">
              Verifying Your Email
            </h1>
            <p className="mt-2 text-zinc-400">Please wait...</p>
          </div>
        )}

        {status === "success" && (
          <div className="rounded-lg border border-green-800 bg-green-900/30 p-8">
            {/* Success Icon */}
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-900/50">
              <svg
                className="h-8 w-8 text-green-400"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M5 13l4 4L19 7" />
              </svg>
            </div>

            <h1 className="text-2xl font-bold text-white">
              Email Verified Successfully!
            </h1>
            <p className="mt-2 text-zinc-400">
              Your email has been verified. You can now sign in to your account.
            </p>

            <p className="mt-4 text-sm text-zinc-500">
              Redirecting to login...
            </p>

            <Link
              href="/login"
              className="mt-6 inline-block rounded-lg bg-brand-primary px-6 py-2 font-semibold text-white transition-colors hover:bg-brand-secondary"
            >
              Go to Login
            </Link>
          </div>
        )}

        {status === "error" && (
          <div className="rounded-lg border border-red-800 bg-red-900/30 p-8">
            {/* Error Icon */}
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-900/50">
              <svg
                className="h-8 w-8 text-red-400"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>

            <h1 className="text-2xl font-bold text-white">
              Verification Failed
            </h1>
            <p className="mt-2 text-zinc-400">{errorMessage}</p>

            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-center">
              <Link
                href="/login"
                className="rounded-lg border border-zinc-700 bg-zinc-800 px-6 py-2 font-semibold text-white transition-colors hover:bg-zinc-700"
              >
                Go to Login
              </Link>
              <Link
                href="/register"
                className="rounded-lg bg-brand-primary px-6 py-2 font-semibold text-white transition-colors hover:bg-brand-secondary"
              >
                Sign Up Again
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
