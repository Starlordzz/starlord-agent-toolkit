import { readFile } from "node:fs/promises";
import { describe, expect, it } from "vitest";
import { parseArticle, parseAuthor, parseRecipe, parseVideo } from "../../src/parsers/content.js";

const fixture = (name: string) => readFile(new URL(`../fixtures/${name}.html`, import.meta.url), "utf8");

describe("typed content parsers", () => {
  it("parses a recipe", async () => {
    const result = parseRecipe(await fixture("recipe"), "https://www.giallozafferano.com/recipes/tiramisu.html");
    expect(result).toMatchObject({ type: "recipe", title: "Classic Tiramisu", servings: "4 servings", author: "GZ Kitchen" });
    expect(result.ingredients).toEqual(["Mascarpone 500 g", "Coffee 300 ml"]);
    expect(result.instructions).toEqual(["Make the coffee.", "Layer the cream."]);
    expect(result.nutrition.calories).toBe("420 kcal");
  });

  it("parses an article", async () => {
    const result = parseArticle(await fixture("article"), "https://www.giallozafferano.com/article/pantry");
    expect(result).toMatchObject({ type: "article", title: "Italian Pantry Guide", body: "Olive oil and pasta are essential.", author: "Mario Rossi" });
  });

  it("parses a video", async () => {
    const result = parseVideo(await fixture("video"), "https://www.giallozafferano.com/video/gnocchi");
    expect(result).toMatchObject({ type: "video", title: "How to shape gnocchi", duration: "PT2M" });
  });

  it("parses an author", async () => {
    const result = parseAuthor(await fixture("author"), "https://www.giallozafferano.com/authors/mario");
    expect(result).toMatchObject({ type: "author", title: "Mario Rossi", description: "Food editor" });
    expect(result.contents).toEqual([]);
  });
});
