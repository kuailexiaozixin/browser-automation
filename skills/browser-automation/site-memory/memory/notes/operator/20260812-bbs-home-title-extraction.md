---
name: bbs.wps.cn首页帖子标题提取（playwright-cli与playwright-mcp）
summary: 用 playwright-cli 与 playwright-mcp 两个子技能打开 bbs.wps.cn 提取首页帖子标题的完整可重放流程
tags: [playwright-cli, playwright-mcp, bbs.wps.cn, 标题提取, mcporter]
noteTypes: [operator]
---

## 目标
用 browser-automation 下的 playwright-cli 与 playwright-mcp 两个子技能，打开 bbs.wps.cn 首页并提取帖子标题列表。

## 前置条件
- 本地 Edge 已开启 CDP 远程调试（端口与 WebSocket 路径从 `%LOCALAPPDATA%\Microsoft\Edge\User Data\DevToolsActivePort` 读取两行）。
- playwright-cli 未全局安装，通过 `npx playwright cli` 调用（本机 1.62.1）。

## 操作步骤

### playwright-cli
1. 连接已运行 Edge：`npx playwright cli attach --cdp=msedge`（按通道名自动发现）。
2. 导航：`npx playwright cli --s=msedge goto https://bbs.wps.cn`。
3. 提取标题：`npx playwright cli --s=msedge eval "() => { const t=[]; document.querySelectorAll('a').forEach(a=>{const tx=(a.innerText||'').trim(); if(tx&&tx.length>4&&a.href.includes('/topic/')) t.push({title:tx,href:a.href});}); return JSON.stringify(t.slice(0,30),null,2); }"`。
4. 会话默认名为 `msedge`，后续命令用 `--s=msedge` 指定。

### playwright-mcp
1. 在项目 `config/mcporter.json` 注册 stdio server（关键：用 `--cdp-endpoint=ws://...` 连接 Edge，不能默认启动内置浏览器）：
   ```json
   {"mcpServers":{"playwright-mcp":{"command":"npx","args":["@playwright/mcp@latest","--cdp-endpoint=ws://127.0.0.1:<port>/devtools/browser/<uuid>"]}}}
   ```
2. 调用需用 `--args` 传 JSON（直接 `'{"action":"list"}'` 位置参数会报参数校验错误），且加 `--timeout 60000`。
3. 列标签页：`mcporter call playwright-mcp.browser_tabs --args '{"action":"list"}' --timeout 60000`。
4. 导航：`mcporter call playwright-mcp.browser_navigate --args '{"url":"https://bbs.wps.cn"}' --timeout 60000`。
5. 提取标题：`mcporter call playwright-mcp.browser_evaluate --args '{"function":"...JS..."}' --timeout 60000`（function 内双引号需转义 `\"`）。

## 已知要点
- 服务名：本地注册后为 `playwright-mcp`；mcp.json 里的 gallery 配置为 `microsoft/playwright-mcp`（HTTP 探测会失败），需改用本地 stdio 注册。
- playwright-mcp 的 `--cdp-endpoint` 不要带 `--headless`（会超时 `Timeout 30000ms exceeded`）。
- 标题筛选条件：`<a>` 文本长度 >4 且 href 含 `/topic/`；取前 30 条。
- 操作完毕不得关闭 Edge；playwright-cli 用 detach，playwright-mcp 断开连接即可。
