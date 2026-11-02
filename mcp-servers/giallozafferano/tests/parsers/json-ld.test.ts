import { readFile } from "node:fs/promises";
import { describe, expect, it } from "vitest";
import { extractJsonLd, findEntity } from "../../src/parsers/json-ld.js";

describe("JSON-LD extraction", () => {
  it("expands arrays and @graph entities", () => {
    const html = `<script type="application/ld+json">[{"@type":"WebPage"},{"@graph":[{"@type":"Recipe","name":"A"}]}]</script>`;
    const entities = extractJsonLd(html);
    expect(entities).toHaveLength(3);
    expect(findEntity(entities, ["recipe"])).toMatchObject({ name: "A" });
  });

  it("extracts a recipe fixture", async () => {
    const html = await readFile(new URL("../fixtures/recipe.html", import.meta.url), "utf8");
    expect(findEntity(extractJsonLd(html), ["Recipe"])?.name).toBe("Classic Tiramisu");
  });
});
