---
name: browser-automation
description: 浏览器自动化综合技能集，聚合子技能覆盖浏览器交互、网页测试、数据抓取等完整链路。当用户涉及浏览器自动化、网页操作、网页测试、数据抓取等场景时触发。
---

## 静态网站优先使用无浏览器方式

**对于静态网站（无需 JavaScript 渲染、无需登录交互的页面），严禁调用本技能的任何子技能。** 优先使用以下无浏览器方式直接获取内容：

### Python（推荐，环境预装）
| 方式 | 命令/代码 | 说明 |
|------|-----------|------|
| `requests` | `requests.get(url).text` | 环境预装，最常用 |
| `httpx` | `httpx.get(url).text` | 支持 HTTP/2，需 `pip_install httpx` |
| `urllib` | `urllib.request.urlopen(url).read()` | 内置模块，零依赖 |

### Node.js（环境可用）
| 方式 | 命令/代码 | 说明 |
|------|-----------|------|
| `fetch` | `fetch(url).then(r => r.text())` | Node 18+ 内置，无需安装 |
| `axios` | `axios.get(url)` | 需 `npm install axios` |

### 命令行
| 方式 | 命令 | 说明 |
|------|------|------|
| `curl` | `curl -sL <url>` | Windows 可用 |
| PowerShell | `Invoke-WebRequest -Uri <url>` | 系统内置 |

### Jina Reader API（AI 友好）
```
https://r.jina.ai/<目标URL>
```
返回 AI 可直接消费的 Markdown 格式内容，适合快速提取正文。

**判断标准**：先尝试上述无浏览器方式获取内容。仅当遇到以下情况时，才回退到 browser-automation 子技能：
- 页面内容依赖 JavaScript 动态渲染
- 需要点击、滚动、表单填写等交互操作
- 需要绕过 Cloudflare 等反爬机制
- 需要获取登录态后的页面

---

## 强制浏览器规则（优先级高于所有子技能默认配置）

**严禁关闭正在运行中的 Microsoft Edge 浏览器。**
在任何场景、任何情况下，不得主动终止、关闭或强制停止正在运行的 Edge 浏览器进程。

**操作完毕后绝不可关闭浏览器。**
浏览器窗口在自动化操作完成后必须保持打开状态，不得执行 `browser.close()` 或任何关闭浏览器/页面的操作。

**严禁启动新的浏览器实例。**
在任何场景、任何情况下，不得创建新的 Edge 浏览器进程。即使以 `--remote-debugging-port` 参数启动也不行。

**严禁重新启动浏览器。**
不得为了启用调试模式或其他目的而关闭浏览器后重新启动。

**严禁使用无头模式。**
`headless` 必须始终设为 `False`，窗口必须保持用户可见。

**不得关闭、最小化或隐藏用户正在使用的浏览器窗口。**
自动化操作不得影响用户正在浏览的页面和窗口状态。

**不得引导用户通过 `chrome://inspect/#remote-debugging` 手动开启远程调试。**
所有调试端口的启用和连接必须由 Agent 自动完成。

**所有浏览器自动化操作必须使用用户本地已安装的 Microsoft Edge 浏览器，严禁下载或安装任何其他浏览器（包括 Chromium、Chrome、Firefox 等）。**
- Edge 可执行文件路径：`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
- 所有子技能（agent-browser、browser-use、browser-harness、playwright-cli、playwright-mcp、Chrome-DevTools-MCP、Scrapling、webwright 等）在启动浏览器时，必须显式指定使用此路径的 Edge 浏览器
- 连接前必须读取 `%LOCALAPPDATA%\Microsoft\Edge\User Data\DevToolsActivePort` 文件获取 Edge 浏览器的远程调试模式动态端口，直接使用 DevToolsActivePort 文件读取端口后，使用 ws\:// WebSocket URL 进行连接，严禁使用 HTTP 端点。

## playwright-cli / playwright-mcp 连接优先级（扩展模式优先，CDP 兜底）

**连接本地带登录态的 Edge 浏览器时，playwright-cli 与 playwright-mcp 必须遵循以下优先级：**

1. **优先使用扩展模式（`--extension`）**：通过 Playwright 浏览器扩展连接运行中的 Edge，无需 CDP 端口，保留完整登录态。
2. **扩展未安装或扩展模式连接失败时，回退使用 CDP（`--cdp=msedge` / `--cdp-endpoint`）**：按浏览器通道名自动发现或通过 WebSocket URL 连接已运行的 Edge。

**检测扩展是否安装是被允许的。** 判断扩展模式是否可用（检查 Edge User Data 下是否存在 Playwright 扩展目录、环境变量 `PLAYWRIGHT_MCP_EXTENSION_TOKEN` 是否已设置）属正常前置检查，可放心执行；此检查仅针对扩展模式，与 CDP 连接规则无关。

**扩展模式前置条件（两个均需满足）：**
- Edge 已安装 Playwright 扩展（扩展 ID：`mmlmfjhmonkocbjadbfplnigmagldckm`，目录位于 `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Extensions\`）。
- 环境变量 `PLAYWRIGHT_MCP_EXTENSION_TOKEN` 已设置（从扩展设置页面获取）。

**扩展模式与 CDP 的连接差异：**
- playwright-cli：`attach --extension=msedge` 按浏览器通道名**自动识别 Edge**，无需显式指定路径。
- playwright-mcp：扩展模式默认查找 Chrome 的 User Data，**必须**通过 `--executable-path` 与 `--user-data-dir` 显式指向 Edge（否则报 `Playwright Extension not found in ...Chrome\User Data`）。
- playwright-mcp 扩展模式连接成功后无需 `--headless` 也可工作；CDP 兜底时**不可带 `--headless`**（会导致 `Timeout 30000ms exceeded` 超时）。

各子技能的具体连接命令见下文「各子技能连接已运行 Edge 浏览器的方式」。


## 自动启动浏览器（解决 CDP 依赖浏览器已运行的缺陷）

当前所有子技能在连接浏览器时，都假设 Edge 已经运行且 CDP 已开启。
如果 Edge 未运行，或运行但未开启远程调试，自动化将失败。

**解决方案**：使用 `scripts/browser_launcher.py` 自动检测并启动 Edge。

### 自动决策树

```
用户请求浏览器自动化
  │
  ├─ CDP 可用（DevToolsActivePort 有效）→ 直接连接 ✅
  │
  ├─ Edge 未运行 → 自动启动 Edge（默认 profile）→ 等待 CDP 就绪 → 连接 ✅
  │     └─ 启动参数：--user-data-dir=默认目录（保留登录态）
  │                   --remote-debugging-port=9222
  │                   --no-first-run --new-window about:blank
  │
  └─ Edge 运行但 CDP 不可用 → 抛出异常，建议使用 Extension 模式
        └─ 原因：已有 Edge 进程锁定用户数据目录，无法启动第二个实例
