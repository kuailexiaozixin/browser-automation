---
name: 微信公众号文章自动化读取受限
summary: mp.weixin.qq.com 文章在本环境多种方式读取均返回空壳页，需登录态或网络放行；hermes browser 后端判定
tags: [微信公众号, 反爬, 空壳页, hermes, browser-use, agent-browser]
noteTypes: [operator]
---

## 目标
读取 https://mp.weixin.qq.com/s/YDjVJlzN-fPC-_kfJ27Dzw 并判定 hermes 浏览器后端。

## 结果
微信文章读取失败（均返回空壳页/空白）：
- requests/curl：http_code=000（网络层阻断）
- CDP 直连 Edge：调试会话连接超时
- hermes web_extract：Content was inaccessible or not found
- playwright-cli 扩展模式：页面 title=微信公众平台，bodyLen=0（无登录态/反爬空壳）

## 已知要点
- 本环境访问 mp.weixin.qq.com 文章受限（网络层 + 反爬双重），需用户微信登录态或网络放行。
- hermes browser 后端判定：`tools/browser_tool.py` 用 **agent-browser CLI**（本地默认）；browser-use 仅是云端 provider（需 `browser.cloud_provider: browser-use` 显式配置）。

## 补充：成功读取路径（playwright-cli 扩展模式）
- `npx playwright cli --s=msedge goto <url> --timeout 45000` 会**超时**，但**不要因此放弃**，超时后页面实际已渲染。
- 直接 `npx playwright cli --s=msedge eval "()=>{var t=document.querySelector('#js_content')||document.body; return JSON.stringify({title:(document.querySelector('#activity-name')||{}).innerText, len:t.innerText.length, text:t.innerText.slice(0,7000)});}"` 即可取到正文。
- 之前读取失败是**加载时机/等待策略**问题（等待 domcontentloaded 超时），非真正无法访问。URL 正确、title 显示"微信公众平台"时，直接 eval 提取正文即可。

## 文章要点（hermes Browser Use mode）
- 文章《Hermes 把 12 个浏览器工具砍成 1 个》：Hermes 新 Browser Use mode 由 @browser_use CLI 3.0 驱动，把 12 个细粒度 browser_* 工具合并成 1 个 browser_exec，token 省 48-66%。
- 启用配置：`browser:\n  backend: "browser-use"`。
- **当前 example01 未配置该 backend**，运行内核不支持 browser.backend，工具面 MCP 暴露的仍是细粒度 browser_*（9 个）→ 非 browser-use CLI，走本地 agent-browser/CDP。
