import * as cheerio from "cheerio";
import { ContentError } from "../errors.js";
import type { ArticleContent, AuthorContent, RecipeContent, VideoContent } from "../types.js";
import { extractJsonLd, findEntity, isObject } from "./json-ld.js";

type Entity = Record<string, unknown>;

export function parseRecipe(html: string, sourceUrl: string): RecipeContent {
  const entity = requiredEntity(html, ["Recipe"], "recipe");
  return {
    type: "recipe",
    title: requiredTitle(entity),
    description: stringValue(entity.description),
    imageUrl: imageValue(entity.image),
    sourceUrl,
    servings: stringValue(entity.recipeYield),
    prepTime: stringValue(entity.prepTime),
    cookTime: stringValue(entity.cookTime),
    totalTime: stringValue(entity.totalTime),
    difficulty: stringValue(entity.difficulty) ?? stringValue(entity.recipeCategory),
    ingredients: stringArray(entity.recipeIngredient),
    instructions: instructionTexts(entity.recipeInstructions),
    nutrition: stringRecord(entity.nutrition),
    author: personName(entity.author),
  };
}

export function parseArticle(html: string, sourceUrl: string): ArticleContent {
  const entity = requiredEntity(html, ["Article", "NewsArticle", "BlogPosting"], "article");
  const $ = cheerio.load(html);
  return {
    type: "article",
    title: requiredTitle(entity),
    description: stringValue(entity.description),
    imageUrl: imageValue(entity.image),
    sourceUrl,
    body: cleanText(stringValue(entity.articleBody) ?? $("article").text()),
    author: personName(entity.author),
    datePublished: stringValue(entity.datePublished),
    dateModified: stringValue(entity.dateModified),
    related: [],
  };
}

export function parseVideo(html: string, sourceUrl: string): VideoContent {
  const entity = requiredEntity(html, ["VideoObject"], "video");
  return {
    type: "video",
    title: requiredTitle(entity),
    description: stringValue(entity.description),
    imageUrl: imageValue(entity.thumbnailUrl) ?? imageValue(entity.image),
    sourceUrl,
    duration: stringValue(entity.duration),
    uploadDate: stringValue(entity.uploadDate),
    author: personName(entity.author),
    embedUrl: stringValue(entity.embedUrl),
  };
}

export function parseAuthor(html: string, sourceUrl: string): AuthorContent {
  const entity = requiredEntity(html, ["Person"], "author");
  return {
    type: "author",
    title: requiredTitle(entity),
    description: stringValue(entity.description),
    imageUrl: imageValue(entity.image),
    sourceUrl,
    contents: [],
  };
}

function requiredEntity(html: string, types: string[], label: string): Entity {
  const entity = findEntity(extractJsonLd(html), types);
  if (!entity) {
    throw new ContentError("TYPE_MISMATCH", `The page does not contain ${label} structured data.`, `Use a GialloZafferano ${label} page URL.`);
  }
  return entity;
}

function requiredTitle(entity: Entity): string {
  const title = stringValue(entity.name) ?? stringValue(entity.headline);
  if (!title) throw new ContentError("PARSE_FAILED", "The content has no title.", "Open the source page directly; its structure may have changed.");
  return title;
}

function stringValue(value: unknown): string | null {
  return typeof value === "string" && cleanText(value) ? cleanText(value) : null;
}

function stringArray(value: unknown): string[] {
  const values = Array.isArray(value) ? value : value === undefined ? [] : [value];
  return values.map(stringValue).filter((item): item is string => item !== null);
}

function imageValue(value: unknown): string | null {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return imageValue(value[0]);
  if (isObject(value)) return stringValue(value.url) ?? stringValue(value.contentUrl);
  return null;
}

function personName(value: unknown): string | null {
  if (typeof value === "string") return cleanText(value);
  if (Array.isArray(value)) return personName(value[0]);
  return isObject(value) ? stringValue(value.name) : null;
}

function instructionTexts(value: unknown): string[] {
  const items = Array.isArray(value) ? value : value === undefined ? [] : [value];
  const output: string[] = [];
  for (const item of items) {
    if (typeof item === "string") output.push(cleanText(item));
    else if (isObject(item)) {
      const text = stringValue(item.text) ?? stringValue(item.name);
      if (text) output.push(text);
      if (Array.isArray(item.itemListElement)) output.push(...instructionTexts(item.itemListElement));
    }
  }
  return output.filter(Boolean);
}

function stringRecord(value: unknown): Record<string, string> {
  if (!isObject(value)) return {};
  return Object.fromEntries(Object.entries(value).flatMap(([key, item]) => {
    const text = stringValue(item);
    return text ? [[key, text]] : [];
  }));
}

function cleanText(value: string): string {
  return value.replace(/\s+/g, " ").trim();
}