```

### 使用方法

```python
from browser_automation.scripts.browser_launcher import ensure_edge

# 一行搞定：自动检测 → 自动启动 → 返回 WebSocket URL
ws_url = ensure_edge()

# 然后任何子技能都可以用这个 ws_url 连接
# 例如 Playwright:
browser = playwright.chromium.connect_over_cdp(ws_url)
```

### 启动策略详解

| 策略 | 说明 |
|------|------|
| `--user-data-dir` | 使用默认 profile 目录，保留全部 Cookie、历史记录、扩展、设置 |
| `--remote-debugging-port=9222` | 开启 CDP 远程调试 |
| `--no-first-run` | 跳过首次运行向导 |
| `--new-window about:blank` | 不自动加载任何页面，不干扰用户 |
| `subprocess.CREATE_NO_WINDOW` | 不弹出控制台窗口 |

### 关键设计决策

1. **为什么使用默认 User Data 目录？**
   - 用户的所有登录态（Cookie、会话、扩展）都存储在默认 profile
   - 新启动的 Edge 与用户手动打开的 Edge 具有完全相同的登录态
   - 解决了「新启动的浏览器没有登录态」的核心问题

2. **为什么使用 `about:blank`？**
   - 不自动加载任何页面，避免干扰用户
   - 用户看到的是空白页，可以在需要时手动导航

3. **Edge 已运行但 CDP 未开启怎么办？**
   - 这是最难处理的场景：已有 Edge 进程锁定了用户数据目录
   - 无法启动第二个实例，也无法给已有进程动态添加 CDP
   - **解决方案**：使用 playwright-cli / playwright-mcp 的 `--extension` 扩展模式（无需 CDP，通过 Playwright 浏览器扩展连接已有 Edge）

### 集成到各子技能

各子技能在连接浏览器前，应优先调用 `ensure_edge()` 确保 Edge 可连接，
而非直接假定 CDP 已就绪。

```python
# 原来的做法（有缺陷）：
ws_url = f"ws://127.0.0.1:{port}{ws_path}"  # 假设 Edge 已在运行

# 改进后的做法（自动容错）：
from browser_automation.scripts.browser_launcher import ensure_edge
ws_url = ensure_edge()  # 自动检测 + 自动启动
```

## 连接 Edge 浏览器的正确方式（覆盖子技能中的错误做法）

### 严禁使用 HTTP 端点

Edge 的 HTTP CDP 端点（`/json/version`、`/json`、`/json/list` 等）**始终返回 404**，不得用于发现 CDP 端口或 WebSocket 路径。任何依赖 HTTP 端点的连接方式（包括但不限于以下方式）在本环境均不可用：

- `http://127.0.0.1:<port>/json/version` → 404
- `http://127.0.0.1:<port>/json` → 404
- `browser-use --cdp-url http://...` → 失败
- `browser-harness` 的 HTTP 发现逻辑 → 失败
- 所有基于 HTTP 的端口扫描或探测 → 失败

### 可靠的连接方式

1. 读取 `DevToolsActivePort` 文件获取端口和 WebSocket 路径
2. 构建 `ws://127.0.0.1:{port}{ws_path}` WebSocket URL
3. 直接通过 WebSocket URL 连接
4. **WebSocket 握手时不得携带 Origin 头**（携带任何 Origin 头都会导致 Edge 返回 403 Forbidden）
5. 连接后发送的 WebSocket 帧**必须设置 mask 位**（客户端帧必须 masked）

### Origin 头导致 403 的排查与解决

**现象**：WebSocket 握手失败，返回 `Handshake status 403 Forbidden`，错误信息为：

```
Rejected an incoming WebSocket connection from the http://127.0.0.1:<port> origin.
Use the command line flag --remote-allow-origins=http://127.0.0.1:<port> to allow
connections from this origin or --remote-allow-origins=* to allow all origins.
```

