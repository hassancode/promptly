/**
 * Tests for empty state components
 * Task: T215 [Phase 9]
 */

import { render, screen, fireEvent } from "@testing-library/react";
import {
  EmptyState,
  EmptyAnalyses,
  EmptyResults,
  EmptyProviderResponses,
  EmptyInsights,
  EmptyRecommendations,
  EmptyCompetitors,
  EmptyCitations,
  ErrorState,
  ProviderOffline,
  AnalysisPending,
} from "@/components/empty-state";

describe("EmptyState", () => {
  it("renders title and description", () => {
    render(
      <EmptyState
        title="Test Title"
        description="Test description text"
      />
    );

    expect(screen.getByText("Test Title")).toBeInTheDocument();
    expect(screen.getByText("Test description text")).toBeInTheDocument();
  });

  it("renders icon when provided", () => {
    render(
      <EmptyState
        title="Title"
        description="Description"
        icon={<svg data-testid="custom-icon" />}
      />
    );

    expect(screen.getByTestId("custom-icon")).toBeInTheDocument();
  });

  it("renders link action", () => {
    render(
      <EmptyState
        title="Title"
        description="Description"
        action={{ label: "Click me", href: "/test" }}
      />
    );

    const link = screen.getByRole("link", { name: "Click me" });
    expect(link).toHaveAttribute("href", "/test");
  });

  it("renders button action", () => {
    const onClick = jest.fn();
    render(
      <EmptyState
        title="Title"
        description="Description"
        action={{ label: "Click me", onClick }}
      />
    );

    const button = screen.getByRole("button", { name: "Click me" });
    fireEvent.click(button);
    expect(onClick).toHaveBeenCalled();
  });

  it("applies custom className", () => {
    const { container } = render(
      <EmptyState
        title="Title"
        description="Description"
        className="custom-class"
      />
    );

    expect(container.firstChild).toHaveClass("custom-class");
  });
});

describe("EmptyAnalyses", () => {
  it("renders no analyses message", () => {
    render(<EmptyAnalyses />);

    expect(screen.getByText("No analyses yet")).toBeInTheDocument();
    expect(screen.getByText(/Start your first AI visibility analysis/)).toBeInTheDocument();
  });

  it("calls onStartAnalysis when button clicked", () => {
    const onStartAnalysis = jest.fn();
    render(<EmptyAnalyses onStartAnalysis={onStartAnalysis} />);

    const button = screen.getByRole("button", { name: "Start Analysis" });
    fireEvent.click(button);
    expect(onStartAnalysis).toHaveBeenCalled();
  });

  it("renders link when no callback provided", () => {
    render(<EmptyAnalyses />);

    const link = screen.getByRole("link", { name: "Start Analysis" });
    expect(link).toHaveAttribute("href", "/analysis/new");
  });
});

describe("EmptyResults", () => {
  it("renders no results message without search term", () => {
    render(<EmptyResults />);

    expect(screen.getByText("No results found")).toBeInTheDocument();
    expect(screen.getByText(/No results match your current filters/)).toBeInTheDocument();
  });

  it("renders search term in message", () => {
    render(<EmptyResults searchTerm="test query" />);

    expect(screen.getByText(/No results match "test query"/)).toBeInTheDocument();
  });

  it("calls onClear when button clicked", () => {
    const onClear = jest.fn();
    render(<EmptyResults onClear={onClear} />);

    const button = screen.getByRole("button", { name: "Clear filters" });
    fireEvent.click(button);
    expect(onClear).toHaveBeenCalled();
  });
});

describe("EmptyProviderResponses", () => {
  it("renders no responses message", () => {
    render(<EmptyProviderResponses />);

    expect(screen.getByText("No responses yet")).toBeInTheDocument();
    expect(screen.getByText(/AI provider responses will appear here/)).toBeInTheDocument();
  });
});

describe("EmptyInsights", () => {
  it("renders no insights message", () => {
    render(<EmptyInsights />);

    expect(screen.getByText("No insights generated")).toBeInTheDocument();
  });

  it("calls onGenerate when provided", () => {
    const onGenerate = jest.fn();
    render(<EmptyInsights onGenerate={onGenerate} />);

    const button = screen.getByRole("button", { name: "Generate Insights" });
    fireEvent.click(button);
    expect(onGenerate).toHaveBeenCalled();
  });
});

describe("EmptyRecommendations", () => {
  it("renders no recommendations message", () => {
    render(<EmptyRecommendations />);

    expect(screen.getByText("No recommendations yet")).toBeInTheDocument();
  });
});

describe("EmptyCompetitors", () => {
  it("renders no competitors message", () => {
    render(<EmptyCompetitors />);

    expect(screen.getByText("No competitors added")).toBeInTheDocument();
  });

  it("calls onAdd when provided", () => {
    const onAdd = jest.fn();
    render(<EmptyCompetitors onAdd={onAdd} />);

    const button = screen.getByRole("button", { name: "Add Competitor" });
    fireEvent.click(button);
    expect(onAdd).toHaveBeenCalled();
  });
});

describe("EmptyCitations", () => {
  it("renders no citations message", () => {
    render(<EmptyCitations />);

    expect(screen.getByText("No citations found")).toBeInTheDocument();
  });
});

describe("ErrorState", () => {
  it("renders default error message", () => {
    render(<ErrorState />);

    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });

  it("renders custom error message", () => {
    render(<ErrorState title="Custom Error" description="Custom description" />);

    expect(screen.getByText("Custom Error")).toBeInTheDocument();
    expect(screen.getByText("Custom description")).toBeInTheDocument();
  });

  it("calls onRetry when provided", () => {
    const onRetry = jest.fn();
    render(<ErrorState onRetry={onRetry} />);

    const button = screen.getByRole("button", { name: "Try again" });
    fireEvent.click(button);
    expect(onRetry).toHaveBeenCalled();
  });
});

describe("ProviderOffline", () => {
  it("renders provider offline message", () => {
    render(<ProviderOffline providerName="OpenAI" />);

    expect(screen.getByText("OpenAI is unavailable")).toBeInTheDocument();
    expect(screen.getByText(/currently offline or not responding/)).toBeInTheDocument();
  });

  it("calls onRetry when provided", () => {
    const onRetry = jest.fn();
    render(<ProviderOffline providerName="OpenAI" onRetry={onRetry} />);

    const button = screen.getByRole("button", { name: "Retry" });
    fireEvent.click(button);
    expect(onRetry).toHaveBeenCalled();
  });
});

describe("AnalysisPending", () => {
  it("renders analysis pending state", () => {
    render(<AnalysisPending />);

    expect(screen.getByText("Analysis in progress")).toBeInTheDocument();
    expect(screen.getByText(/analysis is being processed/)).toBeInTheDocument();
  });
});
