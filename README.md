# starlord-agent-toolkit

Agent 工具集单仓库：MCP Server 与 Skill 统一存放、统一提交历史。

## 目录

```
starlord-agent-toolkit/
├── mcp-servers/
│   ├── giallozafferano/          # 菜谱数据 MCP Server（TypeScript / Node 20+）
│   ├── redbook-search-comment/   # 小红书搜索与评论 MCP Server（Python）
│   └── uiautomator2/             # Android UI 自动化服务 + MCP Server + Python/Dart SDK
├── skills/
│   └── skill-travel-guide/       # 证据驱动的旅行攻略 Skill
├── README.md
└── .gitignore
```

## 组件

| 组件 | 栈 | 入口 | 常用命令 |
| --- | --- | --- | --- |
| `giallozafferano` | TypeScript / MCP SDK | `dist/index.js`，bin `mcp-server-giallozafferano` | `npm install`、`npm run build`、`npm test` |
| `redbook-search-comment` | Python / FastMCP | `xiaohongshu_mcp.py --stdio` | `pip install -r requirements.txt` |
| `uiautomator2` | Python / FastAPI + MCP | `mcp-server-android`，代码在 `mcp_server/` | `pip install -r requirements.txt` |
| `skill-travel-guide` | Markdown Skill | `SKILL.md` | 放入 `~/.claude/skills/skill-travel-guide/` 后按描述触发 |

各子项目保留自身的 `README.md`、`.gitignore` 与许可证，使用方式以子项目文档为准。

## 本地依赖

`node_modules/`、`dist/`、`.venv/`、`venv/`、`browser_data/`、`data/`、`playwright-browsers/` 不入库，克隆后按各子项目 README 安装。

## 历史

三个 MCP Server 与原 Skill 仓库通过 `git subtree --no-squash` 并入本仓库，原始提交流与作者信息保留。原远端仓库：

- `Starlordzz/mcp-giallozafferano`
- `chenningling/Redbook-Search-Comment-MCP2.0`（fork）
- `Starlordzz/multi_uiautomator2`（分支 `feat/mcp-server`）
- `Starlordzz/skill-travel-guide`