**根因**：Edge CDP 服务器在 WebSocket 握手中校验 Origin 头。大多数 WebSocket 客户端库（如 Python 的 `websocket-client`、Node.js 的 `ws`）默认会携带 Origin 头，触发 Edge 的内置校验，返回 403。

**不同语言/库的解决办法**：

| 语言/库 | 做法 | 代码示例 |
|---------|------|---------|
| Python `websocket-client` | 传 `suppress_origin=True` | `ws = websocket.create_connection(ws_url, suppress_origin=True)` |
| Python `websockets` (asyncio) | 传 `origin=None` | `ws = await websockets.connect(ws_url, origin=None)` |
| Node.js `ws` | 设 `headers: { 'Origin': '' }` | `new WebSocket(ws_url, { headers: { 'Origin': '' } })` |
| PowerShell | 清空 Origin 头 | `$ws.Options.SetRequestHeader('Origin', '')` |
| Playwright `connect_over_cdp` | 框架自动处理，无需额外设置 | `browser = playwright.chromium.connect_over_cdp(cdp_url)` |

> **为什么禁用 Origin 头是安全的？** Edge CDP 的身份验证依赖的是 `DevToolsActivePort` 文件的本地文件系统权限——只有能读取该文件的本地进程才能获取端口和 UUID。这本身就是足够的安全屏障。`--remote-allow-origins=*` 会降低安全性，不应使用。

### 注意 UUID 会变化

Edge 每次重启后，`DevToolsActivePort` 中的 WebSocket 路径 UUID（如 `/devtools/browser/<uuid>`）都会重新生成。**严禁硬编码 UUID**，必须每次从 DevToolsActivePort 文件重新读取。

### 覆盖各子技能中的错误做法

以下子技能中包含了使用 HTTP 端点的错误示例或默认行为，必须按上述正确方式覆盖：

- **browser-harness**：其 `ensure_daemon()` 优先尝试 `/json/version` HTTP 端点发现 CDP 端口，在本环境此方式始终失败。必须跳过 HTTP 发现，直接读取 DevToolsActivePort 文件
- **browser-use**：`--cdp-url http://...` 方式不可用，必须使用 `ws://` WebSocket URL
- **playwright-cli**：`--cdp=http://...` 方式不可靠，应使用 `--cdp=msedge` 自动发现或 `--cdp=ws://...` 直连。**连接优先级见上方「playwright-cli / playwright-mcp 连接优先级」：先尝试 `--extension=msedge` 扩展模式，失败再回退 CDP。**

---

---

## ⚠️ 强制启用 site-memory 持久记忆（不可跳过）

**所有 browser-automation 任务必须严格执行以下 pre-flight / post-flight 流程，不得跳过任意一步。**

### Pre-Flight（任务开始前，按序执行）

```
步骤1 → node site-memory/scripts/init-memory-root.mjs
步骤2 → node site-memory/scripts/build-recall-input.mjs --task "<当前任务描述>" --recent-tools "<工具列表>"
步骤3 → node site-memory/scripts/read-recalled-files.mjs --files "<上一步返回的文件列表>"
步骤4 → 将召回的记忆注入当前上下文
```

如果初始化/召回脚本执行失败，不得继续执行浏览器自动化任务，必须先修复记忆系统。

### Post-Flight（任务结束后，按序执行）

```
步骤1 → 将本次操作的可重放流程写入 site-memory/memory/notes/operator/
步骤2 → 笔记必须包含完整的 frontmatter（name、summary、tags、noteTypes）
步骤3 → 内容格式：目标 → 前置条件 → 操作步骤（含代码/命令）→ 已知要点
```

### 记忆存储位置

```
browser-automation/site-memory/memory/
├── INDEX.md
├── manifest.json
└── notes/
    ├── operator/   # 【重点】可重放的操作流程
    ├── guidance/   # 用户偏好/规则
    ├── context/    # 上下文信息（临时）
    └── reference/  # 参考资料
```

### 违规后果

未执行 Pre-Flight 或 Post-Flight 中的任意步骤，视为违反本技能的强制规则。

详见 `site-memory/SKILL.md`


## 子技能列表

### agent-browser
Core agent-browser usage guide（当前版本：0.29.1）。覆盖 snapshot-and-ref 工作流、页面导航、元素交互（click, fill, type, select）、文本和数据提取、截图、标签页管理、表单和认证处理、内容等待、并行多浏览器会话以及常见故障排查。适用于网页交互、表单填写、数据提取、截图、登录、Web 应用测试等场景。

#### ⚠️ 本环境已知问题
- **`agent-browser --auto-connect` 无法识别 Edge**：该命令仅对 Chrome 有效，对 Microsoft Edge 会报 "No running Chrome instance found"，不可用于本环境
- **`agent-browser --cdp <port>` 同样无法识别 Edge**：与 `--auto-connect` 同一问题，不可用于本环境
- **唯一可行的连接方式**：通过 `agent-browser connect ws://127.0.0.1:{端口}{WebSocket路径}` 使用 WebSocket URL 连接（见下方连接方式）
- **`agent-browser tab list` 命令可能超时**：实测该命令连接后可能无响应（超时后被 kill），标签页管理建议使用 PowerShell CDP 直连方案替代
- **`agent-browser open` 在部分网站可能触发 Cloudflare 拦截**：部分网页（如 chat.deepseek.com）可能返回请求被拦截，但页面实际已加载，通过 `get title` / `get url` 确认实际状态

