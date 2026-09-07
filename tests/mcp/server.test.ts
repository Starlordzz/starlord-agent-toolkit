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
      "get_article", "get_author", "get_page", "get_recipe", "get_video", "search_recipes",
    ]);
  });

  it("exposes server instructions for host guidance", async () => {
    const { client } = await connected();
    const instructions = client.getInstructions();
    expect(instructions).toContain("search_recipes");
    expect(instructions).toContain("get_recipe");
  });

  it("advertises an output schema on every tool", async () => {
    const { client } = await connected();
    const result = await client.listTools();
    for (const tool of result.tools) {
      expect(tool.outputSchema, `${tool.name} should declare outputSchema`).toBeDefined();
    }
  });

  it("lists the workflow prompts", async () => {
    const { client } = await connected();
    const result = await client.listPrompts();
    expect(result.prompts.map((prompt) => prompt.name).sort()).toEqual([
      "cook_dish", "plan_italian_menu", "recipe_by_ingredients",
    ]);
  });

  it("renders cook_dish into a tool-driving user message", async () => {
    const { client } = await connected();
    const result = await client.getPrompt({ name: "cook_dish", arguments: { dish: "tiramisu" } });
    const [message] = result.messages;
    expect(message.role).toBe("user");
    const text = (message.content as { type: string; text: string }).text;
    expect(text).toContain("tiramisu");
    expect(text).toContain("search_recipes");
    expect(text).toContain("get_recipe");
  });

  it("renders plan_italian_menu without an occasion", async () => {
    const { client } = await connected();
    const result = await client.getPrompt({ name: "plan_italian_menu", arguments: {} });
    const text = (result.messages[0].content as { type: string; text: string }).text;
    expect(text).toContain("search_recipes");
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
