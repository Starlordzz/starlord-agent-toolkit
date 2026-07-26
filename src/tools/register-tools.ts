import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { ContentError } from "../errors.js";
import type { ContentService } from "../services/content-service.js";
import {
  articleOutputSchema,
  authorOutputSchema,
  pageOutputSchema,
  recipeOutputSchema,
  searchOutputSchema,
  videoOutputSchema,
} from "./schemas.js";

type Service = Pick<ContentService, "search" | "getRecipe" | "getArticle" | "getVideo" | "getAuthor" | "getPage">;
const annotations = { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: true };
const urlSchema = { url: z.string().url().describe("Public HTTPS URL on giallozafferano.com, e.g. a sourceUrl returned by search_content") };

export function registerTools(server: McpServer, service: Service): void {
  server.registerTool("search_content", {
    title: "Search GialloZafferano",
    description:
      "Find Italian recipes on GialloZafferano by dish name, ingredient, or keyword. Use this FIRST whenever the user wants to cook, make, or find a dish, or browse by ingredient — it is the entry point before get_recipe. Returns up to 20 result summaries, each with a sourceUrl; pass the best sourceUrl to get_recipe for full ingredients and steps. Upstream search mainly indexes recipes; for a known article, video, author, or collection URL, use the matching get_* tool instead.",
    inputSchema: {
      query: z.string().trim().min(1).describe("Search terms: a dish name, ingredient, or keyword (e.g. 'tiramisu', 'zucchine')"),
      content_type: z.enum(["all", "recipe", "article", "video", "author", "collection"]).default("all").describe("Optional content type filter"),
      limit: z.number().int().min(1).max(20).default(10).describe("Maximum number of results"),
    },
    outputSchema: searchOutputSchema,
    annotations,
  }, async ({ query, content_type, limit }) => wrap(async () => ({ results: await service.search(query, content_type, limit) })));

  server.registerTool("get_recipe", {
    title: "Get recipe details",
    description:
      "Get the full recipe for one GialloZafferano dish: ingredients, step-by-step instructions, prep/cook/total time, servings, difficulty, nutrition, and author. Use this after search_content (or with a known recipe URL) whenever the user actually wants to cook or see how a dish is made. Input is the recipe page's sourceUrl.",
    inputSchema: urlSchema,
    outputSchema: recipeOutputSchema,
    annotations,
  }, async ({ url }) => wrap(() => service.getRecipe(url)));

  server.registerTool("get_article", {
    title: "Get article",
    description:
      "Read a public GialloZafferano article (cooking tips, roundups, food news): full body text, author, publish/update dates, and source URL. Use with a known giallozafferano.com article URL.",
    inputSchema: urlSchema,
    outputSchema: articleOutputSchema,
    annotations,
  }, async ({ url }) => wrap(() => service.getArticle(url)));

  server.registerTool("get_video", {
    title: "Get video info",
    description:
      "Read metadata for a GialloZafferano recipe video: description, duration, upload date, thumbnail, author, embed URL, and source URL. Does not download the video. Use with a known giallozafferano.com video URL.",
    inputSchema: urlSchema,
    outputSchema: videoOutputSchema,
    annotations,
  }, async ({ url }) => wrap(() => service.getVideo(url)));

  server.registerTool("get_author", {
    title: "Get author profile",
    description:
      "Read a public GialloZafferano author or cook profile: biography, image, and source URL. Use with a known giallozafferano.com author URL, e.g. to learn who created a recipe.",
    inputSchema: urlSchema,
    outputSchema: authorOutputSchema,
    annotations,
  }, async ({ url }) => wrap(() => service.getAuthor(url)));

  server.registerTool("get_page", {
    title: "Get page",
    description:
      "Read any other GialloZafferano page that is not a recipe, article, video, or author — e.g. a category, collection, or topic index. Returns clean main text plus in-page links (each with a sourceUrl you can follow) and the source URL. Use with a known giallozafferano.com URL when no more specific tool fits.",
    inputSchema: urlSchema,
    outputSchema: pageOutputSchema,
    annotations,
  }, async ({ url }) => wrap(() => service.getPage(url)));
}

async function wrap(operation: () => Promise<unknown>) {
  try {
    const data = await operation();
    const structuredContent = asRecord(data);
    return { content: [{ type: "text" as const, text: JSON.stringify(structuredContent, null, 2) }], structuredContent };
  } catch (cause) {
    const error = cause instanceof ContentError
      ? { code: cause.code, message: cause.message, suggestion: cause.suggestion }
      : { code: "UPSTREAM_UNAVAILABLE", message: "The request could not be completed.", suggestion: "Retry later or open the source page directly." };
    const structuredContent = { error };
    return { content: [{ type: "text" as const, text: JSON.stringify(structuredContent, null, 2) }], structuredContent, isError: true };
  }
}

function asRecord(value: unknown): Record<string, unknown> {
  if (typeof value === "object" && value !== null && !Array.isArray(value)) return value as Record<string, unknown>;
  return { result: value };
}
