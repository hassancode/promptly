/**
 * Tests for ErrorToast and SuccessToast components
 * Task: T215 [Phase 9]
 */

import { render, screen, fireEvent, act } from "@testing-library/react";
import ErrorToast, { SuccessToast } from "@/components/ErrorToast";

describe("ErrorToast", () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it("renders with message", () => {
    const onClose = jest.fn();
    render(<ErrorToast message="Test error message" onClose={onClose} />);

    expect(screen.getByText("Test error message")).toBeInTheDocument();
  });

  it("calls onClose when close button clicked", () => {
    const onClose = jest.fn();
    render(<ErrorToast message="Test error" onClose={onClose} />);

    const closeButton = screen.getByRole("button", { name: "Close" });
    fireEvent.click(closeButton);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("auto-closes after default duration", () => {
    const onClose = jest.fn();
    render(<ErrorToast message="Test error" onClose={onClose} />);

    expect(onClose).not.toHaveBeenCalled();

    act(() => {
      jest.advanceTimersByTime(5000);
    });

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("auto-closes after custom duration", () => {
    const onClose = jest.fn();
    render(<ErrorToast message="Test error" onClose={onClose} duration={2000} />);

    act(() => {
      jest.advanceTimersByTime(1999);
    });
    expect(onClose).not.toHaveBeenCalled();

    act(() => {
      jest.advanceTimersByTime(1);
    });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("does not auto-close when duration is 0", () => {
    const onClose = jest.fn();
    render(<ErrorToast message="Test error" onClose={onClose} duration={0} />);

    act(() => {
      jest.advanceTimersByTime(10000);
    });

    expect(onClose).not.toHaveBeenCalled();
  });

  it("has error styling", () => {
    const onClose = jest.fn();
    const { container } = render(<ErrorToast message="Test error" onClose={onClose} />);

    expect(container.querySelector(".bg-red-900\\/90")).toBeInTheDocument();
  });
});

describe("SuccessToast", () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it("renders with message", () => {
    const onClose = jest.fn();
    render(<SuccessToast message="Success message" onClose={onClose} />);

    expect(screen.getByText("Success message")).toBeInTheDocument();
  });

  it("has success styling", () => {
    const onClose = jest.fn();
    const { container } = render(<SuccessToast message="Success" onClose={onClose} />);

    expect(container.querySelector(".bg-green-900\\/90")).toBeInTheDocument();
  });

  it("auto-closes after default duration", () => {
    const onClose = jest.fn();
    render(<SuccessToast message="Success" onClose={onClose} />);

    act(() => {
      jest.advanceTimersByTime(5000);
    });

    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
