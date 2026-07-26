import { readFile } from "node:fs/promises";
import { describe, expect, it } from "vitest";
import { buildSearchUrl, parseSearchResults } from "../../src/parsers/search.js";

describe("search parsing", () => {
  it("builds an encoded site search URL", () => {
    const url = buildSearchUrl("pasta & beans");
    expect(url.hostname).toBe("www.giallozafferano.com");
    expect(url.pathname).toBe("/recipes-search/pasta+%26+beans/");
    expect(url.search).toBe("");
  });

  it("normalizes, filters and deduplicates results", async () => {
    const html = await readFile(new URL("../fixtures/search.html", import.meta.url), "utf8");
    const results = parseSearchResults(html, "https://www.giallozafferano.com/search?q=x", "recipe", 10);
    expect(results).toEqual([{
      type: "recipe",
      title: "Tiramisu",
      summary: "Coffee dessert",
      imageUrl: "https://www.giallozafferano.com/images/tiramisu.jpg",
      sourceUrl: "https://www.giallozafferano.com/recipes/Tiramisu.html",
    }]);
  });
});
