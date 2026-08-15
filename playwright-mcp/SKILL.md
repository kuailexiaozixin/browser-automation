---
name: playwright-mcp
description: "Playwright MCP 服务 — 通过 MCP 协议驱动 Playwright 进行浏览器自动化操作，包括页面导航、元素交互（点击/填写/拖拽/悬停）、截图、无障碍快照、表单填写、标签页管理、JavaScript 执行、网络请求监控、控制台日志、文件上传/拖放等。当用户需要基于 Playwright 的浏览器自动化、网页测试、数据采集、表单自动填写时触发。"
parent: browser-automation
---

# playwright-mcp — Playwright 浏览器自动化 MCP 服务

> **传输方式**: STDIO `npx @playwright/mcp@latest`
> **服务状态**: 已配置（VS Code MCP）
> **工具数量**: 22
> **调用方式**: 通过 `mcporter call playwright-mcp.<工具名>` 或直接 MCP 客户端调用

## 连接本地 Edge 浏览器

playwright-mcp 默认启动内置 Chromium 浏览器，但本环境**强制使用已运行的 Microsoft Edge**。通过 `--cdp-endpoint` 参数连接：

```powershell
# PowerShell：读取 Edge 动态 CDP 端口和 WebSocket 路径
$portFile = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\DevToolsActivePort"
$lines = Get-Content $portFile
$port = [int]$lines[0]
$wsPath = $lines[1]
$wsUrl = "ws://127.0.0.1:$port$wsPath"

# 启动 playwright-mcp 并连接本地 Edge
npx @playwright/mcp@latest --cdp-endpoint "$wsUrl" --headless
```

| 参数 | 说明 |
|------|------|
| `--cdp-endpoint <url>` | 指定 CDP WebSocket 端点 URL，如 `ws://127.0.0.1:9222/devtools/browser/<uuid>` |
| `--browser msedge` | 指定浏览器为 Microsoft Edge |
| `--headless` | 无头模式（本环境用户已确认 Edge 已开启远程调试，无需显示窗口） |
| `--user-data-dir <path>` | 指定用户数据目录，保留登录态 |

**注意**：
- `DevToolsActivePort` 包含两行，必须同时读取端口和 WebSocket 路径
- 连接时必须确保 `--cdp-endpoint` 使用 `ws://` 协议而非 `http://`
- 操作完毕后**不得关闭 Edge 浏览器**，仅断开 MCP 连接即可

## 扩展模式（Playwright Extension）

