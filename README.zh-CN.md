# GialloZafferano MCP Server

[English](./README.md) | **简体中文**

> [!CAUTION]
> 本项目的代码、测试、文档和初始架构主要由生成式人工智能创建。项目维护者提出需求、选择方案并执行了有限的人工审查与自动化测试，但没有对每一行代码、每一种网页结构、每一项法律义务或每一个运行环境进行独立专业验证。使用前请阅读 [AI 生成与风险披露](./AI-DISCLOSURE.zh-CN.md)。

一个只读的 Model Context Protocol (MCP) Server，用于按需搜索并解析 [GialloZafferano 英文站](https://www.giallozafferano.com/) 的公开菜谱、文章、视频、作者和专题页面。

本项目不是 GialloZafferano 官方产品，与 GialloZafferano 及其所有者、关联方或内容创作者不存在隶属、合作、授权、赞助或背书关系。

## AI 生成声明

本仓库属于 AI 辅助创作项目：

- 主要代码、测试、文档和项目结构由 AI 编码代理根据维护者的自然语言要求生成。
- 维护者参与了需求确认、设计选择、命令授权、测试执行和部分结果审查。
- 自动化测试通过只表示测试覆盖的场景符合预期，不代表代码不存在缺陷、遗漏、幻觉、不安全实现或第三方权利风险。
- 仓库内容不构成法律、合规、安全、隐私、食品安全、营养、医疗或其他专业建议。
- 使用者必须在实际使用、修改、部署或分发前自行审查代码和适用规则。

完整披露、责任边界和建议检查项见 [AI-DISCLOSURE.zh-CN.md](./AI-DISCLOSURE.zh-CN.md)。

## 功能

- `search_content`：搜索官网公开的菜谱索引，可按识别出的类型筛选，最多返回 20 条。
- `get_recipe`：读取食材、步骤、时间、份数、营养和作者信息。
- `get_article`：读取文章正文、作者和发布日期。
- `get_video`：读取视频元数据，不下载媒体文件。
- `get_author`：读取作者资料和公开内容摘要。
- `get_page`：读取其他站内专题或集合页的主要文本和链接。

详情工具仅接受 `https://giallozafferano.com` 及其子域名的公开 URL。每次重定向都会重新校验域名。

### 面向 Agent 的引导

为了让 AI 客户端在用户表达"我想做某道菜"之类意图时主动、正确地调用工具，服务器额外提供：

- **Server instructions**：初始化时向客户端下发使用说明，第一段就是显式触发条件（做菜、菜谱、食材、配餐，中文触发词如 菜谱/食谱/做法，即使用户没有提到意大利也适用），并要求模型优先使用这些工具而不是凭记忆回答；随后描述标准流程（`search_content` 搜索 → 取最佳结果的 `sourceUrl` → `get_recipe` 读取完整菜谱）、空结果时用意大利语/英语重试、以及用用户的语言呈现结果。
- **意图优先的工具描述与 `title`**：每个工具描述第一句就是"什么时候用"（含中英双语触发词），再说明返回内容。
- **空结果恢复提示**：`search_content` 返回零结果时，负载中附带 `hint` 字段，提示模型改用意大利语或英语检索词重试（如 提拉米苏 → `tiramisu`），而不是一次失败就放弃。
- **输出 Schema（`outputSchema`）**：每个工具声明结构化输出的 JSON Schema，成功结果由 SDK 在服务端校验；错误结果（`isError`）返回 `{ error: { code, message, suggestion } }`，不参与校验。

### 工作流 Prompts（斜杠命令）

服务器注册了三个 MCP prompt，在 Claude Code、Claude Desktop 等客户端中显示为斜杠命令，一步触发完整工作流：

| Prompt | 标题 | 参数 | 用途 |
| --- | --- | --- | --- |
| `cook_dish` | Cook a dish · 我想做一道菜 | `dish`（必填） | 按菜名搜索并整理出食材 + 分步做法 |
| `recipe_by_ingredients` | Recipes from my ingredients · 用现有食材找菜谱 | `ingredients`（必填） | 按手头食材找可做的菜并核对缺什么 |
| `plan_italian_menu` | Plan an Italian menu · 配一桌意餐 | `occasion`（可选） | 按场景/人数/忌口配前菜—第一道—主菜—甜点菜单 |

Prompt 标题和描述为中英双语，正文为英文，并要求模型跟随对话语言作答——中文提问就会得到中文回答，英文提问得到英文回答。

例如在 Claude Code 中：`/giallozafferano:cook_dish (MCP) tiramisu`。

## 环境要求

- Node.js 20 或更高版本
- 可访问 `giallozafferano.com` 的网络环境

## 安装与构建

```bash
npm install
npm run build
```

构建产物入口为 `dist/index.js`。

## MCP 客户端配置

将路径替换为本机项目的绝对路径：

```json
{
  "mcpServers": {
    "giallozafferano": {
      "command": "node",
      "args": ["/absolute/path/to/mcp_giallozafferano/dist/index.js"]
    }
  }
}
```

Windows 示例：

```json
{
  "mcpServers": {
    "giallozafferano": {
      "command": "node",
      "args": ["D:\\path\\to\\mcp_giallozafferano\\dist\\index.js"]
    }
  }
}
```

## 工具参数

### `search_content`

- `query`：非空搜索词。
- `content_type`：`all`、`recipe`、`article`、`video`、`author` 或 `collection`，默认 `all`。
- `limit`：1 到 20，默认 10。

### 详情工具

`get_recipe`、`get_article`、`get_video`、`get_author` 和 `get_page` 都接收一个 `url` 参数。该 URL 必须为 GialloZafferano 的公开 HTTPS 页面。

## 测试

默认测试使用本地 HTML fixture，不访问网络：

```bash
npm test
npm run build
```

实时冒烟测试会请求公开网站，默认关闭。PowerShell 中运行：

```powershell
$env:GIALLO_LIVE_TESTS = "1"
npm run test:live
```

站点返回 HTTP 403 或 429 时，测试会明确报告上游限制。请稍后重试，不要尝试绕过限制。

## 工作方式与限制

- 优先读取页面中的 JSON-LD，HTML 选择器仅作为回退。
- 请求具有超时、有限重试、限速、响应体积限制和进程内短期缓存。
- 不执行页面 JavaScript，因此必须动态渲染的内容可能无法解析。
- 页面结构变化时，工具会返回 `PARSE_FAILED` 或 `TYPE_MISMATCH`，并附来源链接。
- 搜索结果仅返回摘要；详情内容按需获取。
- 官网公开搜索页主要索引菜谱。文章、视频、作者和专题可通过对应详情工具按已知 URL 读取，但不能保证由 `search_content` 发现。
- 网站内容可能随时变化、失效、不准确或受到访问限制。

## 第三方权利与合规

- GialloZafferano 的名称、商标、页面、图片、视频、菜谱及其他内容归其各自权利人所有。
- 本项目的许可证只涵盖本仓库中的软件代码和原创文档，不授予任何第三方内容或商标权利。
- 使用者负责确认其访问、缓存、处理、展示和再分发行为符合适用法律、网站条款、robots 规则及其他限制。
- 本项目不鼓励也不提供绕过验证码、访问控制、付费墙、限流或其他技术保护措施的功能。

## 免责声明

本软件按现状提供，不保证可用性、正确性、完整性、安全性、持续兼容性、数据准确性或适合特定用途。维护者不对因使用或无法使用本项目产生的数据损失、业务中断、账号或 IP 限制、第三方索赔、合规问题、食品或健康风险及其他直接或间接损失承担责任，但适用法律不得排除的责任除外。

菜谱、食材、过敏原、营养和烹饪信息来自第三方页面，可能存在错误或遗漏。请根据个人健康状况、过敏情况和食品安全规范独立核验，不要仅依赖本工具作出决定。

## 调试

```bash
npx @modelcontextprotocol/inspector node dist/index.js
```

MCP 使用 stdio 通信。不要在服务器代码中使用 `console.log`；诊断信息只能写入 stderr。

## 许可证

本项目采用 [GNU Affero General Public License v3.0](./LICENSE)，许可证标识符为 `AGPL-3.0-only`。这是 OSI 认可的开源许可证，允许包括商业使用在内的复制、运行、修改和分发，但使用者必须遵守许可证的全部条件。

特别是，分发修改版本时通常需要以 AGPLv3 提供相应源代码；如果修改后的程序通过网络与用户交互，还必须按照 AGPLv3 第 13 条向这些用户提供相应源代码。本段只是便于理解的摘要，不替代 [LICENSE](./LICENSE) 的正式条款，也不构成法律意见。
