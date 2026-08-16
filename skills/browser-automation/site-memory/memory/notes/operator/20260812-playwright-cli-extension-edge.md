---
name: playwright-cli扩展模式连接Edge
summary: playwright-cli 用 attach --extension 扩展模式连接 Edge 打开 bbs.wps.cn 提取首页帖子标题的完整流程
tags: [playwright-cli, extension, 扩展模式, Edge, bbs.wps.cn]
noteTypes: [operator]
---

## 目标
用 playwright-cli 的扩展模式（attach --extension）连接运行中的 Edge，打开 bbs.wps.cn 并提取首页帖子标题。

## 前置条件
- Edge 已安装 Playwright 扩展（ID：`mmlmfjhmonkocbjadbfplnigmagldckm`）。
- 环境变量 `PLAYWRIGHT_MCP_EXTENSION_TOKEN` 已设置。
- 扩展模式无需 CDP，通过扩展转发控制浏览器。

## 操作步骤
1. 连接：`npx playwright cli attach --extension=msedge`（按浏览器通道名自动识别 Edge，**无需显式指定可执行路径/User Data**，比 playwright-mcp 简洁）。
2. 导航：`npx playwright cli --s=msedge goto https://bbs.wps.cn`。
3. 提取标题：`npx playwright cli --s=msedge eval "() => { const t=[]; document.querySelectorAll('a').forEach(a=>{const tx=(a.innerText||'').trim(); if(tx&&tx.length>4&&a.href.includes('/topic/')) t.push({title:tx,href:a.href});}); return JSON.stringify(t.slice(0,30),null,2); }"`。
4. 会话默认名为 `msedge`，后续命令用 `--s=msedge` 指定。

## 已知要点
- `attach --extension=msedge` 连接后当前页为扩展欢迎页 connect.html（含 mcpRelayUrl 与 token），属正常。
- 标题筛选：`<a>` 文本长度 >4 且 href 含 `/topic/`，取前 30 条。
- 操作完毕不得关闭 Edge。
