import * as cheerio from "cheerio";
import { ContentError } from "../errors.js";

type JsonObject = Record<string, unknown>;

export function extractJsonLd(html: string): JsonObject[] {
  const $ = cheerio.load(html);
  const entities: JsonObject[] = [];
  let scripts = 0;
  $("script[type='application/ld+json']").each((_, element) => {
    scripts++;
    try {
      expand(JSON.parse($(element).text()), entities);
    } catch {
      // A page may contain an unrelated malformed analytics block.
    }
  });
  if (scripts > 0 && entities.length === 0) {
    throw new ContentError("PARSE_FAILED", "The page contains no valid JSON-LD.", "The site structure may have changed; open the source page directly.");
  }
  return entities;
}

export function findEntity(entities: JsonObject[], expectedTypes: readonly string[]): JsonObject | null {
  const expected = new Set(expectedTypes.map((type) => type.toLowerCase()));
  return entities.find((entity) => entityTypes(entity).some((type) => expected.has(type.toLowerCase()))) ?? null;
}

function expand(value: unknown, output: JsonObject[]): void {
  if (Array.isArray(value)) {
    value.forEach((item) => expand(item, output));
    return;
  }
  if (!isObject(value)) return;
  output.push(value);
  if ("@graph" in value) expand(value["@graph"], output);
}

function entityTypes(entity: JsonObject): string[] {
  const type = entity["@type"];
  if (typeof type === "string") return [type];
  return Array.isArray(type) ? type.filter((item): item is string => typeof item === "string") : [];
}

export function isObject(value: unknown): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
