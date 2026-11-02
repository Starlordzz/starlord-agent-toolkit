import { readFile } from "node:fs/promises";
import { describe, expect, it } from "vitest";
import { parsePage } from "../../src/parsers/page.js";

describe("parsePage", () => {
  it("keeps main content and removes page chrome", async () => {
    const html = await readFile(new URL("../fixtures/collection.html", import.meta.url), "utf8");
    const result = parsePage(html, "https://www.giallozafferano.com/collections/summer");
    expect(result.title).toBe("Summer Recipes");
    expect(result.description).toBe("Fresh seasonal ideas");
    expect(result.body).toContain("Cook with tomatoes and basil.");
    expect(result.body).not.toContain("Navigation noise");
    expect(result.links[0]?.sourceUrl).toBe("https://www.giallozafferano.com/recipes/Caprese.html");
  });
});
