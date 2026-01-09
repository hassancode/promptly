"use client";

import { useEffect } from "react";

export interface ErrorToastProps {
  message: string;
  onClose: () => void;
  duration?: number;
}

export default function ErrorToast({
  message,
  onClose,
  duration = 5000,
}: ErrorToastProps) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  return (
    <div className="fixed bottom-4 right-4 z-50 animate-slide-up">
      <div className="flex items-center gap-3 rounded-lg border border-red-800 bg-red-900/90 px-4 py-3 text-white shadow-lg backdrop-blur-sm">
        {/* Error Icon */}
        <svg
          className="h-5 w-5 flex-shrink-0 text-red-400"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>

        {/* Message */}
        <p className="text-sm font-medium">{message}</p>

        {/* Close Button */}
        <button
          onClick={onClose}
          className="ml-2 flex-shrink-0 text-red-400 transition-colors hover:text-red-300"
          aria-label="Close"
        >
          <svg
            className="h-4 w-4"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}

/**
 * Success Toast variant
 */
export function SuccessToast({
  message,
  onClose,
  duration = 5000,
}: ErrorToastProps) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  return (
    <div className="fixed bottom-4 right-4 z-50 animate-slide-up">
      <div className="flex items-center gap-3 rounded-lg border border-green-800 bg-green-900/90 px-4 py-3 text-white shadow-lg backdrop-blur-sm">
        {/* Success Icon */}
        <svg
          className="h-5 w-5 flex-shrink-0 text-green-400"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>

        {/* Message */}
        <p className="text-sm font-medium">{message}</p>

        {/* Close Button */}
        <button
          onClick={onClose}
          className="ml-2 flex-shrink-0 text-green-400 transition-colors hover:text-green-300"
          aria-label="Close"
        >
          <svg
            className="h-4 w-4"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}
