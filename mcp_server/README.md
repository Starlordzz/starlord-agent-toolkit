# Android Device MCP Server

把 Multi-UIAutomator2 的 Android 自动化能力直接暴露为 **MCP (Model Context Protocol) 工具**，让 ZCode / Claude Desktop / Cursor 等AI 客户端可以直接操控你的安卓真机或模拟器：看屏幕、点按、输入、启动 App、截图，甚至自动诊断崩溃弹窗。

```
AI 客户端 (ZCode / Claude / Cursor)
   └── 本 MCP Server (stdio, 轻量常驻)
         └── automation_client SDK (按需拉起 Automation Server)
               └── Automation Server (FastAPI :8765, 空闲自动退出)
                     └── uiautomator2 / adb → Android 设备
```

MCP Server 本身只是薄封装：所有设备工作都委托给按需启动的 Automation Server（60s/300s 无请求自动退出，下次调用自动重启），不会留常驻后台。

## 安装

前置要求：
- [uv](https://docs.astral.sh/uv/)（Python 环境由它管理，没有会自动下载）
- `adb` 在 PATH 中（Android platform-tools）
- 设备已开启 USB 调试并连接

```bash
# 在仓库根目录执行一次即可（创建 .venv 并安装全部依赖）
uv sync
```

## 接入 AI 客户端

### ZCode / Claude Desktop / 通用 MCP 客户端

在 MCP 配置文件中加入（路径换成你的实际仓库路径）：

```json
{
  "mcpServers": {
    "android-device": {
      "command": "uv",
      "args": ["--directory", "D:/LEARNING/vibeproject/multi_uiautomator2", "run", "mcp-server-android"]
    }
  }
}
```

如果不想用 script 入口，等价写法：`"args": ["--directory", "...", "run", "python", "-m", "mcp_server.server"]`。

### Cursor / 其他支持 JSON 的客户端

同上，把 JSON 放进对应客户端的 MCP 配置即可。

## 环境变量（可选）

| 变量 | 默认 | 说明 |
| :--- | :--- | :--- |
| `AUTOMATION_HOST` | `127.0.0.1` | Automation Server 地址 |
| `AUTOMATION_PORT` | `8765` | Automation Server 端口 |
| `AUTOMATION_SERIAL` | 自动探测 | 默认设备 serial（多设备时建议指定） |
| `AUTOMATION_IDLE_TIMEOUT` | `300` | 后台 server 空闲退出秒数，`0` 表示永不退出 |
| `AUTOMATION_AUTO_START` | `1` | 设为 `0` 则要求 server 已在运行 |
| `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `LLM_MODEL` | 无 | 仅 `ai_*` 系列工具需要；会自动传递给后台 server |

## 工具清单（24 个）

| 分组 | 工具 | 说明 |
| :--- | :--- | :--- |
| 系统 | `get_server_status` / `shutdown_automation_server` | 查看后台服务状态 / 手动停止（随时安全） |
| 设备 | `list_devices` / `connect_device` / `disconnect_device` / `get_device_info` | 枚举 ADB 设备、连接（记住为本次会话默认设备）、分辨率等 |
| App | `start_app` / `stop_app` / `clear_app_data` | 启动 / 强停 / 清数据（清数据需 `confirm=true`） |
| 观察 | `get_screen_elements` | **主力观察工具**：编号交互元素列表 `[3] <Button> text="登录" center=(540,1200)`，省 90% token |
| 观察 | `screenshot` | 返回真实图像（MCP image content），`with_som=true` 叠加编号框，默认压到长边 1280px |
| 操作 | `tap` / `double_tap` / `long_press` | 坐标或选择器（text / text_contains / resource_id / description / xpath / index） |
| 操作 | `input_text` / `clear_text` | 输入 / 清空，支持指定字段或当前焦点 |
| 操作 | `swipe` / `scroll` / `press_key` | 滑动手势、方向滚动、按键（home/back/enter/recent/音量等） |
| 等待 | `find_element` / `wait_for_element` | 判断元素存在 / 阻塞等待元素出现 |
| AI | `ai_understand_screen` / `ai_execute_goal` / `ai_debug_screen` | 服务端 LLM 语义分析 / 自然语言目标执行 / 崩溃弹窗自愈，需配置 LLM 环境变量 |

## 推荐工作流

给 AI 客户端的默认循环（已写入 MCP instructions，客户端会自动遵循）：

1. **观察**：`get_screen_elements`（便宜、结构化）或 `screenshot`（视觉）；
2. **行动**：`tap` / `input_text` / `press_key` / `start_app`；
3. **验证**：再次观察确认结果。

优先用选择器（text / resource_id）而非硬编码坐标，分辨率变化时更稳。`ai_execute_goal` 会把目标交给另一个服务端 LLM 循环执行，除非用户明确要求托管，否则 AI 客户端应使用基础工具自己规划。

## 测试

```bash
# 协议级冒烟测试：模拟真实客户端 stdio 连接，列出工具、验证错误路径，
# 若有真机在线则做一轮 观察→启动设置→SoM 截图→回主页 的完整闭环（非破坏性）
uv run python tests/mcp_smoke_test.py
```

## 故障排查

| 现象 | 处理 |
| :--- | :--- |
| `list_devices` 为空 | 检查 `adb devices`、USB 调试授权弹窗 |
| 工具调用报 server 启动超时 | 首次启动需拉起 FastAPI server（约 5–15s）；确认 `AUTOMATION_PORT` 未被占用 |
| `ai_*` 工具报错 | 未配置 `OPENAI_API_KEY`（或 `LLM_API_KEY`），在 MCP 配置的 `env` 中补上 |
| 长时间思考后第一次调用变慢 | 后台 server 空闲已退出，正在自动重启，属预期行为；可调大 `AUTOMATION_IDLE_TIMEOUT` |
| 多台设备 | 调一次 `connect_device` 指定 serial，或在 env 里设 `AUTOMATION_SERIAL` |
