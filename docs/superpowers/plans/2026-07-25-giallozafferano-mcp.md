# GialloZafferano MCP 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 构建一个通过 stdio 提供服务的 TypeScript MCP Server，实时搜索并解析 GialloZafferano 的菜谱、文章、视频、作者和专题公开页面。

**架构：** MCP 工具处理器只负责 Zod 参数校验与结果包装，内容服务组合站内搜索、类型化解析器和受限 HTTP 客户端。解析优先使用 JSON-LD，HTML 选择器仅补齐缺失字段；网络层统一处理域名白名单、重定向、超时、限速、缓存和响应体积限制。

**技术栈：** Node.js 20、TypeScript、`@modelcontextprotocol/sdk`、Zod、Cheerio、Vitest

---

## 文件结构

- `package.json`：脚本、运行时依赖、开发依赖和 CLI 入口。
- `tsconfig.json`：严格 TypeScript 与 NodeNext ESM 配置。
- `vitest.config.ts`：单元测试、集成测试和覆盖率配置。
- `src/index.ts`：stdio 入口和关闭信号处理。
- `src/server.ts`：创建 MCP Server 并注册 6 个工具。
- `src/config.ts`：集中定义请求限制、缓存和 User-Agent 默认值。
- `src/errors.ts`：稳定的领域错误代码和 MCP 错误格式化。
- `src/types.ts`：搜索项、菜谱、文章、视频、作者和通用页面类型。
- `src/client/url-policy.ts`：URL 规范化和允许域名判断。
- `src/client/http-client.ts`：受限 GET、逐跳重定向、超时和响应限制。
- `src/client/rate-limiter.ts`：串行时间窗限速器。
- `src/client/memory-cache.ts`：有界 TTL 内存缓存。
- `src/parsers/json-ld.ts`：提取、展开和选择 JSON-LD 实体。
- `src/parsers/content.ts`：类型化详情页解析器。
- `src/parsers/search.ts`：搜索结果解析器。
- `src/parsers/page.ts`：专题和未知页面的安全文本提取。
- `src/services/content-service.ts`：获取页面、缓存并调用对应解析器。
- `src/tools/register-tools.ts`：工具 Schema、描述、调用和 MCP 输出。
- `tests/fixtures/*.html`：最小化离线页面样本。
- `tests/**/*.test.ts`：单元与 MCP 集成测试。
- `tests/live/smoke.test.ts`：显式开启的实时只读冒烟测试。
- `README.md`：安装、配置、工具说明、限制和测试命令。
- `LICENSE`：MIT 许可证。

### 任务 1：建立可测试的 TypeScript 项目

**文件：**

- 创建：`package.json`
- 创建：`tsconfig.json`
- 创建：`vitest.config.ts`
- 创建：`src/config.ts`
- 创建：`src/types.ts`
- 创建：`tests/config.test.ts`

- [ ] **步骤 1：编写配置失败测试**

```typescript
// tests/config.test.ts
import { describe, expect, it } from "vitest";
import { DEFAULT_CONFIG } from "../src/config.js";

describe("DEFAULT_CONFIG", () => {
  it("uses bounded network defaults", () => {
    expect(DEFAULT_CONFIG.requestTimeoutMs).toBe(10_000);
    expect(DEFAULT_CONFIG.maxResponseBytes).toBe(2_000_000);
    expect(DEFAULT_CONFIG.cacheMaxEntries).toBe(100);
    expect(DEFAULT_CONFIG.cacheTtlMs).toBe(300_000);
    expect(DEFAULT_CONFIG.minRequestIntervalMs).toBe(500);
  });
});
```

- [ ] **步骤 2：创建项目元数据并验证测试失败**

`package.json` 使用 ESM，定义 `build`、`test`、`test:watch`、`test:live` 和 `start`。依赖固定为当前安装时解析出的兼容版本，不手写未来版本号：

