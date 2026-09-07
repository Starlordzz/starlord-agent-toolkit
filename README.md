# Multi-UIAutomator2 (Automation Service & SDK)

> **按需启动、无常驻后台、多语言共享（Python / Dart / MCP）、带 AI 视觉与语义理解的 Android UI 自动化服务**

---

## ⚠️ 重复造轮子声明

本项目是一个典型的**重复造轮子**项目 —— 市面上已有许多更成熟、更完善的同类方案，如果没有特殊的自用需求，请优先使用它们：

| 已有方案 | 说明 |
| :--- | :--- |
| [openatx/uiautomator2](https://github.com/openatx/uiautomator2) | 本项目底层依赖的 Python 库，单项目使用直接用它即可 |
| [mobile-next/mobile-mcp](https://github.com/mobile-next/mobile-mcp) | 让 AI 客户端（Claude / Cursor 等）直接操控 Android / iOS 设备的 MCP Server |
| [droidrun/droidrun](https://github.com/droidrun/droidrun) | LLM 驱动的 Android 自动化 Agent 框架 |
| [Appium](https://github.com/appium/appium) | 老牌跨平台移动端自动化框架 |
| [Maestro](https://github.com/mobile-dev-inc/maestro) | 简单易用的移动端 UI 测试框架 |

本项目继续存在的理由只有两个：

- **学习练手**：把 uiautomator2、MCP 协议、多语言 SDK 串起来完整跑通一遍；
- **自用场景**：多个本地项目共享同一个「按需启动、空闲自退出」的自动化服务实例，并顺带暴露为 MCP 工具。

不追求生产可用，不承诺持续维护。

---

## 🤖 MCP Server（AI 客户端直连安卓设备）

本项目内置 MCP Server（`mcp_server/`），把全部自动化能力（观察 / 点按 / 输入 / 截图 / SoM 视觉标注 / AI 自愈）暴露为 24 个 MCP 工具，可在 ZCode、Claude Desktop、Cursor 等 AI 客户端中直接操控安卓设备：

```json
{
  "mcpServers": {
    "android-device": {
      "command": "uv",
      "args": ["--directory", "/path/to/multi_uiautomator2", "run", "mcp-server-android"]
    }
  }
}
```

安装与配置详见 [mcp_server/README.md](mcp_server/README.md)。

---

## 🎯 核心设计理念

1. **按需启动，用完即走（No Always-Running Daemon）**：
   - 本地平时没有任何常驻进程占用 CPU / 内存 / 端口。
   - 任何 Python、Dart 或其他子项目调用自动化接口时，**SDK 自动在后台静默启动 `automation-server`**。
   - **Idle Watchdog（空闲看门狗）**：默认 60 秒无新请求时，服务自动断开设备连接并退出进程。
2. **多项目统一，彻底杜绝冲突**：
   - 解决多项目各自依赖 `uiautomator2` 导致的 ADB 抢占、端口冲突、Session 冲突。
   - Dart / Flutter / Python / JS 等所有项目只依赖极轻量的 Client SDK。
3. **AI 视觉与语义理解（Self-Understanding & AI Debug）**：
   - 自动将庞大的 Android XML 结构树提炼为编号交互元素列表（大幅降低 90%+ Token 消耗）。
   - 支持 Set-of-Marks (SoM) 视觉标记与多模态大模型对接。
   - 提供自然语言目标驱动 (`ai_act`)、界面语义分析 (`ai_understand`) 和异常弹窗/崩溃自动诊断修复 (`ai_debug`)。

---

## 🏗️ 架构全景

```
 ┌──────────────────────┐      ┌──────────────────────┐
 │    Python 项目       │      │     Dart / Flutter   │
 │ (automation_client)  │      │ (automation_client)  │
 └──────────┬───────────┘      └──────────┬───────────┘
            │                             │
            │ HTTP (离线时自动拉起 Server)  │
            └──────────────┬──────────────┘
                           ↓
        ┌──────────────────────────────────────┐
        │       Automation Server (8765)       │
        │  - 60s 空闲自动退出 (Idle Watchdog)   │
        │  - UIAutomator2 / ADB 设备池调度     │
        │  - UI 树精简与 Set-of-Marks 视觉标记  │
        │  - AI 目标规划与自动调试诊断          │
        └──────────────────┬───────────────────┘
                           │
             ┌─────────────┴─────────────┐
             ↓                           ↓
            ADB                     UIAutomator2
             │                           │
             └─────────────┬─────────────┘
                           ↓
                    Android 设备 / 模拟器
```

---

## 📦 项目结构

```
multi_uiautomator2/
├── server/                   # 自动化服务端核心
│   ├── app.py                # FastAPI 入口 & CLI
│   ├── config.py             # 配置管理 (端口、空闲超时、LLM 密钥)
│   ├── lifecycle.py          # Idle Watchdog 空闲自动退出看门狗
│   ├── core/
│   │   ├── device_manager.py # ADB 与 uiautomator2 连接与会话管理
│   │   ├── actions.py        # 统一动作引擎 (点击/输入/滑动/按键/App生命周期)
│   │   ├── hierarchy.py      # UI 树解析与 AI 编号精简器
│   │   └── screenshot.py     # 截图与 Set-of-Marks (SoM) 视觉标记
│   ├── ai/
│   │   ├── agent.py          # 界面理解、多步目标执行与自愈调试
│   │   └── llm_provider.py   # OpenAI / Gemini / 本地大模型统一接口
│   └── routes/               # API 路由 (/device, /app, /ui, /ai)
├── mcp_server/               # MCP Server (AI 客户端 stdio 接入, 24 个工具)
│   ├── server.py
│   └── README.md
├── sdk/
│   ├── python/               # Python SDK
│   │   ├── automation_client/
│   │   └── examples/
│   └── dart/                 # Dart SDK
│       ├── lib/
│       └── example/
├── tests/                    # 单元与集成测试
└── requirements.txt          # Python 依赖
```

---

## 🚀 快速开始

### 1. 安装服务端依赖

```bash
pip install -r requirements.txt
```

---

### 2. Python 项目中使用

在 Python 项目中引入客户端即可，**无需手动启动服务端**：

```python
from automation_client import AutomationClient

# 创建 Client（会自动检测并在后台拉起 server，60s 无请求后自动关闭）
client = AutomationClient(auto_start_server=True, idle_timeout=60)

# 连接手机
client.connect()

# 基础操作
client.click(text="登录")
client.input(text="my_username", resource_id="com.example:id/username")
client.press("home")

# 截图保存
client.screenshot(save_path="screen.png")

# 获取精简 UI 树
dump = client.dump(simplified=True)
print(f"当前屏幕有 {dump['element_count']} 个可操作控件")

# AI 自然语言驱动（需配置 OPENAI_API_KEY）
res = client.ai_act(goal="点击设置图标进入关于手机页面")
print("AI 执行结果:", res)
```

---

### 3. Dart / Flutter 项目中使用

在 Dart / Flutter 项目中：

```dart
import 'package:automation_client/automation_client.dart';

void main() async {
  // 创建 Client（Dart 端纯 HTTP，自动检测并按需拉起本地服务）
  final client = AutomationClient(autoStartServer: true, idleTimeout: 60);

  // 连接设备
  await client.connect();

  // 点击与输入
  await client.click(text: "登录");
  await client.input(text: "my_username", resourceId: "username");

  // 截屏保存
  await client.screenshot(savePath: "screen.png");

  // 按键
  await client.press(key: "home");

  // AI 语义分析当前界面
  final analysis = await client.aiUnderstand();
  print("页面类型: ${analysis['analysis']['screen_type']}");

  client.close();
}
```

---

## 🧠 AI Agent 与自我理解能力

| 功能 | API | 说明 |
| :--- | :--- | :--- |
| **语义理解** | `POST /ai/understand` | 识别当前页面类型 (登录/表单/列表/弹窗)，提炼核心控件 |
| **目标驱动** | `POST /ai/act` | 接受自然语言目标（如 `"打开WiFi设置并开启开关"`），自动进行「观察 -> 思考 -> 点击/输入 -> 验证」多步闭环 |
| **异常自愈** | `POST /ai/debug` | 检测界面是否发生 Crash、ANR、权限拦截或异常遮罩，并可自动点击关闭或回退 |

---

## 🛠️ REST API 接口清单

| 分组 | 方法 | 路径 | 描述 |
| :--- | :--- | :--- | :--- |
| **System** | `GET` | `/health` | 健康检查 (SDK 检测存活) |
| | `GET` | `/status` | 服务状态与空闲倒计时 |
| | `POST` | `/config/idle-timeout` | 动态修改空闲超时时间 (秒) |
| | `POST` | `/shutdown` | 手动关闭服务 |
| **Device** | `GET` | `/device/list` | 列出所有 ADB 设备 |
| | `POST` | `/device/connect` | 连接指定/默认设备 |
| | `GET` | `/device/info` | 获取分辨率/前台App等信息 |
| | `POST` | `/device/disconnect` | 断开并释放设备会话 |
| **UI** | `POST` | `/ui/click` | 点击坐标或选择器 |
| | `POST` | `/ui/input` | 输入文本 |
| | `POST` | `/ui/clear` | 清除输入框文本 |
| | `POST` | `/ui/swipe` | 屏幕滑动 |
| | `POST` | `/ui/scroll` | 页面滚动 (up/down/left/right) |
| | `POST` | `/ui/press` | 按键 (back/home/enter 等) |
| | `POST` | `/ui/screenshot` | 截屏 (可附带 SoM 视觉标注) |
| | `POST` | `/ui/dump` | 获取精简 UI 树与交互元素 |
| | `POST` | `/ui/find` | 检查元素是否存在 |
| | `POST` | `/ui/wait` | 等待元素出现 |
| **App** | `POST` | `/app/start` | 启动指定 App |
| | `POST` | `/app/stop` | 强制停止 App |
| | `GET` | `/app/current` | 获取当前前台 App |
| **AI** | `POST` | `/ai/understand` | 屏幕语义解析 |
| | `POST` | `/ai/act` | 自然语言多步目标执行 |
| | `POST` | `/ai/debug` | 异常弹窗/崩溃诊断与自动修复 |

