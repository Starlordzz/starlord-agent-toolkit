import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

/**
 * Named workflow prompts. In hosts like Claude Code / Claude Desktop these show
 * up as slash commands, giving the user a one-step entry point (e.g. "我想做一道菜")
 * that drives the standard search_content → get_recipe flow. Titles and bodies are
 * Chinese and user-facing; the tools they invoke stay English and model-facing.
 */

function userMessage(text: string) {
  return { messages: [{ role: "user" as const, content: { type: "text" as const, text } }] };
}

export function registerPrompts(server: McpServer): void {
  server.registerPrompt("cook_dish", {
    title: "我想做一道菜",
    description: "输入菜名，自动在 GialloZafferano 上搜索并整理出一份完整菜谱（食材 + 分步做法）。",
    argsSchema: { dish: z.string().min(1).describe("想做的菜名，例如 tiramisu、lasagne、提拉米苏") },
  }, ({ dish }) => userMessage(
    `我想做「${dish}」。请按以下步骤操作：\n` +
    `1. 用 search_content 工具在 GialloZafferano 上搜索「${dish}」。\n` +
    `2. 从结果里挑最贴合的一条，对它的 sourceUrl 调用 get_recipe。\n` +
    `3. 用中文整理并输出：食材清单、分步骤做法、所需时间与份数，并在末尾附上来源链接。\n` +
    `如果没有搜到合适的结果，请如实说明并给出替代建议，不要编造菜谱。`,
  ));

  server.registerPrompt("recipe_by_ingredients", {
    title: "用现有食材找菜谱",
    description: "输入手头已有的食材，找出可以做的 GialloZafferano 菜谱。",
    argsSchema: { ingredients: z.string().min(1).describe("现有食材，用逗号分隔，例如 zucchine, uova, parmigiano") },
  }, ({ ingredients }) => userMessage(
    `我手头有这些食材：${ingredients}。请按以下步骤操作：\n` +
    `1. 用 search_content 工具在 GialloZafferano 上按这些食材（可分别或组合）搜索候选菜谱。\n` +
    `2. 挑 2-3 个最合适的，对每个的 sourceUrl 调用 get_recipe，核对实际所需食材。\n` +
    `3. 用中文推荐优先做哪几道、分别还缺什么食材，并附上每道菜的来源链接。\n` +
    `只依据工具返回的内容作答，不要编造菜谱。`,
  ));

  server.registerPrompt("plan_italian_menu", {
    title: "配一桌意餐",
    description: "根据场景、人数或忌口，配一份前菜—第一道—主菜—甜点的意大利菜单并给出菜谱。",
    argsSchema: { occasion: z.string().optional().describe("场景、人数或忌口，例如「4 人素食晚餐」「快手工作日午餐」，可留空") },
  }, ({ occasion }) => {
    const requirement = occasion?.trim() || "没有特别要求，家常即可";
    return userMessage(
      `帮我配一桌意大利菜单（antipasto 前菜 / primo 第一道 / secondo 主菜 / dolce 甜点，每类 1-2 道）。要求：${requirement}。请按以下步骤操作：\n` +
      `1. 用 search_content 逐类搜索候选菜（如 antipasti、primi、secondi、dolci 或具体菜名）。\n` +
      `2. 对每道入选的菜，用 get_recipe 拿到食材与做法。\n` +
      `3. 用中文输出完整菜单、每道菜的来源链接，以及一份合并后的采购清单。\n` +
      `只依据工具返回的内容作答，不要编造菜谱。`,
    );
  });
}