```json
{
  "name": "mcp-server-giallozafferano",
  "version": "0.1.0",
  "description": "Read-only MCP server for public GialloZafferano content",
  "type": "module",
  "bin": { "mcp-server-giallozafferano": "dist/index.js" },
  "files": ["dist", "README.md", "LICENSE"],
  "scripts": {
    "build": "tsc -p tsconfig.json",
    "test": "vitest run --exclude tests/live/**",
    "test:watch": "vitest",
    "test:live": "GIALLO_LIVE_TESTS=1 vitest run tests/live",
    "start": "node dist/index.js"
  },
  "engines": { "node": ">=20" },
  "license": "MIT"
}
```

安装：`npm install @modelcontextprotocol/sdk zod cheerio && npm install -D typescript vitest @types/node`

运行：`npm test -- tests/config.test.ts`

预期：FAIL，提示无法解析 `../src/config.js`。

- [ ] **步骤 3：实现配置和公共类型**

```typescript
// src/config.ts
export interface AppConfig {
  requestTimeoutMs: number;
  maxResponseBytes: number;
  cacheMaxEntries: number;
  cacheTtlMs: number;
  minRequestIntervalMs: number;
  userAgent: string;
}

export const DEFAULT_CONFIG: Readonly<AppConfig> = {
  requestTimeoutMs: 10_000,
  maxResponseBytes: 2_000_000,
  cacheMaxEntries: 100,
  cacheTtlMs: 300_000,
  minRequestIntervalMs: 500,
  userAgent: "mcp-server-giallozafferano/0.1 (+read-only public content)",
};
```

在 `src/types.ts` 定义并导出 `ContentType`、`SearchResult`、`RecipeContent`、`ArticleContent`、`VideoContent`、`AuthorContent`、`PageContent`。每种详情类型必须包含 `type`、`title` 和 `sourceUrl`；缺失标量使用 `null`，集合使用空数组。

`tsconfig.json` 使用 `target: ES2022`、`module/moduleResolution: NodeNext`、`strict: true`、`outDir: dist`、`rootDir: .`、`noUncheckedIndexedAccess: true`。`vitest.config.ts` 将测试环境设为 `node`。

- [ ] **步骤 4：验证项目骨架**

运行：`npm test -- tests/config.test.ts && npm run build`

预期：测试 PASS；TypeScript 无错误并生成 `dist/src/config.js`。

- [ ] **步骤 5：Commit**

```bash
git add package.json package-lock.json tsconfig.json vitest.config.ts src/config.ts src/types.ts tests/config.test.ts
git commit -m "chore: scaffold TypeScript MCP project"
```

如果目录仍不是 Git 仓库，跳过 commit，不自动执行 `git init`。

### 任务 2：实现 URL 策略、缓存、限速与受限 HTTP 客户端

**文件：**

- 创建：`src/errors.ts`
- 创建：`src/client/url-policy.ts`
- 创建：`src/client/memory-cache.ts`
- 创建：`src/client/rate-limiter.ts`
- 创建：`src/client/http-client.ts`
- 创建：`tests/client/url-policy.test.ts`
- 创建：`tests/client/memory-cache.test.ts`
- 创建：`tests/client/http-client.test.ts`

- [ ] **步骤 1：编写 URL 与缓存失败测试**

测试必须断言：接受 `https://www.giallozafferano.com/...` 和根域名；拒绝 HTTP、用户凭据、`evilgiallozafferano.com`、外域和非网页协议；TTL 后缓存失效；超过容量时淘汰最旧项。

```typescript
expect(normalizeAllowedUrl("https://www.giallozafferano.com/recipes/Tiramisu.html").hostname)
  .toBe("www.giallozafferano.com");
expect(() => normalizeAllowedUrl("https://giallozafferano.com@evil.test/x"))
  .toThrowError(ContentError);
```

运行：`npm test -- tests/client/url-policy.test.ts tests/client/memory-cache.test.ts`

