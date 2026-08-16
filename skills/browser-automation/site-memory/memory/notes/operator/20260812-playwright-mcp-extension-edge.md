---
name: playwright-mcp扩展模式连接Edge
summary: playwright-mcp 用 --extension 扩展模式连接 Edge 打开 bbs.wps.cn 的完整可重放流程（关键：需指定 Edge 路径）
tags: [playwright-mcp, extension, 扩展模式, Edge, bbs.wps.cn]
noteTypes: [operator]
---

## 目标
用 playwright-mcp 的浏览器扩展模式（--extension）连接运行中的 Edge，打开 bbs.wps.cn 并提取首页帖子标题。

## 前置条件
- Edge 已安装 Playwright 扩展（ID：`mmlmfjhmonkocbjadbfplnigmagldckm`）。
- 环境变量 `PLAYWRIGHT_MCP_EXTENSION_TOKEN` 已设置（从扩展设置页面获取）。
- 扩展模式无需 CDP，通过扩展转发控制浏览器。

## 操作步骤
1. 在项目 `config/mcporter.json` 注册 playwright-mcp，**必须显式指定 Edge 路径**：
   ```json
   {"mcpServers":{"playwright-mcp":{"command":"npx","args":[
     "@playwright/mcp@latest",
     "--extension",
     "--executable-path=C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
     "--user-data-dir=C:\\Users\\贺新\\AppData\\Local\\Microsoft\\Edge\\User Data",
     "--headless"]}}}
   ```
2. 验证连接：`mcporter call playwright-mcp.browser_tabs --args '{"action":"list"}' --timeout 60000`（应看到扩展欢迎页 connect.html）。
3. 导航：`mcporter call playwright-mcp.browser_navigate --args '{"url":"https://bbs.wps.cn"}' --timeout 60000`。
4. 提取标题：`mcporter call playwright-mcp.browser_evaluate --args '{"function":"...JS..."}' --timeout 60000`（JS 内双引号转义 `\"`）。

## 已知要点
- **若不加 `--executable-path`/`--user-data-dir`**，扩展模式默认找 `C:\Users\...\Google\Chrome\User Data`，报错 `Playwright Extension not found in ...Chrome\User Data`。必须指向 Edge。
- `--user-data-dir` 必须指向 Edge 的 User Data（内含已装的 Playwright 扩展）。
- 调用统一用 `--args` 传 JSON + `--timeout 60000`（与任务 1 的 CDP 模式一致）。
- 标题筛选：`<a>` 文本长度 >4 且 href 含 `/topic/`，取前 30 条。
- 操作完毕不得关闭 Edge。
