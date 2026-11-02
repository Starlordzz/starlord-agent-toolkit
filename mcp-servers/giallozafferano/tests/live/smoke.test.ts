import { describe, expect, it } from "vitest";
import { DEFAULT_CONFIG } from "../../src/config.js";
import { MemoryCache } from "../../src/client/memory-cache.js";
import { RateLimiter } from "../../src/client/rate-limiter.js";
import { RestrictedHttpClient } from "../../src/client/http-client.js";
import { ContentService } from "../../src/services/content-service.js";

const liveDescribe = process.env.GIALLO_LIVE_TESTS === "1" ? describe : describe.skip;

liveDescribe("GialloZafferano live smoke test", () => {
  it("searches public content and reads a recipe", async () => {
    const http = new RestrictedHttpClient(DEFAULT_CONFIG, fetch, new RateLimiter(DEFAULT_CONFIG.minRequestIntervalMs));
    const service = new ContentService(http, new MemoryCache(10, 60_000));
    const results = await service.search("tiramisu", "all", 10);
    expect(results.length).toBeGreaterThan(0);
    expect(results.every((item) => new URL(item.sourceUrl).hostname.endsWith("giallozafferano.com"))).toBe(true);
    const recipe = results.find((item) => item.type === "recipe");
    expect(recipe, "The search returned no result identified as a recipe").toBeDefined();
    const detail = await service.getRecipe(recipe!.sourceUrl);
    expect(detail.title).not.toBe("");
    expect(detail.ingredients.length).toBeGreaterThan(0);
  }, 30_000);
});