预期：FAIL，目标模块不存在。

- [ ] **步骤 2：实现领域错误、URL 策略和有界缓存**

`ContentError` 构造函数接收稳定代码：`INVALID_INPUT`、`SECURITY_REJECTED`、`NOT_FOUND`、`UPSTREAM_BLOCKED`、`UPSTREAM_UNAVAILABLE`、`TYPE_MISMATCH`、`PARSE_FAILED`。`normalizeAllowedUrl` 只允许 HTTPS、无用户名密码且主机为 `giallozafferano.com` 或以 `.giallozafferano.com` 结尾。

`MemoryCache<T>` 接收 `maxEntries`、`ttlMs` 和可注入的 `now()`；`get` 删除过期项，`set` 在满容量时删除 Map 中最旧键。

- [ ] **步骤 3：验证 URL 与缓存测试通过**

运行：`npm test -- tests/client/url-policy.test.ts tests/client/memory-cache.test.ts`

预期：全部 PASS。

- [ ] **步骤 4：编写 HTTP 客户端失败测试**

向 `RestrictedHttpClient` 注入 `fetchImpl`、`sleep` 和配置。覆盖：成功 HTML、404、403、429、500、AbortError、非 HTML、超大 Content-Length、流式响应越界，以及 302 重定向到外域时不得发起第二次请求。

```typescript
it("rejects an off-site redirect before following it", async () => {
  const fetchImpl = vi.fn().mockResolvedValue(
    new Response(null, { status: 302, headers: { location: "https://evil.test/x" } }),
  );
  const client = makeClient(fetchImpl);
  await expect(client.getHtml("https://www.giallozafferano.com/x"))
    .rejects.toMatchObject({ code: "SECURITY_REJECTED" });
  expect(fetchImpl).toHaveBeenCalledTimes(1);
});
```

运行：`npm test -- tests/client/http-client.test.ts`

预期：FAIL，`RestrictedHttpClient` 尚不存在。

- [ ] **步骤 5：实现限速器与 HTTP 客户端**

`RateLimiter.wait()` 串行化调用，并保证两次请求起始时间至少相隔 `minRequestIntervalMs`。`getHtml()` 使用 `redirect: "manual"`，最多处理 5 次重定向并逐跳调用 `normalizeAllowedUrl`；通过 `AbortSignal.timeout()` 超时；只接受 `text/html` 或 `application/xhtml+xml`；读取流时累计字节并在超过限制后取消 reader。

错误映射必须精确：404 → `NOT_FOUND`；403/429 → `UPSTREAM_BLOCKED`；5xx、超时和网络错误 → `UPSTREAM_UNAVAILABLE`；错误内容类型和超大响应 → `PARSE_FAILED`。最多重试 2 次 5xx 和网络错误；429 仅在 `Retry-After` 不超过 2 秒时重试 1 次。

- [ ] **步骤 6：验证完整客户端测试**

运行：`npm test -- tests/client`

预期：全部 PASS，无真实网络请求。

- [ ] **步骤 7：Commit**

```bash
git add src/errors.ts src/client tests/client
git commit -m "feat: add restricted HTTP client"
```

### 任务 3：实现 JSON-LD 与类型化内容解析器

**文件：**

- 创建：`src/parsers/json-ld.ts`
- 创建：`src/parsers/content.ts`
- 创建：`tests/fixtures/recipe.html`
- 创建：`tests/fixtures/article.html`
- 创建：`tests/fixtures/video.html`
- 创建：`tests/fixtures/author.html`
- 创建：`tests/parsers/json-ld.test.ts`
- 创建：`tests/parsers/content.test.ts`

- [ ] **步骤 1：建立最小 fixture 并编写失败测试**

每个 fixture 只包含一个页面标题、一个 `application/ld+json` 脚本和用于 HTML 回退的最小节点。测试 JSON-LD 的对象、数组和 `@graph` 展开，忽略无效 JSON 脚本但在全部无效时抛 `PARSE_FAILED`。