### browser-use
基于 browser-use CLI 的浏览器自动化技能，专为 AI Agent 设计。适用于网页导航、表单填写、截图、网页数据提取、Cookie 管理等场景。**强制使用本地带登录态的 Edge 浏览器，浏览器窗口必须可见。**

#### ⚠️ 本环境已知问题
- **`browser-use connect` 命令在此环境下无法正常工作**（Edge HTTP CDP 端点返回 404），不要依赖它作为唯一连接手段
- **`browser-use --cdp-url http://...` 不适用于此环境的 Edge**（HTTP 端点 404），必须使用 `ws://` WebSocket URL
- **通过 CDP 创建的标签页默认在后台打开**，需额外执行 `Target.activateTarget` 或 `browser-use tab switch` 才能跳到前台
- **严禁使用 `--profile` 方式**：这会启动新浏览器实例，违反顶层规则
- **严禁使用无头模式**：`open` 默认启动 headless 浏览器，必须通过 CDP 连接已有 Edge

### browser-harness
通过 CDP 直接控制浏览器的自动化技能。支持本地 Chrome/Edge CDP 连接、远程云端浏览器（Browser Use cloud）、多会话管理、Cookie 同步、截图与点击坐标工作流、跨域 iframe/Shadow DOM 处理等。自动化工作流核心：`ensure_real_tab()` 确保当前标签页有效 → `capture_screenshot()` 截图理解页面状态 → `click_at_xy(x,y)` 坐标点击 → `wait_for_load()` 等待加载 → 必要时用 `js(...)` 做 DOM 检查。

**连接层自修复**：`ensure_daemon()` 自动检测 daemon 存活状态，若 CDP 连接断开则自动重建。**本环境禁用 HTTP 端点发现（404 无效），一律直接读取 `DevToolsActivePort` 文件获取 WebSocket 地址**，无需手动干预。

**其他交互能力参考**（非内置，对应 GitHub 链接受限于网络）：cookies、dialogs、downloads、drag-and-drop、dropdowns、iframes、network-requests、print-as-pdf、scrolling、shadow-dom、tabs、uploads、viewport。

### playwright-cli
基于 Playwright 的浏览器自动化 CLI 工具，专为编码代理（Coding Agents）优化。提供 token 高效的浏览器控制命令，支持页面导航、元素交互（click, fill, drag, drop, hover, select）、截图/PDF 导出、多标签页管理、Cookie/LocalStorage/SessionStorage 操作、网络请求拦截与 Mock、视频录制、Tracing、DevTools 调试（console, network, requests）、扩展模式（--extension）与 CDP 附加连接、元素高亮标注、Locator 生成、UI 审查批注（show --annotate）、规范驱动测试等。连接本地 Edge 时优先扩展模式，失败回退 CDP（见下方连接方式）。

### Chrome-DevTools-MCP
Chrome DevTools MCP 官方子技能套件（ChromeDevTools/chrome-devtools-mcp），聚合 6 个 CDP 协议层调试与诊断子技能：
- **chrome-devtools** — 通过 MCP 使用 Chrome DevTools 进行高效调试、故障排查和浏览器自动化
- **chrome-devtools-cli** — 通过 CLI 命令自动化浏览器操作和 DevTools 功能；提供 `chrome-devtools start`/`status`/`stop` 服务管理与 `list_pages`/`take_snapshot`/`click`/`fill`/`navigate_page` 等全量浏览器操作命令
- **a11y-debugging** — 基于 web.dev 指南的无障碍（a11y）调试与审计
- **debug-optimize-lcp** — Largest Contentful Paint（LCP）性能调试与优化
- **memory-leak-debugging** — JavaScript/Node.js 内存泄漏诊断与解决
- **troubleshooting** — 连接与目标问题的故障排查

### Scrapling
使用 Scrapling 抓取网页，支持反机器人绕过（如 Cloudflare Turnstile）、隐身无头浏览、Spider 框架、自适应抓取和 JavaScript 渲染。覆盖 Fetcher（静态/动态/隐身会话）、Parser（Adaptive/MainClasses/Selection）、Spider（架构/高级/代理/IP 轮换/请求响应/会话管理）等完整链路。适用场景：网页内容抓取、反爬对抗、动态页面渲染、批量爬取、交互式爬虫调试等。

### webwright
基于 Playwright 的代码即操作（code-as-action）浏览器自动化子技能。通过编写和运行 final_script.py 完成网页任务，自动保存截图和动作日志，并支持视觉自验证。提供默认单次执行和可重用 CLI 工具两种模式。适用于需要编写可复用自动化脚本、批量执行网页操作、记录执行过程供事后审查的场景。

【本环境适配】webwright 官方默认启动新浏览器实例，但本环境强制通过 CDP 连接已运行的 Edge 浏览器（见下方连接方式），不可启动新浏览器。所有 webwright 脚本中的浏览器启动代码必须替换为 `connect_over_cdp` 方式。

### playwright-mcp

Playwright MCP 服务 — 通过 MCP 协议驱动 Playwright 进行浏览器自动化操作。提供 22 个工具，覆盖页面导航、元素交互（点击/填写/拖拽/悬停）、截图、无障碍快照、表单填写、标签页管理、JavaScript 执行、网络请求监控、控制台日志、文件上传/拖放等。连接本地已运行的 Edge 浏览器时**优先扩展模式（`--extension`）**，扩展未安装或失败时回退 `--cdp-endpoint`（见下方连接方式）。

