import { readFile } from "node:fs/promises";
import { describe, expect, it, vi } from "vitest";
import { MemoryCache } from "../../src/client/memory-cache.js";
import { ContentService } from "../../src/services/content-service.js";

const recipeUrl = "https://www.giallozafferano.com/recipes/tiramisu.html";

describe("ContentService", () => {
  it("caches parsed recipe results", async () => {
    const html = await readFile(new URL("../fixtures/recipe.html", import.meta.url), "utf8");
    const http = { getHtml: vi.fn().mockResolvedValue(html) };
    const service = new ContentService(http, new MemoryCache(10, 1000));
    const first = await service.getRecipe(recipeUrl);
    const second = await service.getRecipe(recipeUrl);
    expect(first).toEqual(second);
    expect(first.sourceUrl).toBe(recipeUrl);
    expect(http.getHtml).toHaveBeenCalledTimes(1);
  });

  it("does not cache parser failures", async () => {
    const http = { getHtml: vi.fn().mockResolvedValue("<html><title>Not a recipe</title></html>") };
    const service = new ContentService(http, new MemoryCache(10, 1000));
    await expect(service.getRecipe(recipeUrl)).rejects.toMatchObject({ code: "TYPE_MISMATCH" });
    await expect(service.getRecipe(recipeUrl)).rejects.toMatchObject({ code: "TYPE_MISMATCH" });
    expect(http.getHtml).toHaveBeenCalledTimes(2);
  });

  it("searches and caches by query, type and limit", async () => {
    const html = await readFile(new URL("../fixtures/search.html", import.meta.url), "utf8");
    const http = { getHtml: vi.fn().mockResolvedValue(html) };
    const service = new ContentService(http, new MemoryCache(10, 1000));
    const results = await service.search("tiramisu", "recipe", 1);
    await service.search("tiramisu", "recipe", 1);
    expect(results).toHaveLength(1);
    expect(http.getHtml).toHaveBeenCalledTimes(1);
  });
});
