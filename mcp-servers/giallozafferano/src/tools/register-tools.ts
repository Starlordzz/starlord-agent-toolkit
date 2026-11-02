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
const urlSchema = { url: z.string().url().describe("Public HTTPS URL on giallozafferano.com, e.g. a sourceUrl returned by search_recipes") };

export function registerTools(server: McpServer, service: Service): void {
  server.registerTool("search_recipes", {
    title: "Search GialloZafferano recipes",
    description:
      "Use for ANY recipe or cooking request — the user wants to cook, bake, find a recipe (菜谱/食谱/做法), use up ingredients, or get meal or dinner ideas. Searches GialloZafferano, Italy's most popular recipe site, by dish name, ingredient, or keyword; it is the entry point before get_recipe. Returns up to 20 result summaries, each with a sourceUrl; pass the best sourceUrl to get_recipe for full ingredients and steps. Upstream search mainly indexes recipes and works best with Italian or English terms (提拉米苏 → 'tiramisu'); for a known article, video, author, or collection URL, use the matching get_* tool instead.",
    inputSchema: {
      query: z.string().trim().min(1).describe("Search terms: a dish name, ingredient, or keyword (e.g. 'tiramisu', 'zucchine'). Translate non-Italian/English terms first"),
      content_type: z.enum(["all", "recipe", "article", "video", "author", "collection"]).default("all").describe("Optional content type filter"),
      limit: z.number().int().min(1).max(20).default(10).describe("Maximum number of results"),
    },
    outputSchema: searchOutputSchema,
    annotations,
  }, async ({ query, content_type, limit }) => wrap(async () => {
    const results = await service.search(query, content_type, limit);
    const payload: { results: typeof results; hint?: string } = { results };
    if (results.length === 0) {
      payload.hint =
        "No results for this query. Retry search_recipes with Italian or English terms (e.g. 提拉米苏 → 'tiramisu', 西葫芦 → 'zucchine') or a more generic keyword before concluding the dish does not exist on the site.";
    }
    return payload;
  }));

  server.registerTool("get_recipe", {
    title: "Get full recipe",
    description:
      "Get the complete recipe for one dish: ingredients, step-by-step instructions, prep/cook/total time, servings, difficulty, nutrition, and author. Use after search_recipes — or directly with a known giallozafferano.com recipe URL — whenever the user wants to cook a dish or see how it is made (怎么做/步骤). Input is the recipe page's sourceUrl.",
    inputSchema: urlSchema,
    outputSchema: recipeOutputSchema,
    annotations,
  }, async ({ url }) => wrap(() => service.getRecipe(url)));

  server.registerTool("get_article", {
    title: "Get article",
    description:
      "Read a public GialloZafferano article (cooking tips, roundups, food news): full body text, author, publish/update dates, and source URL. Use when the conversation cites a giallozafferano.com article URL, or when search results point to an article worth reading in full.",
    inputSchema: urlSchema,
    outputSchema: articleOutputSchema,
    annotations,
  }, async ({ url }) => wrap(() => service.getArticle(url)));

  server.registerTool("get_video", {
    title: "Get video info",
    description:
      "Read metadata for a GialloZafferano recipe video: description, duration, upload date, thumbnail, author, embed URL, and source URL. Does not download the video. Use with a known giallozafferano.com video URL, e.g. when the user wants to watch how a dish is made.",
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
