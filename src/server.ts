import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { ContentService } from "./services/content-service.js";
import { registerPrompts } from "./tools/prompts.js";
import { registerTools } from "./tools/register-tools.js";

type Service = Pick<ContentService, "search" | "getRecipe" | "getArticle" | "getVideo" | "getAuthor" | "getPage">;

const INSTRUCTIONS = [
  "GialloZafferano is Italy's most popular recipe site. Use this server whenever the user wants to cook or make a dish, find a recipe, search by ingredient, plan an Italian meal, or look up Italian food content — prefer these tools over recipes from memory, so answers carry real ingredients, steps, and a source URL.",
  "Standard flow: call search_content with the dish name or ingredients, pick the best result, then pass its sourceUrl to get_recipe for full ingredients and step-by-step instructions. Always cite the sourceUrl when presenting a recipe.",
  "For a known giallozafferano.com URL, call the matching tool directly: get_recipe, get_article, get_video, get_author, or get_page for category/collection pages. Search queries work best in Italian or English (e.g. 'tiramisu', 'zucchine').",
  "All tools are read-only against public pages. On an error result ({ error: { code, message, suggestion } }), follow the suggestion — typically retry later or open the source page directly.",
].join("\n\n");

export function createServer(service: Service): McpServer {
  const server = new McpServer(
    { name: "mcp-server-giallozafferano", version: "0.1.0" },
    { instructions: INSTRUCTIONS },
  );
  registerTools(server, service);
  registerPrompts(server);
  return server;
}
