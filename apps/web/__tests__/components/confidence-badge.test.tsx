/**
 * Tests for ConfidenceBadge component
 * Task: T215 [Phase 9]
 */

import { render, screen } from "@testing-library/react";
import ConfidenceBadge from "@/components/analysis/ConfidenceBadge";

describe("ConfidenceBadge", () => {
  describe("badge view (default)", () => {
    it("renders high confidence badge", () => {
      render(<ConfidenceBadge level="high" />);

      expect(screen.getByText("High Confidence")).toBeInTheDocument();
      expect(screen.getByText("✓✓✓")).toBeInTheDocument();
    });

    it("renders medium confidence badge", () => {
      render(<ConfidenceBadge level="medium" />);

      expect(screen.getByText("Medium Confidence")).toBeInTheDocument();
      expect(screen.getByText("✓✓")).toBeInTheDocument();
    });

    it("renders low confidence badge", () => {
      render(<ConfidenceBadge level="low" />);

      expect(screen.getByText("Low Confidence")).toBeInTheDocument();
      expect(screen.getByText("✓")).toBeInTheDocument();
    });

    it("renders none confidence badge", () => {
      render(<ConfidenceBadge level="none" />);

      expect(screen.getByText("No Confidence")).toBeInTheDocument();
      expect(screen.getByText("○")).toBeInTheDocument();
    });

    it("handles unknown level as none", () => {
      render(<ConfidenceBadge level="unknown" />);

      expect(screen.getByText("No Confidence")).toBeInTheDocument();
    });

    it("applies correct color classes for high", () => {
      const { container } = render(<ConfidenceBadge level="high" />);
      const badge = container.querySelector("span");

      expect(badge).toHaveClass("bg-green-100", "text-green-800");
    });

    it("applies correct color classes for medium", () => {
      const { container } = render(<ConfidenceBadge level="medium" />);
      const badge = container.querySelector("span");

      expect(badge).toHaveClass("bg-yellow-100", "text-yellow-800");
    });

    it("applies correct color classes for low", () => {
      const { container } = render(<ConfidenceBadge level="low" />);
      const badge = container.querySelector("span");

      expect(badge).toHaveClass("bg-orange-100", "text-orange-800");
    });

    it("shows description in title attribute", () => {
      const { container } = render(<ConfidenceBadge level="high" />);
      const badge = container.querySelector("span");

      expect(badge).toHaveAttribute(
        "title",
        "Strong evidence with multiple credible citations"
      );
    });
  });

  describe("description view", () => {
    it("shows full description for high confidence", () => {
      render(<ConfidenceBadge level="high" showDescription />);

      expect(screen.getByText("High Confidence")).toBeInTheDocument();
      expect(
        screen.getByText("Strong evidence with multiple credible citations")
      ).toBeInTheDocument();
    });

    it("shows full description for medium confidence", () => {
      render(<ConfidenceBadge level="medium" showDescription />);

      expect(
        screen.getByText("Moderate evidence with some citations")
      ).toBeInTheDocument();
    });

    it("shows full description for low confidence", () => {
      render(<ConfidenceBadge level="low" showDescription />);

      expect(
        screen.getByText("Limited evidence or missing citations")
      ).toBeInTheDocument();
    });

    it("shows full description for none confidence", () => {
      render(<ConfidenceBadge level="none" showDescription />);

      expect(
        screen.getByText("No evidence or response unavailable")
      ).toBeInTheDocument();
    });

    it("renders as card layout with description", () => {
      const { container } = render(<ConfidenceBadge level="high" showDescription />);

      expect(container.querySelector(".rounded-lg")).toBeInTheDocument();
      expect(container.querySelector(".border-2")).toBeInTheDocument();
    });
  });
});
