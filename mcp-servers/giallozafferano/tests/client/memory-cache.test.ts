import { describe, expect, it } from "vitest";
import { MemoryCache } from "../../src/client/memory-cache.js";

describe("MemoryCache", () => {
  it("expires entries after the TTL", () => {
    let now = 0;
    const cache = new MemoryCache<string>(2, 100, () => now);
    cache.set("a", "one");
    now = 101;
    expect(cache.get("a")).toBeUndefined();
  });

  it("evicts the oldest entry when full", () => {
    const cache = new MemoryCache<string>(2, 1000, () => 0);
    cache.set("a", "one");
    cache.set("b", "two");
    cache.set("c", "three");
    expect(cache.get("a")).toBeUndefined();
    expect(cache.get("b")).toBe("two");
  });
});
