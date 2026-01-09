"use client";

/**
 * Accessibility utilities and components
 * Task: T205 [Phase 9]
 *
 * Provides:
 * - Screen reader only text
 * - Skip to content link
 * - Focus management utilities
 * - ARIA live region for announcements
 */

import React, { useEffect, useRef, createContext, useContext, useState, useCallback } from "react";

// Screen reader only text - visually hidden but accessible
export function ScreenReaderOnly({ children }: { children: React.ReactNode }) {
  return (
    <span className="sr-only">
      {children}
    </span>
  );
}

// Skip to main content link for keyboard navigation
export function SkipToContent({
  targetId = "main-content",
  children = "Skip to main content",
}: {
  targetId?: string;
  children?: React.ReactNode;
}) {
  return (
    <a
      href={`#${targetId}`}
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
    >
      {children}
    </a>
  );
}

// Focus trap for modals and dialogs
export function useFocusTrap(isActive: boolean) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    // Focus first element on mount
    firstElement?.focus();

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== "Tab") return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    container.addEventListener("keydown", handleKeyDown);
    return () => container.removeEventListener("keydown", handleKeyDown);
  }, [isActive]);

  return containerRef;
}

// Restore focus on unmount
export function useRestoreFocus() {
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    previousFocusRef.current = document.activeElement as HTMLElement;

    return () => {
      previousFocusRef.current?.focus();
    };
  }, []);
}

// ARIA live region context for announcements
interface AnnouncementContextType {
  announce: (message: string, priority?: "polite" | "assertive") => void;
}

const AnnouncementContext = createContext<AnnouncementContextType | null>(null);

export function AnnouncementProvider({ children }: { children: React.ReactNode }) {
  const [politeMessage, setPoliteMessage] = useState("");
  const [assertiveMessage, setAssertiveMessage] = useState("");

  const announce = useCallback((message: string, priority: "polite" | "assertive" = "polite") => {
    if (priority === "assertive") {
      setAssertiveMessage("");
      // Small delay to ensure the change is announced
      setTimeout(() => setAssertiveMessage(message), 100);
    } else {
      setPoliteMessage("");
      setTimeout(() => setPoliteMessage(message), 100);
    }
  }, []);

  return (
    <AnnouncementContext.Provider value={{ announce }}>
      {children}
      {/* Polite announcements */}
      <div
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {politeMessage}
      </div>
      {/* Assertive announcements for urgent updates */}
      <div
        aria-live="assertive"
        aria-atomic="true"
        className="sr-only"
      >
        {assertiveMessage}
      </div>
    </AnnouncementContext.Provider>
  );
}

export function useAnnouncement() {
  const context = useContext(AnnouncementContext);
  if (!context) {
    throw new Error("useAnnouncement must be used within AnnouncementProvider");
  }
  return context;
}

// Keyboard navigation helpers
export function useKeyboardNavigation<T extends HTMLElement>(
  items: T[],
  options: {
    orientation?: "horizontal" | "vertical" | "both";
    loop?: boolean;
    onSelect?: (index: number) => void;
  } = {}
) {
  const { orientation = "vertical", loop = true, onSelect } = options;
  const [activeIndex, setActiveIndex] = useState(0);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      const isVertical = orientation === "vertical" || orientation === "both";
      const isHorizontal = orientation === "horizontal" || orientation === "both";

      let newIndex = activeIndex;

      switch (e.key) {
        case "ArrowDown":
          if (isVertical) {
            e.preventDefault();
            newIndex = loop
              ? (activeIndex + 1) % items.length
              : Math.min(activeIndex + 1, items.length - 1);
          }
          break;
        case "ArrowUp":
          if (isVertical) {
            e.preventDefault();
            newIndex = loop
              ? (activeIndex - 1 + items.length) % items.length
              : Math.max(activeIndex - 1, 0);
          }
          break;
        case "ArrowRight":
          if (isHorizontal) {
            e.preventDefault();
            newIndex = loop
              ? (activeIndex + 1) % items.length
              : Math.min(activeIndex + 1, items.length - 1);
          }
          break;
        case "ArrowLeft":
          if (isHorizontal) {
            e.preventDefault();
            newIndex = loop
              ? (activeIndex - 1 + items.length) % items.length
              : Math.max(activeIndex - 1, 0);
          }
          break;
        case "Home":
          e.preventDefault();
          newIndex = 0;
          break;
        case "End":
          e.preventDefault();
          newIndex = items.length - 1;
          break;
        case "Enter":
        case " ":
          e.preventDefault();
          onSelect?.(activeIndex);
          return;
        default:
          return;
      }

      setActiveIndex(newIndex);
      items[newIndex]?.focus();
    },
    [activeIndex, items, loop, orientation, onSelect]
  );

  return {
    activeIndex,
    setActiveIndex,
    handleKeyDown,
    getItemProps: (index: number) => ({
      tabIndex: index === activeIndex ? 0 : -1,
      "aria-selected": index === activeIndex,
    }),
  };
}

// Accessible button that looks like a link
export function ButtonLink({
  children,
  onClick,
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`text-blue-600 hover:text-blue-800 underline focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

// Visually hidden label for inputs
export function HiddenLabel({
  htmlFor,
  children,
}: {
  htmlFor: string;
  children: React.ReactNode;
}) {
  return (
    <label htmlFor={htmlFor} className="sr-only">
      {children}
    </label>
  );
}

// Loading state with accessible announcement
export function LoadingState({
  message = "Loading...",
  className = "",
}: {
  message?: string;
  className?: string;
}) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={`flex items-center justify-center ${className}`}
    >
      <svg
        className="animate-spin h-5 w-5 mr-2 text-blue-600"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <span>{message}</span>
    </div>
  );
}

// Progress indicator with ARIA
export function ProgressIndicator({
  current,
  total,
  label,
  className = "",
}: {
  current: number;
  total: number;
  label: string;
  className?: string;
}) {
  const percentage = Math.round((current / total) * 100);

  return (
    <div className={className}>
      <div className="flex justify-between text-sm mb-1">
        <span id="progress-label">{label}</span>
        <span aria-hidden="true">{percentage}%</span>
      </div>
      <div
        role="progressbar"
        aria-valuenow={current}
        aria-valuemin={0}
        aria-valuemax={total}
        aria-labelledby="progress-label"
        className="h-2 bg-gray-200 rounded-full overflow-hidden"
      >
        <div
          className="h-full bg-blue-600 transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="sr-only">
        {current} of {total} complete
      </span>
    </div>
  );
}