通过 `mcporter call playwright-mcp.<工具名>` 调用。

详细使用方式见 `playwright-mcp/SKILL.md`。

## 信息密度优化工具（新增）

这两个工具位于 `scripts/web_tools.py`，解决的核心问题是：
**"如何用最少的 token 获取最多的有效信息"**。
它们独立于各子技能，可在所有子技能中复用。

> 来源：GenericAgent (lsdefine/GenericAgent) 的 `simphtml.py` + `ga.py`，遵循 MIT 许可证

### web_scan —— 布局感知的页面内容提取

**替代各子技能的 snapshot/get_html/content 命令。** 自动完成以下流程：

1. **布局分析**：在浏览器中执行 `js_optHTML`，克隆 DOM → 计算每个元素的可见性/面积/Z-index → 覆盖检测（`hasOverlap`）→ 主/次划分（`analyzeNode`）→ 浮动弹窗提升（Hoist）→ 标记 `R:floatingAd` 并删除
2. **属性级 token 压缩**：`src`(>30) → `__url__`、`data:` → `__img__`、style 移除、data-v* 清除
3. **重复列表自动截断**：`findMainList()` 扫描全页面找候选容器 → 标签/类名统计分组 → 5 维评分（面积比 + 均匀性 + 布局 + 计数 + 尺寸）→ 保留前 3-6 项
4. **递归预算控制**：超出 `maxlen` 时按比例从最大子元素削减或从尾部删除

```python
from browser_automation.scripts.web_tools import web_scan

# 获取简化 HTML（自动布局分析 + 压缩 + 列表截断）
result = web_scan(driver)
# result.content —— 简化后的 HTML
# result.metadata.tabs —— 所有标签页列表

# 仅获取标签页列表（省 token）
result = web_scan(driver, tabs_only=True)

# 纯文本模式
result = web_scan(driver, text_only=True)

# 切换标签页
result = web_scan(driver, switch_tab_id="<tab_id>")
```

### web_execute_js —— 带变化观测的 JS 执行

**替代各子技能的 eval/execute_script。** 在返回 JS 返回值的同时自动附加：

1. **瞬变文本采集**：执行前注入 `startStrMonitor`（450ms 轮询），执行后对比初始/最终的文本集合 → `transients`
2. **DOM 差异检测**：`find_changed_elements()` 比较执行前后的 HTML 签名（`tagName:attrs:directText`）→ `diff`（含 `top_change`）
3. **新标签页自动发现**：比较执行前后的会话 ID 集合 → 自动识别新标签页

```python
from browser_automation.scripts.web_tools import web_execute_js

# 执行 JS + 自动检测页面变化
result = web_execute_js(driver, "document.querySelector('button').click()")
# result.js_return —— JS 返回值
# result.diff —— DOM 变化摘要
# result.transients —— 页面新增文本
# result.newTabs —— 新标签页列表

# 纯读取时设置 no_monitor=True（省 2-3 秒）
result = web_execute_js(driver, "return document.title", no_monitor=True)
```

### 子技能适配对照

| 子技能 | web_scan 替代 | web_execute_js 替代 |
|--------|--------------|--------------------|
| agent-browser | `snapshot` → `web_scan(driver)` | `eval` → `web_execute_js(driver, code)` |
| browser-use | `state` → `web_scan(driver)` | `eval` → `web_execute_js(driver, code)` |
| playwright-cli | `content` → `web_scan(driver)` | `evaluate` → `web_execute_js(driver, code)` |
| browser-harness | `page_info()` → `web_scan(driver)` | `execute_js` → `web_execute_js(driver, code)` |
| playwright-mcp | `browser_snapshot` → `web_scan(driver)` | `browser_evaluate` → `web_execute_js(driver, code)` |

使用前提：`driver` 对象必须支持 `execute_js(code)` 方法（返回 `{'data': result}` 或 `{'result': result}` 格式），可选支持 `get_all_sessions()` / `get_session_dict()` / `default_session_id`。

---

## 各子技能连接已运行 Edge 浏览器的方式

本环境强制使用已运行的 Microsoft Edge。Edge 的 CDP 端口不固定，需从 `DevToolsActivePort` 文件读取：

```python
import os
port_file = os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\DevToolsActivePort")
with open(port_file) as f:
    port = int(f.readline().strip())         # 第一行：端口号
    ws_path = f.readline().strip()           # 第二行：WebSocket 路径（如 /devtools/browser/<uuid>）
# CDP WebSocket 端点: ws://127.0.0.1:{port}{ws_path}
# 注意：DevToolsActivePort 有两行，需读取第二行的 WebSocket 路径构建完整 URL

# ⚠️ 连接时必须禁止 Origin 头，否则 Edge 返回 403
import websocket
ws = websocket.create_connection(f"ws://127.0.0.1:{port}{ws_path}", suppress_origin=True)
```

各子技能的具体连接方式如下：

### agent-browser

**⚠️ 注意：`agent-browser --auto-connect` 和 `agent-browser --cdp <port>` 在此环境无法连接 Edge（仅支持 Chrome）。** 必须使用以下方式通过 WebSocket URL 连接：

**正确的连接方式（通过 WebSocket URL）：**

先读取 Edge 的 CDP 端口和 WebSocket 路径构建 URL：

