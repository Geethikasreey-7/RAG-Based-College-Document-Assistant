import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SourceReferences from "../SourceReferences";

describe("SourceReferences", () => {
  it("renders source filename and page number", () => {
    render(
      <SourceReferences
        sources={[
          { filename: "machine_learning.pdf", page: 4 },
          { filename: "machine_learning.pdf", page: 7 },
        ]}
      />
    );

    expect(screen.getByText(/Sources/i)).not.toBeNull();
    expect(screen.getAllByText("machine_learning.pdf").length).toBe(2);
    expect(screen.getByText(/Page\s*4/i)).not.toBeNull();
  });
});