如果 Edge 未开启远程调试，可通过安装 [Playwright Extension](https://chromewebstore.google.com/detail/playwright-extension/mmlmfjhmonkocbjadbfplnigmagldckm) 后使用 `--extension` 模式连接：

```bash
# 请先通过环境变量设置 Token（从 Playwright 扩展设置页面获取）
# 设置方式见下方「Token 配置」

# 启动 playwright-mcp 扩展模式（Token 需已注入环境变量）
npx @playwright/mcp@latest --extension --headless
```

| 参数 | 说明 |
|------|------|
| `--extension` | 通过 Playwright 扩展连接已有浏览器，无需 `--remote-debugging-port` |
| `PLAYWRIGHT_MCP_EXTENSION_TOKEN` | 环境变量，扩展与 MCP 服务器之间的认证 Token（**必须自行设置，见下方 Token 配置**） |

**注意**：
- `--extension` 是布尔标志，无需指定浏览器通道名（自动识别已安装扩展的浏览器）
- `PLAYWRIGHT_MCP_EXTENSION_TOKEN` 需从 Playwright 扩展设置页面获取，通过 `setx` 或系统环境变量设置
- 扩展模式与 `--cdp-endpoint` 模式二选一即可，**本环境推荐使用 `--cdp-endpoint` 模式**（已开远程调试）

### Token 配置

```bash
# 方式一：临时设置（仅当前终端会话有效）
export PLAYWRIGHT_MCP_EXTENSION_TOKEN=your_token_here

# 方式二：永久设置（系统级，重启后生效）
setx PLAYWRIGHT_MCP_EXTENSION_TOKEN your_token_here

# 方式三：写入 PowerShell profile（当前用户永久）
# echo '$env:PLAYWRIGHT_MCP_EXTENSION_TOKEN="your_token_here"' >> $PROFILE
```

## 与 chrome-devtools-mcp 的区别

| 特性 | playwright-mcp | chrome-devtools-mcp |
|------|---------------|-------------------|
| 浏览器引擎 | Playwright 内置 Chromium/Firefox/WebKit | 依赖已安装的 Edge/Chrome |
| 快照方式 | browser_snapshot（无障碍树 Markdown） | take_snapshot（a11y 树 + uid 标识） |
| 元素定位 | `target` 参数（引用快照中的 ref） | `uid` 参数（唯一标识符） |
| 批量表单 | browser_fill_form（字段数组） | fill_form（uid-value 对） |
| 高级功能 | browser_run_code（Playwright API） | Lighthouse 审计、性能追踪、内存快照 |
| 适用场景 | 通用浏览器自动化、表单填写、数据采集 | 前端性能分析、Lighthouse 审计 |

**选择建议**：
- 需要**通用浏览器自动化**（导航、交互、表单、截图） → 优先使用 **playwright-mcp**
- 需要**前端性能分析**（Lighthouse、Core Web Vitals、内存分析） → 使用 **chrome-devtools-mcp**

## 触发条件

- 用户需要自动化浏览器操作（点击、填写、导航等）
- 用户需要网页截图或无障碍快照
- 用户需要批量填写表单
- 用户需要监控网络请求或控制台日志
- 用户需要多标签页管理
- 用户需要执行 Playwright 代码片段
- 用户需要文件上传或拖放操作

## 页面导航工具

### browser_navigate — 导航到 URL

导航到指定 URL，加载页面。

```bash
mcporter call playwright-mcp.browser_navigate url="https://example.com"
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 目标 URL |

**常见场景**: 打开目标网页，每次会话的起始操作。

---

### browser_navigate_back — 返回上一页

在浏览器历史中返回上一页。

```bash
mcporter call playwright-mcp.browser_navigate_back
```

**常见场景**: 页面交互后需要返回上一个页面继续操作。

---

### browser_close — 关闭页面

关闭当前浏览器页面。

```bash
mcporter call playwright-mcp.browser_close
```

**常见场景**: 任务完成后关闭浏览器释放资源。

---

### browser_resize — 调整窗口大小

调整浏览器窗口尺寸。

```bash
mcporter call playwright-mcp.browser_resize width=1920 height=1080
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| width | number | 是 | 窗口宽度（像素） |
| height | number | 是 | 窗口高度（像素） |

**常见场景**: 模拟不同分辨率下的页面布局效果。

---

## 标签页管理

### browser_tabs — 标签页操作

列出、创建、关闭或选择浏览器标签页。

```bash
# 列出所有标签页
mcporter call playwright-mcp.browser_tabs action="list"

# 新建标签页并打开 URL
mcporter call playwright-mcp.browser_tabs action="new" url="https://example.com"

# 选择第 2 个标签页
mcporter call playwright-mcp.browser_tabs action="select" index=1

# 关闭当前标签页
mcporter call playwright-mcp.browser_tabs action="close"

# 关闭第 3 个标签页
mcporter call playwright-mcp.browser_tabs action="close" index=2
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| action | string | 是 | 操作类型：`list`（列出）、`new`（新建）、`close`（关闭）、`select`（选择） |
| index | number | 否 | 标签页索引（用于 close/select），省略时 close 操作关闭当前标签页 |
| url | string | 否 | 新标签页打开的 URL（仅 new 操作） |

**常见场景**: 多标签页之间切换操作，或在新标签页中打开链接。

---

## 页面快照与截图

### browser_snapshot — 无障碍快照（推荐）

捕获当前页面的无障碍树快照，以 Markdown 格式返回。**推荐优先使用 snapshot 进行页面理解，而非 screenshot**。

```bash
# 获取整个页面快照
mcporter call playwright-mcp.browser_snapshot

# 获取指定元素快照
mcporter call playwright-mcp.browser_snapshot target="ref=target-element-ref"

# 限制快照深度并包含元素边界框
mcporter call playwright-mcp.browser_snapshot depth=5 boxes=true

# 保存快照到文件
mcporter call playwright-mcp.browser_snapshot filename="snapshot.md"
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| target | string | 否 | 指定元素的选择器或快照引用 |
| filename | string | 否 | 保存快照到指定 Markdown 文件 |
| depth | number | 否 | 限制快照树的深度 |
| boxes | boolean | 否 | 是否包含每个元素的边界框 `[box=x,y,width,height]` |

**常见场景**: 了解页面结构、定位交互目标。快照返回的 `ref` 值用于后续 click、fill 等操作的 `target` 参数。每次页面变化后应重新获取快照。

---

### browser_take_screenshot — 页面截图

对当前页面或指定元素进行截图。

```bash
# 截取当前视口
mcporter call playwright-mcp.browser_take_screenshot type="png"

# 截取完整页面（含滚动区域）
mcporter call playwright-mcp.browser_take_screenshot type="png" fullPage=true

# 截取指定元素
mcporter call playwright-mcp.browser_take_screenshot element="登录按钮" target="ref=btn-login" type="png"

# 保存到指定文件名
mcporter call playwright-mcp.browser_take_screenshot type="jpeg" filename="screenshot.jpg"
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| element | string | 否 | 人类可读的元素描述 |
| target | string | 否 | 快照中的元素引用或 CSS 选择器 |
| type | string | 是 | 图片格式：`png`（默认）或 `jpeg` |
| filename | string | 否 | 保存文件名，默认 `page-{timestamp}.{png\|jpeg}` |
| fullPage | boolean | 否 | 是否截取完整滚动页面（不能与元素截图同时使用） |

**常见场景**: 需要视觉确认页面状态，或保存截图作为交付物。

---

## 元素交互工具

### browser_click — 点击元素

点击页面上的指定元素。

```bash
# 单击
mcporter call playwright-mcp.browser_click element="搜索按钮" target="ref=search-btn"

# 双击
mcporter call playwright-mcp.browser_click target="ref=text-item" doubleClick=true

# 右键点击
mcporter call playwright-mcp.browser_click target="ref=context-target" button="right"

# 带修饰键点击（Ctrl+点击）
mcporter call playwright-mcp.browser_click target="ref=link" modifiers="Control"
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| element | string | 否 | 人类可读的元素描述 |
| target | string | 是 | 快照中的元素引用或 CSS 选择器 |
| doubleClick | boolean | 否 | 是否双击，默认 false |
| button | string | 否 | 鼠标按钮：`left`（默认）、`right`、`middle` |
| modifiers | string | 否 | 修饰键：`Alt`、`Control`、`ControlOrMeta`、`Meta`、`Shift` |

**常见场景**: 点击按钮、链接、菜单项等交互元素。

---

### browser_type — 键盘输入

向可编辑元素输入文本。

```bash
# 基本输入
mcporter call playwright-mcp.browser_type element="用户名输入框" target="ref=username" text="hello"

# 输入后按回车提交
mcporter call playwright-mcp.browser_type target="ref=search-input" text="关键词" submit=true

# 逐字符输入（触发 keydown/keypress 事件）
mcporter call playwright-mcp.browser_type target="ref=phone-input" text="13800138000" slowly=true
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| element | string | 否 | 人类可读的元素描述 |
| target | string | 是 | 快照中的元素引用或 CSS 选择器 |
| text | string | 是 | 要输入的文本 |
| submit | boolean | 否 | 输入后按回车提交，默认 false |
| slowly | boolean | 否 | 逐字符输入（触发 key handlers），默认 false（整段填入） |

**常见场景**: 填写输入框、搜索框等。需要逐字符触发事件时使用 `slowly=true`。

---

### browser_press_key — 按键操作

按下键盘按键。

```bash
# 按回车
mcporter call playwright-mcp.browser_press_key key="Enter"

# 按 Escape 关闭弹窗
mcporter call playwright-mcp.browser_press_key key="Escape"

# 按 Tab 切换焦点
mcporter call playwright-mcp.browser_press_key key="Tab"

# 按方向键
mcporter call playwright-mcp.browser_press_key key="ArrowDown"
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| key | string | 是 | 按键名称，如 `ArrowLeft`、`Enter`、`Escape`、`Tab`、`a` |

**常见场景**: 按回车提交、按 Escape 关闭弹窗、Tab 切换焦点等快捷键操作。

---

### browser_hover — 鼠标悬停

将鼠标悬停在指定元素上。

```bash
mcporter call playwright-mcp.browser_hover element="导航菜单" target="ref=nav-menu"
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| element | string | 否 | 人类可读的元素描述 |
| target | string | 是 | 快照中的元素引用或 CSS 选择器 |

**常见场景**: 触发下拉菜单、工具提示等悬停效果。

---

### browser_select_option — 选择下拉选项

在 `<select>` 下拉框中选择选项。

```bash
# 单选
mcporter call playwright-mcp.browser_select_option element="国家选择" target="ref=country-select" values="China"

# 多选
mcporter call playwright-mcp.browser_select_option target="ref=tags-select" values="tag1,tag2,tag3"
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| element | string | 否 | 人类可读的元素描述 |
| target | string | 是 | 快照中的元素引用或 CSS 选择器 |
| values | string[] | 是 | 要选择的值（单值或多值数组） |

**常见场景**: 选择下拉列表中的选项。多个值用逗号分隔。

---

### browser_drag — 拖拽操作

将元素拖拽到目标位置。

```bash
mcporter call playwright-mcp.browser_drag startElement="待办事项" startTarget="ref=item-1" endElement="完成列表" endTarget="ref=done-list"
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| startElement | string | 否 | 源元素的人类可读描述 |
| startTarget | string | 是 | 源元素的快照引用或选择器 |
| endElement | string | 否 | 目标元素的人类可读描述 |
| endTarget | string | 是 | 目标元素的快照引用或选择器 |

**常见场景**: 拖拽排序、拖放元素到目标区域。

---

### browser_drop — 拖放文件/数据

将文件或 MIME 数据拖放到指定元素上，模拟从页面外部拖入。

```bash
# 拖放本地文件
mcporter call playwright-mcp.browser_drop target="ref=upload-zone" paths="C:/path/to/file.pdf"

# 拖放 MIME 数据
mcporter call playwright-mcp.browser_drop target="ref=drop-area" data='{"text/plain": "hello", "text/uri-list": "https://example.com"}'
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| element | string | 否 | 目标元素的人类可读描述 |
| target | string | 是 | 目标元素的快照引用或选择器 |
| paths | string[] | 否 | 要拖放的本地文件绝对路径（与 data 至少提供一个） |
| data | object | 否 | MIME 类型到值的映射，如 `{"text/plain": "hello"}`（与 paths 至少提供一个） |

**常见场景**: 向拖放上传区域拖入文件或数据。

---

## 表单工具

### browser_fill_form — 批量填写表单

一次性填写多个表单字段。

```bash
mcporter call playwright-mcp.browser_fill_form --args '{"fields": [
  {"name": "用户名", "type": "textbox", "value": "张三", "target": "ref=username"},
  {"name": "邮箱", "type": "textbox", "value": "zhangsan@email.com", "target": "ref=email"},
  {"name": "性别", "type": "radio", "value": "male", "target": "ref=gender-male"},
  {"name": "国家", "type": "combobox", "value": "中国", "target": "ref=country"},
  {"name": "同意协议", "type": "checkbox", "value": "true", "target": "ref=agree"}
]}'
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| fields | array | 是 | 字段数组，每项包含以下属性 |

**fields 子项属性**：

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| target | string | 是 | 字段元素的快照引用或选择器 |
| name | string | 是 | 字段的人类可读名称 |
| type | string | 是 | 字段类型：`textbox`、`checkbox`、`radio`、`combobox`、`slider` |
| value | string | 是 | 填入值。checkbox 为 `true`/`false`，combobox 为选项文本 |

**常见场景**: 批量填写登录表单、注册表单、搜索条件等多字段表单，一次调用完成所有填写。

---

### browser_file_upload — 上传文件

通过文件选择器上传一个或多个文件。

```bash
# 上传单个文件
mcporter call playwright-mcp.browser_file_upload paths="C:/path/to/file.pdf"

# 上传多个文件
mcporter call playwright-mcp.browser_file_upload --args '{"paths": ["C:/file1.pdf", "C:/file2.png"]}'

# 取消文件选择
mcporter call playwright-mcp.browser_file_upload
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| paths | string[] | 否 | 文件绝对路径数组，省略则取消文件选择 |

**常见场景**: 自动化文件上传操作。需先触发文件选择对话框，然后调用此工具。

---

### browser_handle_dialog — 处理对话框

处理浏览器弹出的 alert、confirm、prompt 对话框。

```bash
# 接受确认对话框
mcporter call playwright-mcp.browser_handle_dialog accept=true

# 拒绝确认对话框
mcporter call playwright-mcp.browser_handle_dialog accept=false

# 回复 prompt 对话框
mcporter call playwright-mcp.browser_handle_dialog accept=true promptText="输入的内容"
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| accept | boolean | 是 | 是否接受对话框 |
| promptText | string | 否 | 对 prompt 类型对话框的回复文本 |

**常见场景**: 页面弹出确认对话框时自动接受或拒绝。

---

## JavaScript 执行

### browser_evaluate — 执行 JavaScript

在当前页面或指定元素上执行 JavaScript 表达式。

```bash
# 在页面上执行
mcporter call playwright-mcp.browser_evaluate function="() => { return document.title }"

# 在指定元素上执行
mcporter call playwright-mcp.browser_evaluate element="价格元素" target="ref=price" function="(el) => { return el.textContent }"

# 保存结果到文件
mcporter call playwright-mcp.browser_evaluate function="() => { return JSON.stringify(Array.from(document.querySelectorAll('a')).map(a => ({text: a.innerText, href: a.href}))) }" filename="links.json"
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| element | string | 否 | 元素的人类可读描述 |
| target | string | 否 | 元素的快照引用或选择器 |
| function | string | 是 | JavaScript 函数：`() => { code }` 或 `(element) => { code }`（提供 element 时） |
| filename | string | 否 | 保存结果到指定文件 |

**常见场景**: 提取页面数据、修改 DOM、执行自定义逻辑。

---

### browser_run_code — 执行 Playwright 代码

运行 Playwright API 代码片段，拥有完整的 Playwright `page` 对象访问权限。

```bash
# 执行 Playwright 代码
mcporter call playwright-mcp.browser_run_code --args '{"code": "async (page) => { await page.getByRole(\"button\", { name: \"Submit\" }).click(); return await page.title(); }"}'

# 从文件加载代码
mcporter call playwright-mcp.browser_run_code filename="script.js"
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 否 | Playwright 代码，函数签名 `async (page) => { ... }` |
| filename | string | 否 | 从文件加载代码（与 code 同时提供时，code 被忽略） |

**常见场景**: 执行复杂的浏览器操作，超出基础工具能力的场景（如等待特定网络请求、处理 iframe、操作 Shadow DOM 等）。

---

## 调试工具

### browser_console_messages — 获取控制台日志

获取页面的控制台消息。

```bash
# 获取 info 级别及以上的消息
mcporter call playwright-mcp.browser_console_messages level="info"

# 获取 error 级别消息
mcporter call playwright-mcp.browser_console_messages level="error"

# 获取自会话开始以来的所有消息
mcporter call playwright-mcp.browser_console_messages level="debug" all=true

# 保存到文件
mcporter call playwright-mcp.browser_console_messages level="warning" filename="console.log"
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| level | string | 是 | 日志级别：`error` < `warning` < `info` < `debug`，每个级别包含更严重的级别 |
| all | boolean | 否 | 是否返回自会话开始以来的所有消息（而非仅上次导航后），默认 false |
| filename | string | 否 | 保存到指定文件，省略则返回文本 |

**常见场景**: 检查页面 JavaScript 错误、调试前端问题。

---

### browser_network_requests — 获取网络请求

获取页面加载以来的网络请求列表。

```bash
# 仅获取非静态资源请求（API 请求等）
mcporter call playwright-mcp.browser_network_requests static=false requestBody=false requestHeaders=false

# 获取完整请求详情（含请求体和请求头）
mcporter call playwright-mcp.browser_network_requests static=false requestBody=true requestHeaders=true

# 按正则过滤请求
mcporter call playwright-mcp.browser_network_requests static=false requestBody=true requestHeaders=false filter="/api/.*user"

# 保存到文件
mcporter call playwright-mcp.browser_network_requests static=false requestBody=true requestHeaders=false filename="requests.log"
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| static | boolean | 是 | 是否包含静态资源（图片、字体、脚本等），默认 false |
| requestBody | boolean | 是 | 是否包含请求体，默认 false |
| requestHeaders | boolean | 是 | 是否包含请求头，默认 false |
| filter | string | 否 | 正则过滤，仅返回 URL 匹配的请求，如 `/api/.*user` |
| filename | string | 否 | 保存到指定文件 |

**常见场景**: 分析 API 请求、检查接口参数和响应、调试网络问题。

---

## 等待工具

### browser_wait_for — 等待条件

等待文本出现/消失，或等待指定时间。

```bash
# 等待文本出现
mcporter call playwright-mcp.browser_wait_for text="加载完成"

# 等待文本消失
mcporter call playwright-mcp.browser_wait_for textGone="加载中..."

# 等待 3 秒
mcporter call playwright-mcp.browser_wait_for time=3
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| time | number | 否 | 等待时间（秒） |
| text | string | 否 | 等待出现的文本 |
| textGone | string | 否 | 等待消失的文本 |

**常见场景**: 页面加载或 AJAX 请求完成后等待特定内容出现/消失，或简单的延时等待。

---

## 典型工作流

### 工作流 1：网页数据采集
1. `browser_navigate` — 打开目标网页
2. `browser_snapshot` — 获取页面快照，定位目标元素
3. `browser_click` — 交互（翻页、展开等）
4. `browser_evaluate` — 提取数据
5. `browser_close` — 关闭页面

### 工作流 2：表单自动填写与提交
1. `browser_navigate` — 打开表单页面
2. `browser_snapshot` — 获取表单字段的引用
3. `browser_fill_form` — 批量填写所有字段
4. `browser_click` — 点击提交按钮
5. `browser_wait_for` — 等待成功提示出现

### 工作流 3：多标签页数据采集
1. `browser_navigate` — 打开列表页
2. `browser_snapshot` — 获取链接列表
3. `browser_tabs action="new" url="..."` — 新标签页打开详情
4. `browser_evaluate` — 提取详情页数据
5. `browser_tabs action="select" index=0` — 切回列表页
6. `browser_navigate_back` 或重复操作

### 工作流 4：文件上传自动化
1. `browser_navigate` — 打开上传页面
2. `browser_snapshot` — 定位上传按钮
3. `browser_click` — 触发文件选择对话框
4. `browser_file_upload` — 选择文件上传

### 工作流 5：网络请求监控
1. `browser_navigate` — 打开目标页面
2. `browser_network_requests` — 查看所有 API 请求
3. `browser_network_requests filter="/api/.*" requestBody=true` — 过滤并查看请求详情
4. `browser_console_messages level="error"` — 检查是否有错误

## 注意事项

- `browser_snapshot` 是页面理解的首选工具，返回的元素引用用于后续交互的 `target` 参数
- `browser_take_screenshot` 用于视觉确认，**不能**用于定位交互目标
- `element` 参数为人类可读描述，用于记录操作意图；`target` 参数为实际定位引用
- 复杂操作优先使用 `browser_run_code` 直接调用 Playwright API
- `browser_fill_form` 适用于批量表单填写，单个字段可用 `browser_type`