```powershell
# PowerShell：读取 DevToolsActivePort 获取端口和 WebSocket 路径
$portFile = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\DevToolsActivePort"
$lines = Get-Content $portFile
$port = [int]$lines[0]
$wsPath = $lines[1]
# 构建完整 WebSocket URL
$wsUrl = "ws://127.0.0.1:$port$wsPath"
# 通过 WebSocket URL 连接 Edge（唯一可用方式）
agent-browser connect "$wsUrl"
```

**连接成功后的操作：**
```bash
# 页面导航与获取信息
agent-browser open https://目标网址     # 在当前标签页导航到目标网址
agent-browser get url                   # 获取当前 URL
agent-browser get title                 # 获取页面标题

# 页面快照（含交互元素引用 ref，如 "button [ref=e6]"）
agent-browser snapshot                  # 获取完整页面快照
agent-browser snapshot -i               # 仅交互元素（更精简）
agent-browser snapshot -i -c            # 交互元素 + 紧凑模式

# 点击 / 输入元素（通过快照中的 ref）
# ⚠️ 注意：在 PowerShell 中 @ 是特殊字符，@ref 必须用引号包裹！
agent-browser click '@e9'               # 点击 ref=e9 的元素
agent-browser fill '@e4' '文本'          # 在 ref=e4 的元素中输入文本
agent-browser type '@e4' '按键文本'      # 按键级输入（支持 Tab, Enter 等）

# CSS 选择器方式（另一种选择元素的方式）
agent-browser click 'button:has-text("登录")'   # 按文本点击按钮
agent-browser click '#submit-button'             # 按 ID 选择

# find 命令（按语义查找元素并操作）
agent-browser find role button click --name '密码登录'
agent-browser find text 发送验证码 click
agent-browser find placeholder '请输入手机号' click

# 执行 JavaScript
agent-browser eval 'document.title'              # 获取页面标题
agent-browser eval 'document.querySelector("h1").textContent'

# 截图
agent-browser screenshot                         # 截取当前视口
agent-browser screenshot ./page.png              # 保存到指定路径

# 页面操作
agent-browser scroll down                        # 向下滚动
agent-browser scroll up                          # 向上滚动
agent-browser wait 2000                          # 等待 2 秒
agent-browser press Enter                        # 按键（Enter, Tab, Escape 等）
agent-browser back                               # 后退
agent-browser forward                            # 前进
agent-browser reload                             # 刷新

# 标签页管理（`tab list` 在部分环境可能超时，需注意）
agent-browser tab new https://目标网址           # 打开新标签页
agent-browser tab 1                              # 切换到第 1 个标签页
```

**PowerShell 环境说明（重要！）：**
- PowerShell **不支持** `&&` 命令连接符（这是 Bash 语法）。必须用 `;` 分隔命令：`agent-browser connect "$wsUrl"; agent-browser open https://目标网址`
- 在 PowerShell 中 `@` 是数组/变量的特殊字符，`@ref` 必须用**引号包裹**：`'@e9'` 或 `"@e9"`，否则会报 "Missing arguments" 错误

**注意：** `agent-browser connect` 仅建立 CDP 会话连接，不会关闭浏览器。

### browser-use

**⚠️ 先决条件：** 用户必须已经打开了一个 Edge 浏览器窗口（有 Edge 进程在运行），这样 `DevToolsActivePort` 文件中才会有有效的端口和 WebSocket 路径。

**1. 读取 Edge 动态端口并构建 WebSocket URL：**

```powershell
# PowerShell：读取 DevToolsActivePort 获取端口和 WebSocket 路径
$portFile = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\DevToolsActivePort"
$lines = Get-Content $portFile
$port = [int]$lines[0]
$wsPath = $lines[1]
# 构建完整 WebSocket URL：ws://127.0.0.1:<port>/devtools/browser/<uuid>
$wsUrl = "ws://127.0.0.1:$port$wsPath"
```

**2. 通过 `ws://` CDP URL 连接并操作（推荐）：**

```bash
# 先连接（必须用 ws://，不要用 http://）
browser-use --cdp-url "ws://127.0.0.1:<port>/devtools/browser/<uuid>"

# 打开新标签页（默认在后台打开）
browser-use tab new https://example.com

# 切换到前台显示
browser-use tab switch <索引>
```

**3. ⚠️ 以下方式禁用于本环境：**

| 方式 | 原因 |
|------|------|
| `browser-use connect` | HTTP CDP 端点 404，连接失败 |
| `browser-use --cdp-url http://...` | HTTP 端点 404，必须用 `ws://` |
| `browser-use open <url>` | 默认启动 headless Chromium，违反规则 |
| `browser-use --profile "..." open <url>` | 启动新浏览器实例，违反规则 |

**4. 备用方案：CDP WebSocket 直连（推荐优先使用，比 browser-use CLI 更可靠）**

> ⚠️ 实测表明，本环境中 `browser-use --cdp-url` 命令的运行输出不直观（仅打印环境变量注入信息，无命令结果确认），而以下 PowerShell CDP 直连方案经验证可正常创建并激活标签页。**建议优先使用此方案。**

以下 PowerShell 脚本可直接通过 CDP WebSocket 打开并激活标签页，无需依赖 browser-use CLI：

