/**
 * Tests for loading skeleton components
 * Task: T215 [Phase 9]
 */

import { render, screen } from "@testing-library/react";
import {
  Skeleton,
  SkeletonText,
  SkeletonCard,
  SkeletonAnalysisItem,
  SkeletonAnalysisList,
  SkeletonProviderCard,
  SkeletonDashboard,
} from "@/components/loading-skeleton";

describe("Loading Skeleton Components", () => {
  describe("Skeleton", () => {
    it("renders with default classes", () => {
      render(<Skeleton data-testid="skeleton" />);
      const skeleton = screen.getByTestId("skeleton");
      expect(skeleton).toBeInTheDocument();
      expect(skeleton).toHaveClass("animate-pulse", "bg-gray-200", "rounded");
    });

    it("accepts custom className", () => {
      render(<Skeleton className="h-10 w-20" data-testid="skeleton" />);
      const skeleton = screen.getByTestId("skeleton");
      expect(skeleton).toHaveClass("h-10", "w-20");
    });
  });

  describe("SkeletonText", () => {
    it("renders single line by default", () => {
      const { container } = render(<SkeletonText />);
      const lines = container.querySelectorAll(".animate-pulse");
      expect(lines).toHaveLength(1);
    });

    it("renders multiple lines when specified", () => {
      const { container } = render(<SkeletonText lines={3} />);
      const lines = container.querySelectorAll(".animate-pulse");
      expect(lines).toHaveLength(3);
    });
  });

  describe("SkeletonCard", () => {
    it("renders card structure", () => {
      const { container } = render(<SkeletonCard />);
      expect(container.querySelector(".bg-white")).toBeInTheDocument();
      expect(container.querySelector(".rounded-lg")).toBeInTheDocument();
    });
  });

  describe("SkeletonAnalysisItem", () => {
    it("renders analysis item skeleton", () => {
      const { container } = render(<SkeletonAnalysisItem />);
      expect(container.querySelector(".bg-white")).toBeInTheDocument();
    });
  });

  describe("SkeletonAnalysisList", () => {
    it("renders default 3 items", () => {
      const { container } = render(<SkeletonAnalysisList />);
      const items = container.querySelectorAll(".bg-white");
      expect(items).toHaveLength(3);
    });

    it("renders specified number of items", () => {
      const { container } = render(<SkeletonAnalysisList count={5} />);
      const items = container.querySelectorAll(".bg-white");
      expect(items).toHaveLength(5);
    });
  });

  describe("SkeletonProviderCard", () => {
    it("renders provider card skeleton", () => {
      const { container } = render(<SkeletonProviderCard />);
      expect(container.querySelector(".rounded-lg")).toBeInTheDocument();
    });
  });

  describe("SkeletonDashboard", () => {
    it("renders full dashboard skeleton", () => {
      const { container } = render(<SkeletonDashboard />);
      // Should contain multiple skeleton elements
      const skeletons = container.querySelectorAll(".animate-pulse");
      expect(skeletons.length).toBeGreaterThan(5);
    });
  });
});
