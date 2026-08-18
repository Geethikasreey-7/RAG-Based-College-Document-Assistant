import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import ChatInput from "../ChatInput";

describe("ChatInput", () => {
  it("sends the entered text on click", () => {
    const handleSend = vi.fn();
    render(<ChatInput onSend={handleSend} isLoading={false} disabled={false} />);

    fireEvent.change(screen.getByPlaceholderText(/Ask a question about your documents/i), {
      target: { value: "What is in the document?" },
    });
    fireEvent.click(screen.getByRole("button"));

    expect(handleSend).toHaveBeenCalledWith("What is in the document?");
  });

  it("sends on Enter key press", () => {
    const handleSend = vi.fn();
    render(<ChatInput onSend={handleSend} isLoading={false} disabled={false} />);

    const textarea = screen.getByPlaceholderText(/Ask a question about your documents/i);
    fireEvent.change(textarea, { target: { value: "hello" } });
    fireEvent.keyDown(textarea, { key: "Enter", code: "Enter" });

    expect(handleSend).toHaveBeenCalledWith("hello");
  });
});