```powershell
$lines = Get-Content "$env:LOCALAPPDATA\Microsoft\Edge\User Data\DevToolsActivePort"
$port = [int]$lines[0]
$wsPath = $lines[1]
$wsUrl = "ws://127.0.0.1:$port$wsPath"

$ws = New-Object System.Net.WebSockets.ClientWebSocket
$ct = New-Object System.Threading.CancellationToken
$ws.ConnectAsync([System.Uri]$wsUrl, $ct).Wait()

# 创建新标签页
$create = @{id=1; method="Target.createTarget"; params=@{url="https://目标网址"; newWindow=$false}} | ConvertTo-Json
$bytes = [System.Text.Encoding]::UTF8.GetBytes($create)
$ws.SendAsync([ArraySegment[byte]]::new($bytes), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait()

# 读取返回中的 targetId
$buffer = New-Object byte[] 4096
$result = $ws.ReceiveAsync([ArraySegment[byte]]::new($buffer), $ct).Result
$response = [System.Text.Encoding]::UTF8.GetString($buffer, 0, $result.Count)
$targetId = ($response | ConvertFrom-Json).result.targetId

# 激活到前台
$activate = @{id=2; method="Target.activateTarget"; params=@{targetId=$targetId}} | ConvertTo-Json
$bytes2 = [System.Text.Encoding]::UTF8.GetBytes($activate)
$ws.SendAsync([ArraySegment[byte]]::new($bytes2), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait()

$ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "done", $ct).Wait()
# ⚠️ 注意：上述只关闭 WebSocket 连接（$ws），不是关闭 Edge 浏览器！Edge 窗口必须保持打开。
Write-Output "✅ 标签页已创建并激活到前台"
```

**5. 连接后的常用操作（完整命令参考见 `browser-use/SKILL.md`）**

连接成功后，可通过 browser-use CLI 执行以下操作：

| 操作 | 命令 | 说明 |
|------|------|------|
| 获取页面状态 | `browser-use state` | 获取 URL、标题、可点击元素列表 |
| 截图 | `browser-use screenshot [path.png]` | 页面截图（`--full` 全页） |
| 点击元素 | `browser-use click <索引>` | 按 state 返回的索引点击 |
| 输入文本 | `browser-use input <索引> "文本"` | 点击元素并输入文本 |
| 执行 JS | `browser-use eval "js代码"` | 执行 JavaScript 返回结果 |
| 获取 HTML | `browser-use get html` | 获取页面 HTML |
| 标签页管理 | `browser-use tab list/switch/close` | 管理多个标签页 |

> ⚠️ 注意：`browser-use close` 命令在此环境下可能关闭 CDP 会话而非浏览器本身，使用需谨慎。优先使用备用方案中的 PowerShell CDP 直连完成操作后关闭 WebSocket 连接（仅断开 CDP 会话，不关闭 Edge）。

### browser-harness
自动连接。`browser-harness` 接收 stdin Python 脚本后，`main()` 调用 `ensure_daemon()` 启动 daemon 子进程。**Daemon 直接读取 `DevToolsActivePort` 文件（覆盖 Chrome 和 Edge 的 User Data 目录）获取 WebSocket 地址，不做 HTTP 端点发现（本环境 404 无效）**。整体无需显式命令，即输即用。

**注意 PowerShell 兼容性**：PowerShell 不支持 `<<'PY'` heredoc 语法，需用管道传参：
```powershell
echo "print(page_info())" | browser-harness
# 或
$script = @"
new_tab("https://example.com")
print(page_info())
"@
$script | browser-harness
```

### playwright-cli
**连接优先级：扩展模式优先，CDP 兜底。** 先尝试扩展模式，扩展未安装或连接失败时回退 CDP。

```bash
# 【优先】方式一：扩展模式（自动识别 Edge，无需显式指定路径，保留登录态）
# 前置条件：Edge 已安装 Playwright 扩展，且 PLAYWRIGHT_MCP_EXTENSION_TOKEN 已设置
playwright-cli attach --extension=msedge

# 【回退】方式二：按浏览器通道名自动发现并连接已运行的 Edge
playwright-cli attach --cdp=msedge

# 【回退】方式三：通过 WebSocket URL 直接连接（当 --cdp=msedge 无法自动发现时使用）
# 需从 DevToolsActivePort 读取两行：port 和 ws_path，拼接完整 URL
# 注意：--cdp=http://... 方式在 Edge 中不可靠（HTTP 端点可能返回 404），
# 应使用 WebSocket URL 绕过此限制
playwright-cli attach --cdp=ws://127.0.0.1:<port>/devtools/browser/<uuid>
```

### Chrome-DevTools-MCP
Chrome-DevTools-MCP 通过 `chrome-devtools` CLI 连接已运行的 Edge。先读取 Edge 的 CDP 端口和 WebSocket 路径：

```powershell
# PowerShell：读取 DevToolsActivePort 获取端口和 WebSocket 路径
$portFile = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\DevToolsActivePort"
$lines = Get-Content $portFile
$port = [int]$lines[0]
$wsPath = $lines[1]
# 构建完整 WebSocket URL：ws://127.0.0.1:<port>/devtools/browser/<uuid>
```

然后启动 Chrome-DevTools-MCP 守护进程连接 Edge，**必须指定 `--headless false`**：

**方式一：`--wsEndpoint`（推荐，最可靠）**
通过 WebSocket URL 直接连接，不受 HTTP 端点限制影响：
```bash
chrome-devtools start --wsEndpoint "ws://127.0.0.1:<port>/devtools/browser/<uuid>" --headless false
```

