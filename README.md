# GialloZafferano MCP Server

一个只读的 Model Context Protocol (MCP) Server，按需搜索并解析 [GialloZafferano 英文站](https://www.giallozafferano.com/) 的公开菜谱、文章、视频、作者和专题页面。

本项目不是 GialloZafferano 官方产品，不保存整站镜像，不下载视频，不登录账户，也不会绕过访问限制。工具输出始终保留原始来源 URL。

## 功能

- `search_content`：搜索官网公开的菜谱索引，可按识别出的类型筛选，最多返回 20 条。
- `get_recipe`：读取食材、步骤、时间、份数、营养和作者信息。
- `get_article`：读取文章正文、作者和发布日期。
- `get_video`：读取视频元数据，不下载媒体文件。
- `get_author`：读取作者资料和公开内容摘要。
- `get_page`：读取其他站内专题或集合页的主要文本和链接。

详情工具仅接受 `https://giallozafferano.com` 及其子域名的公开 URL。每次重定向都会重新校验域名。

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

## 调试

可使用 MCP Inspector 检查工具：

```bash
npx @modelcontextprotocol/inspector node dist/index.js
```

MCP 使用 stdio 通信。不要在服务器代码中使用 `console.log`；诊断信息只能写入 stderr。

## 许可证

项目代码使用 [MIT License](./LICENSE)。GialloZafferano 的名称、商标和网站内容归其各自权利人所有。