菜谱断言至少包括：标题、描述、图片、份数、ISO 8601 时间字符串、食材数组、步骤文本数组、营养信息、作者和传入的规范来源 URL。文章、视频和作者分别验证设计规格中列出的字段。

运行：`npm test -- tests/parsers/json-ld.test.ts tests/parsers/content.test.ts`

预期：FAIL，解析器模块不存在。

- [ ] **步骤 2：实现 JSON-LD 提取**

```typescript
export function extractJsonLd(html: string): Record<string, unknown>[];
export function findEntity(
  entities: Record<string, unknown>[],
  expectedTypes: readonly string[],
): Record<string, unknown> | null;
```

`extractJsonLd` 使用 Cheerio 读取脚本文本，展开顶层数组与 `@graph`，仅保留普通对象。`findEntity` 同时支持字符串和数组形式的 `@type`，比较时大小写不敏感。

- [ ] **步骤 3：实现类型化内容解析器**

```typescript
export function parseRecipe(html: string, sourceUrl: string): RecipeContent;
export function parseArticle(html: string, sourceUrl: string): ArticleContent;
export function parseVideo(html: string, sourceUrl: string): VideoContent;
export function parseAuthor(html: string, sourceUrl: string): AuthorContent;
```

实现共享的 `asString`、`asStringArray`、`imageUrl`、`personName`、`instructionText` 辅助函数。正文清理应折叠连续空白，不执行脚本，不解析嵌入 HTML。若找不到期望实体则抛 `TYPE_MISMATCH`；缺失非关键字段返回 `null` 或空数组。

- [ ] **步骤 4：验证解析器**

运行：`npm test -- tests/parsers`

预期：全部 PASS。

- [ ] **步骤 5：Commit**

```bash
git add src/parsers/json-ld.ts src/parsers/content.ts tests/fixtures tests/parsers
git commit -m "feat: parse typed GialloZafferano content"
```

### 任务 4：实现搜索与通用专题页解析

**文件：**

- 创建：`src/parsers/search.ts`
- 创建：`src/parsers/page.ts`
- 创建：`tests/fixtures/search.html`
- 创建：`tests/fixtures/collection.html`
- 创建：`tests/parsers/search.test.ts`
- 创建：`tests/parsers/page.test.ts`

- [ ] **步骤 1：编写失败测试**

搜索 fixture 包含重复链接、相对链接、图片、摘要和不同内容类型提示。测试必须验证 URL 规范化、按 URL 去重、类型归一化、稳定顺序和 limit。专题页测试验证移除 `script`、`style`、导航、页脚和 Cookie UI，仅保留标题、描述、主要文本和站内内容链接。

运行：`npm test -- tests/parsers/search.test.ts tests/parsers/page.test.ts`

预期：FAIL，模块不存在。

- [ ] **步骤 2：实现搜索解析器**

```typescript
export function buildSearchUrl(query: string): URL;
export function parseSearchResults(
  html: string,
  baseUrl: string,
  contentType: ContentType | "all",
  limit: number,
): SearchResult[];
```

`buildSearchUrl` 使用 `URL` 和 `URLSearchParams`，不得字符串拼接查询词。结果链接再次经过允许域名校验。无法可靠判断类型时使用 `collection`，不得仅凭标题猜测作者或视频。

- [ ] **步骤 3：实现通用页面解析器**

```typescript
export function parsePage(html: string, sourceUrl: string): PageContent;
```

正文从 `main`、`article` 或内容主体候选中选取；删除非内容节点后折叠空白，正文上限为 20,000 字符，链接上限为 50。若没有标题或有效正文，抛 `PARSE_FAILED`。

- [ ] **步骤 4：验证搜索和页面解析**

运行：`npm test -- tests/parsers/search.test.ts tests/parsers/page.test.ts`

预期：全部 PASS。

