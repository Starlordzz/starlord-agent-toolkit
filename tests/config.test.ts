import { describe, expect, it } from "vitest";
import { DEFAULT_CONFIG } from "../src/config.js";

describe("DEFAULT_CONFIG", () => {
  it("uses bounded network defaults", () => {
    expect(DEFAULT_CONFIG.requestTimeoutMs).toBe(10_000);
    expect(DEFAULT_CONFIG.maxResponseBytes).toBe(2_000_000);
    expect(DEFAULT_CONFIG.cacheMaxEntries).toBe(100);
    expect(DEFAULT_CONFIG.cacheTtlMs).toBe(300_000);
    expect(DEFAULT_CONFIG.minRequestIntervalMs).toBe(500);
  });
});
