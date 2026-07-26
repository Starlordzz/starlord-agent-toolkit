import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { ContentService } from "./services/content-service.js";
import { registerTools } from "./tools/register-tools.js";

type Service = Pick<ContentService, "search" | "getRecipe" | "getArticle" | "getVideo" | "getAuthor" | "getPage">;

export function createServer(service: Service): McpServer {
  const server = new McpServer({ name: "mcp-server-giallozafferano", version: "0.1.0" });
  registerTools(server, service);
  return server;
}