- [ ] **步骤 5：Commit**

```bash
git add src/parsers/search.ts src/parsers/page.ts tests/fixtures/search.html tests/fixtures/collection.html tests/parsers
git commit -m "feat: parse search and collection pages"
```

### 任务 5：实现内容服务与缓存数据流

**文件：**

- 创建：`src/services/content-service.ts`
- 创建：`tests/services/content-service.test.ts`

- [ ] **步骤 1：编写失败测试**

向服务注入只含 `getHtml(url)` 的客户端和缓存。断言：`search` 构建站内 URL 并应用过滤；重复详情调用只请求一次；各 getter 调用正确解析器；解析失败不进入缓存；所有返回对象保留规范来源 URL。

```typescript
const first = await service.getRecipe(recipeUrl);
const second = await service.getRecipe(recipeUrl);
expect(first).toEqual(second);
expect(http.getHtml).toHaveBeenCalledTimes(1);
```

运行：`npm test -- tests/services/content-service.test.ts`

预期：FAIL，服务模块不存在。

- [ ] **步骤 2：实现内容服务**

```typescript
export class ContentService {
  search(query: string, type: ContentType | "all", limit: number): Promise<SearchResult[]>;
  getRecipe(url: string): Promise<RecipeContent>;
  getArticle(url: string): Promise<ArticleContent>;
  getVideo(url: string): Promise<VideoContent>;
  getAuthor(url: string): Promise<AuthorContent>;
  getPage(url: string): Promise<PageContent>;
}
```

缓存键包含操作名与规范 URL；搜索键包含规范化查询词、类型和 limit。缓存解析后的对象，不缓存错误或原始 HTML。

- [ ] **步骤 3：验证服务测试**

运行：`npm test -- tests/services/content-service.test.ts`

预期：全部 PASS。

- [ ] **步骤 4：Commit**

```bash
git add src/services/content-service.ts tests/services/content-service.test.ts
git commit -m "feat: add cached content service"
```

### 任务 6：注册 MCP 工具并完成协议集成测试

**文件：**

- 创建：`src/tools/register-tools.ts`
- 创建：`src/server.ts`
- 创建：`src/index.ts`
- 创建：`tests/mcp/server.test.ts`

- [ ] **步骤 1：编写 MCP 集成失败测试**

使用 SDK 的内存 transport 连接 Client 与 Server。注入 mock `ContentService`，列出工具并断言名称恰好为 `search_content`、`get_recipe`、`get_article`、`get_video`、`get_author`、`get_page`。调用成功工具时解析返回 JSON；服务抛 `ContentError` 时断言 `isError: true` 和稳定错误代码；非法参数由 Schema 拒绝。

运行：`npm test -- tests/mcp/server.test.ts`

预期：FAIL，MCP Server 工厂不存在。

- [ ] **步骤 2：实现工具注册**

每个工具描述都写明用途、返回字段和限制。`search_content` 的 `content_type` 默认 `all`，`limit` 默认 10 且范围为 1 到 20。详情 URL 使用 `z.string().url()`，业务层继续执行域名校验。

统一成功输出：

```typescript
return {
  content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }],
  structuredContent: data,
};
```

统一错误输出包含 `{ error: { code, message, suggestion } }`，并设置 `isError: true`。未知异常映射为 `UPSTREAM_UNAVAILABLE`，不得返回堆栈。

- [ ] **步骤 3：实现 Server 工厂与 stdio 入口**

`createServer(service)` 创建并返回已注册工具但尚未 connect 的 `McpServer`。`src/index.ts` 组合默认配置、缓存、限速器、HTTP 客户端和服务，再连接 `StdioServerTransport`。只允许 `console.error` 写诊断信息；处理 SIGINT/SIGTERM 时调用 `server.close()`。

确保 `package.json` 的 `bin` 改为 `dist/src/index.js`，并在 `src/index.ts` 首行加入 `#!/usr/bin/env node`。

