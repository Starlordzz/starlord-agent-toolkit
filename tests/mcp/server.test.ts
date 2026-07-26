import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ContentError } from "../../src/errors.js";
import { createServer } from "../../src/server.js";

const recipe = {
  type: "recipe" as const, title: "Tiramisu", description: null, imageUrl: null,
  sourceUrl: "https://www.giallozafferano.com/recipes/tiramisu.html", servings: null,
  prepTime: null, cookTime: null, totalTime: null, difficulty: null,
  ingredients: ["Coffee"], instructions: ["Layer it"], nutrition: {}, author: null,
};

function service() {
  return {
    search: vi.fn().mockResolvedValue([]),
    getRecipe: vi.fn().mockResolvedValue(recipe),
    getArticle: vi.fn(), getVideo: vi.fn(), getAuthor: vi.fn(), getPage: vi.fn(),
  };
}

const closers: Array<() => Promise<void>> = [];
afterEach(async () => { await Promise.all(closers.splice(0).map((close) => close())); });

async function connected(mockService = service()) {
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  const server = createServer(mockService);
  const client = new Client({ name: "test-client", version: "1.0.0" });
  await server.connect(serverTransport);
  await client.connect(clientTransport);
  closers.push(() => client.close(), () => server.close());
  return { client, mockService };
}

describe("MCP server", () => {
  it("lists the six public tools", async () => {
    const { client } = await connected();
    const result = await client.listTools();
    expect(result.tools.map((tool) => tool.name).sort()).toEqual([
      "get_article", "get_author", "get_page", "get_recipe", "get_video", "search_content",
    ]);
  });

  it("returns JSON and structured content", async () => {
    const { client } = await connected();
    const result = await client.callTool({ name: "get_recipe", arguments: { url: recipe.sourceUrl } });
    expect(result.isError).not.toBe(true);
    expect(result.structuredContent).toMatchObject({ title: "Tiramisu" });
  });

  it("maps domain errors to MCP errors", async () => {
    const mock = service();
    mock.getRecipe.mockRejectedValue(new ContentError("SECURITY_REJECTED", "Blocked URL", "Use a source URL."));
    const { client } = await connected(mock);
    const result = await client.callTool({ name: "get_recipe", arguments: { url: "https://example.com/x" } });
    expect(result.isError).toBe(true);
    expect((result.structuredContent as { error: { code: string } }).error.code).toBe("SECURITY_REJECTED");
  });
});
