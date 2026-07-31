# skill-travel-guide

一个证据驱动的旅行攻略 Skill：用当前事实、路线几何、旅行者约束和显式优先级构建可执行行程；本地美食推荐必须有独立证据支撑；可选生成移动端攻略网站。

本 Skill 遵循开放的 **Agent Skills** 规范（SKILL.md + references/），可在支持该规范的多数 agent 平台安装使用。

## ⚠️ 状态说明：实验性，未经充分测试

本 Skill **尚未经过多轮实测验证**，目前处于早期实验阶段：

- 未在多个平台、多种行程类型（城市游 / 景区 / 多日跨城 / 自驾等）上反复验证过效果；
- 提示词中的证据规则、MCP 降级路径、Plan B 逻辑均未经长期回归测试，可能存在遗漏或失效；
- 输出结果**不构成任何出行建议**。营业时间、票务与预约政策、交通班次、餐厅状态、天气等动态信息，务必在出发前自行通过官方渠道核实；
- 欢迎提 issue 反馈实际使用中的问题。

使用前请自行判断风险，作者不对依据本 Skill 输出所做的出行决策承担责任。

## 目录结构

```
skill-travel-guide/
├── SKILL.md                      # 入口：触发条件与核心流程
├── README.md                     # 本文件（安装说明，agent 不读取）
├── LICENSE                       # AGPL-3.0
├── agents/openai.yaml            # OpenAI 风格 manifest 的平台读取；其他平台忽略
└── references/
    ├── research-method.md        # 信源分级、MCP 使用与降级、时效标签
    ├── food-evidence.md          # 美食证据规则与双轨推荐
    ├── itinerary-output.md       # 输出格式与不确定性措辞
    ├── example-day.md            # 填好的一日示例
    └── optional-website.md       # 仅在用户明确要网站时读取
```

## 安装

**要求**：安装到目标平台时，目标文件夹名必须为 `skill-travel-guide`（与 SKILL.md 的 `name` 一致，本地开发目录名不限）；内部相对路径不可改动。

### Claude Code

将整个文件夹复制到 skills 目录：

- 个人级：`~/.claude/skills/skill-travel-guide/`
- 项目级：`<项目>/.claude/skills/skill-travel-guide/`

之后在对话中描述旅行规划需求即可自动触发，或显式输入 `/skill-travel-guide`。

### Codex CLI / 其他支持 Agent Skills 规范的平台

复制到该平台的 skills 目录（如 Codex 的 `~/.codex/skills/`），平台会读取 SKILL.md 的 frontmatter 完成注册。读取 OpenAI 风格 manifest 的平台会使用 `agents/openai.yaml` 中的展示信息。

### 不支持 Skills 的平台（通用降级方案）

任何能读文件的 agent 都可以手动挂载：

1. 把本文件夹放进项目内（如 `docs/skills/skill-travel-guide/`）。
2. 在该平台的常驻指令文件（`AGENTS.md`、`CLAUDE.md`、`.cursorrules`、system prompt 等）中加入一行：

   > 处理旅行规划类请求时，先阅读 `docs/skills/skill-travel-guide/SKILL.md` 并遵循其中流程与引用文件。

## 可选依赖（中国大陆行程）

强烈建议安装 **高德地图 MCP** 与 **小红书 MCP**（安装方式随平台不同，见 `references/research-method.md` 的 Preferred MCP Gate）。缺失时 Skill 会提示安装并降级到公开信源，不会伪造调用结果。

## 平台兼容注意事项

- SKILL.md 指令为平台中立措辞；涉及平台差异处（MCP 安装、网站部署脚本形态）已写为"按用户实际平台调整"。
- `agents/openai.yaml` 与 SKILL.md 的描述文案需人工保持同步。

## 许可证

本项目采用 **GNU Affero General Public License v3.0 (AGPL-3.0)** 授权，完整条款见 [LICENSE](LICENSE)。

要点：

- 可自由使用、修改、分发；
- 分发修改版时，必须以相同协议（AGPL-3.0）开源你的修改；
- **网络服务条款**：若你将本 Skill（或其修改版）用于向用户提供网络服务，也必须向这些用户提供对应的完整源码。

```
Copyright (C) 2026 Starlordzz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
