# browser-automation

浏览器自动化综合技能集（Agent Skill），聚合多套浏览器驱动、网页抓取与自动化方案，供 AI 代理在会话中通过 `skill` 工具加载使用。覆盖 CDP 直连控制、Playwright/Chrome DevTools MCP、反爬抓取、站点记忆与网页任务工作流等场景。

## 子技能模块

| 模块 | 说明 |
|------|------|
| `agent-browser` | 面向 AI 代理的高效浏览器自动化 CLI（CDP 直连，无 Playwright/Puppeteer 依赖，快照式交互） |
| `browser-harness` | 极简自愈式浏览器套件（CDP），含领域技能工作区（domain-skills） |
| `browser-use` | 基于 CDP 的直接浏览器控制，用于交互、抓取、测试与站点/应用工作 |
| `Chrome-DevTools-MCP` | Chrome DevTools 协议 MCP 调试子技能集（可访问性、LCP 优化、内存泄漏、排障） |
| `playwright-cli` | Playwright 驱动的浏览器交互与网页测试 CLI |
| `playwright-mcp` | Playwright MCP 服务（STDIO，`@playwright/mcp`） |
| `Scrapling` | 网页抓取（静态/动态/无头/反爬绕过），含 Spider 框架 |
| `webwright` | 代码即动作（code-as-action）的网页任务工作流（Microsoft Webwright） |
| `site-memory` | 站点记忆子系统，为浏览器自动化提供跨会话上下文保持 |

## 安装与使用

本仓库以 **Agent Skill** 形式分发，支持 AgentSkills 标准的助手（Claude Code、Codex、WPS 灵犀、DeepSeek Harness 等）原生读取加载。

**以支持 AgentSkills 的助手为例：**

```bash
# Claude Code
/plugin marketplace add kuailexiaozixin/browser-automation
```

**从 GitHub Release 下载安装（dsh / 灵犀等本地技能目录）：**

```bash
curl -L -o browser-automation.zip \
  https://github.com/kuailexiaozixin/browser-automation/archive/refs/tags/v0.1.0.zip
unzip browser-automation.zip
mkdir -p ~/.dsh/skills
mv browser-automation-0.1.0 ~/.dsh/skills/browser-automation
# 重启 dsh 后即可通过 skill 工具加载
```

> 用户技能目录默认 `<dshHome>/skills`，Windows 下为 `C:\Users\<用户名>\.dsh\skills\`。

各子模块的具体安装与调用方式见对应子目录的 `SKILL.md`。

## 第三方开源项目引用

本技能集收载、适配并引用了以下开源项目，尊重并保留其原始版权与许可证声明（许可证全文见各子目录对应文件，以各上游仓库为准）：

| 开源项目 | 组织/作者 | 许可证 | 上游仓库 |
|---------|----------|--------|---------|
| Browser Harness | Browser Use | MIT | [browser-use/browser-harness](https://github.com/browser-use/browser-harness) |
| Browser Use | Browser Use | MIT | [browser-use/browser-use](https://github.com/browser-use/browser-use) |
| Scrapling | D4Vinci (Karim shoair) | BSD-3-Clause | [D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling) |
| Chrome DevTools MCP | Google ChromeDevTools | Apache-2.0 | [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) |
| Playwright / MCP | Microsoft | Apache-2.0 | [microsoft/playwright](https://github.com/microsoft/playwright) |
| Webwright | Microsoft Research | 开源（以官方仓库为准） | [microsoft/webwright](https://github.com/microsoft/webwright) |
| react-devtools hook（agent-browser 内置） | Meta (facebook/react) | MIT | [facebook/react](https://github.com/facebook/react) |

> 说明：
> - 各子模块为独立技能包，其代码与内容分别遵循各自上游许可证（详见对应子目录 `LICENSE*` 与上游仓库）。
> - `site-memory`、`webwright` 适配层、`browser-harness` 领域工作区（domain-skills）等为基于上游项目的整理/适配产物。
> - 本仓库的聚合与整理结构（SKILL.md 编排、目录组织）为原创内容；如整体再分发，请同时遵守各上游项目的许可证条款。

## 贡献与反馈

欢迎通过 [Issues](https://github.com/kuailexiaozixin/browser-automation/issues) 反馈问题或建议。
