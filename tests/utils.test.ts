import { describe, expect, it } from "vitest";
import { initialsFromName } from "@/lib/utils";

describe("initialsFromName", () => {
  it("returns initials for a two-part name", () => {
    expect(initialsFromName("Joy Auta")).toBe("JA");
  });

  it("ignores extra whitespace", () => {
    expect(initialsFromName("  Greenfield   College ")).toBe("GC");
  });
});
