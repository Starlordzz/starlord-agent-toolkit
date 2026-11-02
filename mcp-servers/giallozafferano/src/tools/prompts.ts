import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

/**
 * Named workflow prompts. In hosts like Claude Code / Claude Desktop these show
 * up as slash commands, giving the user a one-step entry point that drives the
 * standard search_recipes → get_recipe flow. Titles and descriptions are
 * bilingual (English + Chinese) because they are user-facing UI strings; bodies
 * are English for the model and end with an instruction to answer in the
 * language of the conversation, so the same prompt serves users of any language.
 */

const RESPOND_IN_USER_LANGUAGE =
  "Answer in the language I have been using in this conversation. " +
  "Only use what the tools return — if nothing suitable is found, say so honestly instead of inventing a recipe.";

function userMessage(text: string) {
  return { messages: [{ role: "user" as const, content: { type: "text" as const, text } }] };
}

export function registerPrompts(server: McpServer): void {
  server.registerPrompt("cook_dish", {
    title: "Cook a dish · 我想做一道菜",
    description:
      "Search GialloZafferano for a dish and turn the best match into a complete recipe (ingredients + step-by-step instructions). " +
      "输入菜名，自动搜索并整理出完整菜谱（食材 + 分步做法）。",
    argsSchema: { dish: z.string().min(1).describe("Dish you want to cook, e.g. tiramisu, lasagne / 想做的菜名，如 提拉米苏") },
  }, ({ dish }) => userMessage(
    `I want to cook "${dish}". Please:\n` +
    `1. Use the search_recipes tool to search GialloZafferano for "${dish}" — if the name is not in Italian or English, translate it first (e.g. 提拉米苏 → tiramisu).\n` +
    `2. Pick the best match and call get_recipe with its sourceUrl.\n` +
    `3. Present the ingredient list, step-by-step instructions, prep/cook time, and servings, ending with the source URL.\n` +
    `If no good match exists, suggest close alternatives from the search results. ${RESPOND_IN_USER_LANGUAGE}`,
  ));

  server.registerPrompt("recipe_by_ingredients", {
    title: "Recipes from my ingredients · 用现有食材找菜谱",
    description:
      "Find GialloZafferano recipes you can make with the ingredients you already have, and see what is still missing. " +
      "输入手头食材，找出能做的菜并核对还缺什么。",
    argsSchema: { ingredients: z.string().min(1).describe("Ingredients you have, comma-separated, e.g. zucchine, uova, parmigiano / 现有食材，逗号分隔") },
  }, ({ ingredients }) => userMessage(
    `I have these ingredients: ${ingredients}. Please:\n` +
    `1. Use the search_recipes tool to find candidate GialloZafferano recipes for these ingredients, searched individually or combined — translate them into Italian or English first if needed.\n` +
    `2. Pick the 2-3 best fits and call get_recipe with each one's sourceUrl to check the full ingredient list.\n` +
    `3. Recommend which dishes to make first, list what I am still missing for each, and include each recipe's source URL.\n` +
    RESPOND_IN_USER_LANGUAGE,
  ));

  server.registerPrompt("plan_italian_menu", {
    title: "Plan an Italian menu · 配一桌意餐",
    description:
      "Plan a full Italian menu (antipasto / primo / secondo / dolce) for an occasion, with a real recipe behind every course. " +
      "按场景、人数或忌口配一桌前菜—第一道—主菜—甜点的意餐菜单。",
    argsSchema: { occasion: z.string().optional().describe("Occasion, headcount, or dietary needs, e.g. 'vegetarian dinner for 4' / 场景、人数或忌口，如「4 人素食晚餐」，可留空") },
  }, ({ occasion }) => {
    const requirement = occasion?.trim() || "no special requirements — everyday home cooking is fine";
    return userMessage(
      `Help me plan an Italian menu (antipasto / primo / secondo / dolce, 1-2 dishes per course). Requirements: ${requirement}. Please:\n` +
      `1. Use search_recipes to find candidates for each course (e.g. antipasti, primi, secondi, dolci, or specific dish names).\n` +
      `2. Call get_recipe with each chosen dish's sourceUrl to get its ingredients and steps.\n` +
      `3. Present the full menu with each dish's source URL, plus one combined shopping list.\n` +
      RESPOND_IN_USER_LANGUAGE,
    );
  });
}
