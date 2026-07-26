import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { ContentError } from "../errors.js";
import type { ContentService } from "../services/content-service.js";

type Service = Pick<ContentService, "search" | "getRecipe" | "getArticle" | "getVideo" | "getAuthor" | "getPage">;
const annotations = { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: true };
const urlSchema = { url: z.string().url().describe("Public HTTPS URL on giallozafferano.com") };

export function registerTools(server: McpServer, service: Service): void {
  server.registerTool("search_content", {
    description: "Search the public GialloZafferano recipe index. Returns content summaries and source URLs, at most 20 results. The upstream search primarily exposes recipes; use typed get tools for known article, video, author, or collection URLs.",
    inputSchema: {
      query: z.string().trim().min(1).describe("Search terms"),
      content_type: z.enum(["all", "recipe", "article", "video", "author", "collection"]).default("all").describe("Optional content type filter"),
      limit: z.number().int().min(1).max(20).default(10).describe("Maximum number of results"),
    },
    annotations,
  }, async ({ query, content_type, limit }) => wrap(async () => ({ results: await service.search(query, content_type, limit) })));

  server.registerTool("get_recipe", {
    description: "Read a public GialloZafferano recipe. Returns ingredients, instructions, timing, servings, nutrition, author, and source URL when available.",
    inputSchema: urlSchema, annotations,
  }, async ({ url }) => wrap(() => service.getRecipe(url)));

  server.registerTool("get_article", {
    description: "Read a public GialloZafferano article. Returns body, author, dates, related items, and source URL.",
    inputSchema: urlSchema, annotations,
  }, async ({ url }) => wrap(() => service.getArticle(url)));

  server.registerTool("get_video", {
    description: "Read metadata for a public GialloZafferano video page. Returns description, duration, thumbnail, author, embed URL, and source URL; does not download video.",
    inputSchema: urlSchema, annotations,
  }, async ({ url }) => wrap(() => service.getVideo(url)));

  server.registerTool("get_author", {
    description: "Read a public GialloZafferano author profile. Returns biography, image, listed content, and source URL.",
    inputSchema: urlSchema, annotations,
  }, async ({ url }) => wrap(() => service.getAuthor(url)));

  server.registerTool("get_page", {
    description: "Read a public GialloZafferano collection or topic page that is not a recipe, article, video, or author. Returns clean main text, links, and source URL.",
    inputSchema: urlSchema, annotations,
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