**方式二：`--browserUrl`**
通过 HTTP CDP 端点 URL 连接：
```bash
chrome-devtools start --browserUrl "http://127.0.0.1:<port>" --headless false
```

**验证连接是否成功：**
```bash
chrome-devtools status        # 确认 daemon 正在运行
chrome-devtools list_pages    # 确认能列出 Edge 中的页面
```

连接成功后，`list_pages`、`select_page`、`navigate_page`、`take_snapshot`、`click`、`fill`、`evaluate_script` 等所有 DevTools 工具直接操作已运行的 Edge。

**操作完毕后停止守护进程：**
```bash
chrome-devtools stop
```

**参数说明：**
- `-w, --wsEndpoint <url>`：WebSocket 端点 URL（如 `ws://127.0.0.1:9222/devtools/browser/<uuid>`）
- `-u, --browserUrl <url>`：HTTP CDP 端点 URL（如 `http://127.0.0.1:9222`）
- **`--headless false`（⚠️ 必须指定）**：确保浏览器窗口保持可见，禁止无头模式

**注意：** 当前安装版本（v0.23.0）不支持 `--autoConnect` 参数，请使用上述两种方式连接。若需更新版本，运行 `npm install -g chrome-devtools-mcp@latest` 后重试。

### Scrapling
```python
from scrapling.fetchers import StealthyFetcher

fetcher = StealthyFetcher(
    cdp_url=f"http://127.0.0.1:{port}",  # 连接到已运行的 Edge
)
```

### webwright
webwright 的本质是编写 Python Playwright 脚本，浏览器启动代码完全可控。本环境强制通过 CDP 连接已运行的 Edge（禁止启动新浏览器），且必须读取 `DevToolsActivePort` 的两行内容（端口和 WebSocket 路径）：

```python
import asyncio
import os
from playwright.async_api import async_playwright

# 读取 Edge 动态 CDP 端口和 WebSocket 路径（DevToolsActivePort 有两行）
port_file = os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\DevToolsActivePort")
with open(port_file) as f:
    port = int(f.readline().strip())         # 第一行：端口号，如 9222
    ws_path = f.readline().strip()           # 第二行：WebSocket 路径，如 /devtools/browser/<uuid>
ws_url = f"ws://127.0.0.1:{port}{ws_path}" # 完整 CDP WS URL

async def main():
    async with async_playwright() as p:
        # 连接已运行的 Edge，而非启动新浏览器
        browser = await p.chromium.connect_over_cdp(ws_url)
        # 使用已有浏览器上下文（保留登录态和 Cookie）
        context = browser.contexts[0]
        page = await context.new_page()

        await page.goto("https://目标网址", wait_until="domcontentloaded")
        # ... 后续操作（截图、日志等与官方模式一致）

        # 注意：严禁关闭浏览器！勿调用 await browser.close()

asyncio.run(main())
```

**关键规则：**
- 必须使用 `async_playwright` + `asyncio.run()` 模式
- 必须通过 `connect_over_cdp(ws_url)` 连接已运行的 Edge
- 必须使用 `browser.contexts[0]` 获取已有上下文（保留登录态）
- **禁止调用 `browser.close()`**，操作后浏览器必须保持打开状态
- 必须读取 `DevToolsActivePort` 的两行内容，不可只读端口

### playwright-mcp

**连接优先级：扩展模式优先，CDP 兜底。** playwright-mcp 连接本地带登录态的 Edge 时，先尝试扩展模式，扩展未安装或连接失败时回退 `--cdp-endpoint`。

```powershell
# 【优先】方式一：扩展模式（无需 CDP 端口，通过 Playwright 扩展连接已运行的 Edge）
# 前置条件：Edge 已安装 Playwright 扩展，且 PLAYWRIGHT_MCP_EXTENSION_TOKEN 已设置
# 关键：扩展模式默认查找 Chrome 的 User Data，必须显式指定 Edge 的 executable-path 与 user-data-dir
npx @playwright/mcp@latest --extension --executable-path="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --user-data-dir="$env:LOCALAPPDATA\Microsoft\Edge\User Data"

# 【回退】方式二：CDP（--cdp-endpoint）连接已运行的 Edge
# 注意：CDP 兜底时不可带 --headless（会导致 Timeout 30000ms exceeded 超时）
$portFile = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\DevToolsActivePort"
$lines = Get-Content $portFile
$port = [int]$lines[0]
$wsPath = $lines[1]
$wsUrl = "ws://127.0.0.1:$port$wsPath"
npx @playwright/mcp@latest --cdp-endpoint "$wsUrl"
```

连接后通过 `mcporter call playwright-mcp.<工具名>` 或 MCP 客户端调用浏览器操作工具。

## 静态网站示例

- GitHub 仓库：
  - 展示如何创建仓库并通过 GitHub Pages 部署静态站点，包括示例项目结构和配置文件。
- 微信公众号文章：
  - 提供如张羽毛的博客、丁香园等公众号文章的链接示例，示范内容提取与嵌入方法。
- 简悦、知乎专栏：
  - 示例如何使用简悦订阅知乎专栏获取静态网站设计灵感。
- 其他平台：
  - 如 SegmentFault、CSDN 博客等，提供静态网站实战案例。
- 示例项目结构：
  - /index.html、/css/*.css、/js/*.js、/assets/*.png 等文件组织方式。