- [ ] **步骤 4：验证协议与构建**

运行：`npm test -- tests/mcp/server.test.ts && npm run build`

预期：6 个工具全部可列出并调用；TypeScript 构建成功。

- [ ] **步骤 5：运行完整离线测试**

运行：`npm test`

预期：所有测试 PASS，测试日志中没有真实网络请求。

- [ ] **步骤 6：Commit**

```bash
git add src/tools src/server.ts src/index.ts tests/mcp package.json
git commit -m "feat: expose GialloZafferano MCP tools"
```

### 任务 7：文档、实时冒烟测试与发布前验证

**文件：**

- 创建：`tests/live/smoke.test.ts`
- 创建：`README.md`
- 创建：`LICENSE`

- [ ] **步骤 1：编写显式开启的实时冒烟测试**

测试在 `GIALLO_LIVE_TESTS !== "1"` 时使用 `describe.skip`。开启时调用 `search("tiramisu", "all", 3)`，断言至少一个结果、所有 URL 属于允许域名；再读取第一个明确识别为 recipe 的结果，断言标题、来源 URL 和非空食材。若搜索结果没有 recipe，测试应给出明确失败原因，不静默跳过。

- [ ] **步骤 2：编写 README 和许可证**

README 必须包含：项目用途与只读边界、Node.js 20 要求、`npm install`/`npm run build`/`npm test`、6 个工具及参数、Codex/Claude Desktop 的 stdio 配置 JSON、实时测试命令、网络限制、来源归属和网站结构变化排障。

客户端配置使用绝对入口占位说明，而不是不可运行的路径：

```json
{
  "mcpServers": {
    "giallozafferano": {
      "command": "node",
      "args": ["/absolute/path/to/mcp_giallozafferano/dist/src/index.js"]
    }
  }
}
```

LICENSE 使用标准 MIT 文本，年份为 2026，不声称获得 GialloZafferano 商标或内容授权。

- [ ] **步骤 3：运行离线质量门禁**

运行：`npm test && npm run build`

预期：全部测试 PASS，构建退出码为 0。

- [ ] **步骤 4：检查 CLI 启动与 MCP 握手**

运行：`npx @modelcontextprotocol/inspector node dist/src/index.js`

预期：Inspector 能连接，显示 6 个工具；手动调用非法外域 URL 返回 `SECURITY_REJECTED`。Inspector 是长驻进程，验证后正常终止。

- [ ] **步骤 5：在网络可用且站点允许时运行实时测试**

PowerShell：`$env:GIALLO_LIVE_TESTS='1'; npm run test:live`

预期：搜索和一个菜谱详情 PASS。若站点返回 403/429，记录为上游限制，不修改代码绕过限制；离线测试仍须保持通过。

- [ ] **步骤 6：最终检查 stdio 与工作区差异**

运行：`npm test && npm run build && git status --short`

预期：测试和构建通过；只显示本计划涉及的文件。若仍非 Git 仓库，改用文件清单核对，不自动初始化仓库。

- [ ] **步骤 7：Commit**

```bash
git add README.md LICENSE tests/live/smoke.test.ts
git commit -m "docs: add setup and live verification guide"
```

## 规格覆盖自检

- 6 个 MCP 工具：任务 4 至任务 6。
- JSON-LD 优先及 HTML 回退：任务 3 和任务 4。
- 域名、重定向、SSRF、超时、限速、体积限制：任务 2。
- 进程内短期缓存：任务 2 和任务 5。
- 稳定错误分类与 `isError: true`：任务 2 和任务 6。
- 离线 fixture、协议集成测试和可选实时测试：任务 3、任务 4、任务 6 和任务 7。
- stdio 分发、README 和客户端配置：任务 6 和任务 7。

计划中的类型名、方法签名和工具名与设计规格一致；未包含登录、持久化镜像、视频下载、脚本执行或任意域名抓取。
