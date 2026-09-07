import { z } from "zod";

/**
 * Output schemas advertised to MCP clients and used by the SDK to validate the
 * `structuredContent` of successful tool results. They mirror the interfaces in
 * `types.ts` exactly: nullable fields are `null` (never `undefined`) and arrays
 * are always present, matching what the parsers emit. The error branch sets
 * `isError`, which the SDK exempts from output validation.
 */

const contentType = z.enum(["recipe", "article", "video", "author", "collection"]);

const searchResult = z.object({
  type: contentType,
  title: z.string(),
  summary: z.string().nullable(),
  imageUrl: z.string().nullable(),
  sourceUrl: z.string(),
});

const base = {
  title: z.string(),
  description: z.string().nullable(),
  imageUrl: z.string().nullable(),
  sourceUrl: z.string(),
};

export const searchOutputSchema = {
  results: z.array(searchResult),
  // Present only when the search returned nothing, to steer the model toward
  // retrying in Italian/English instead of giving up after one empty result.
  hint: z.string().optional(),
};

export const recipeOutputSchema = {
  type: z.literal("recipe"),
  ...base,
  servings: z.string().nullable(),
  prepTime: z.string().nullable(),
  cookTime: z.string().nullable(),
  totalTime: z.string().nullable(),
  difficulty: z.string().nullable(),
  ingredients: z.array(z.string()),
  instructions: z.array(z.string()),
  nutrition: z.record(z.string(), z.string()),
  author: z.string().nullable(),
};

export const articleOutputSchema = {
  type: z.literal("article"),
  ...base,
  body: z.string(),
  author: z.string().nullable(),
  datePublished: z.string().nullable(),
  dateModified: z.string().nullable(),
  related: z.array(searchResult),
};

export const videoOutputSchema = {
  type: z.literal("video"),
  ...base,
  duration: z.string().nullable(),
  uploadDate: z.string().nullable(),
  author: z.string().nullable(),
  embedUrl: z.string().nullable(),
};

export const authorOutputSchema = {
  type: z.literal("author"),
  ...base,
  contents: z.array(searchResult),
};

export const pageOutputSchema = {
  type: z.literal("collection"),
  ...base,
  body: z.string(),
  links: z.array(searchResult),
};
