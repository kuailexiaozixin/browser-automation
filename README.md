# browser-automation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/kuailexiaozixin/browser-automation)](https://github.com/kuailexiaozixin/browser-automation/releases)
[![GitHub stars](https://img.shields.io/github/stars/kuailexiaozixin/browser-automation)](https://github.com/kuailexiaozixin/browser-automation)
[![GitHub issues](https://img.shields.io/github/issues/kuailexiaozixin/browser-automation)](https://github.com/kuailexiaozixin/browser-automation/issues)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-ready-blueviolet)](https://agentskills.io)

浏览器自动化**综合技能集**（Agent Skill），聚合多套浏览器驱动、网页抓取与自动化方案，供 AI 代理在会话中通过 `skill` 工具加载使用。覆盖 **CDP 直连控制、Playwright / Chrome DevTools MCP、反爬抓取、站点记忆与网页任务工作流**等场景。

支持 AgentSkills 标准的助手（Claude Code、Codex、WPS 灵犀、DeepSeek Harness 等）可原生加载。

---

## ✨ 特性

- **多方案聚合**：一个技能集覆盖 4 类浏览器自动化技术栈（CDP 直连、Playwright、DevTools 协议、抓取框架），按需选用
- **CDP 直连**：`agent-browser` / `browser-harness` / `browser-use` 无需 Playwright/Puppeteer，快照式交互仅需 200-400 token
- **调试优化**：Chrome DevTools MCP 子技能集覆盖可访问性审计、LCP 优化、内存泄漏排查、疑难排障
- **反爬抓取**：Scrapling 支持静态/动态/无头/反爬绕过（如 Cloudflare Turnstile），含 Spider 框架
- **跨会话记忆**：`site-memory` 为浏览器自动化提供持久上下文保持
- **代码即动作**：`webwright` 让 AI 直接编写 Playwright 代码驱动网页任务

## 📦 子技能模块

| 模块 | 说明 |
|------|------|
| [`agent-browser`](skills/browser-automation/agent-browser/) | 面向 AI 代理的高效浏览器自动化 CLI（CDP 直连，快照式交互） |
| [`browser-harness`](skills/browser-automation/browser-harness/) | 极简自愈式浏览器套件（CDP）+ 领域技能工作区（domain-skills） |
| [`browser-use`](skills/browser-automation/browser-use/) | 基于 CDP 的直接浏览器控制，用于交互、抓取、测试 |
| [`Chrome-DevTools-MCP`](skills/browser-automation/Chrome-DevTools-MCP/) | Chrome DevTools 协议 MCP 调试子技能集 |
| [`playwright-cli`](skills/browser-automation/playwright-cli/) | Playwright 驱动的浏览器交互与网页测试 CLI |
| [`playwright-mcp`](skills/browser-automation/playwright-mcp/) | Playwright MCP 服务（STDIO，`@playwright/mcp`） |
| [`scrapling`](skills/browser-automation/scrapling/) | 网页抓取（静态/动态/无头/反爬绕过），含 Spider 框架 |
| [`webwright`](skills/browser-automation/webwright/) | 代码即动作（code-as-action）的网页任务工作流 |
| [`site-memory`](skills/browser-automation/site-memory/) | 站点记忆子系统，跨会话上下文保持 |

## 🚀 快速开始

本仓库以 **Agent Skill** 形式分发，支持 AgentSkills 标准的助手可直接读取加载。

### 方式一：AgentSkills 助手直接加载

```bash
# Claude Code
/plugin marketplace add kuailexiaozixin/browser-automation
```

### 方式二：从 GitHub Release 下载（本地技能目录）

```bash
# 下载源码归档（zip 或 tar.gz）
curl -L -o browser-automation.zip \
  https://github.com/kuailexiaozixin/browser-automation/archive/refs/tags/v0.1.0.zip
unzip browser-automation.zip

# 放入技能发现目录（dsh / 灵犀等）
mkdir -p ~/.dsh/skills
mv browser-automation-0.1.0 ~/.dsh/skills/browser-automation
# 重启后即可通过 skill 工具加载
```

> 用户技能目录默认 `<dshHome>/skills`，Windows 下为 `C:\Users\<用户名>\.dsh\skills\`。

## 📁 目录结构

```
browser-automation/
├── SKILL.md                    # 技能入口（总路由）
├── agent-browser/              # 浏览器自动化 CLI 技能
├── browser-harness/            # 自愈式浏览器套件 + 领域工作区
├── browser-use/                # CDP 直接控制
├── Chrome-DevTools-MCP/        # DevTools 调试子技能集
├── playwright-cli/             # Playwright CLI 技能
├── playwright-mcp/             # Playwright MCP 技能
├── Scrapling/                  # 网页抓取框架
├── webwright/                  # 网页任务工作流
├── site-memory/                # 站点记忆子系统
├── README.md                   # 本文档
└── LICENSE                     # MIT 许可证
```

## 🧰 使用示例

加载技能后，直接对 AI 代理描述任务即可。例如：

```text
用 browser-automation 的 agent-browser，打开 https://example.com，
提取页面上所有文章的标题，并截图保存。
```

```text
用 Scrapling 抓取这个页面，绕过 Cloudflare 验证，把结果存成 CSV。
```

```text
用 playwright-mcp 自动化：登录、填写表单、点击提交，等待结果页出现。
```

各子模块的详细命令与用法见对应子目录的 `SKILL.md`。

## ❓ FAQ

**Q：为什么有多个浏览器自动化模块？如何选择？**
A：不同场景技术栈不同——CDP 直连（agent-browser/harness/browser-use）轻量快速，适合一般网页交互；Playwright 生态成熟，适合测试与复杂流程；DevTools MCP 面向调试优化；Scrapling 擅长反爬抓取。按任务在 `SKILL.md` 中路由。

**Q：支持哪些助手？**
A：支持 AgentSkills 标准的助手均可原生加载；也支持通过本地技能目录放入 dsh、WPS 灵犀等。

**Q：`site-memory` 的笔记会随仓库分发吗？**
A：不会。`site-memory/memory/` 个人记忆数据已在 `.gitignore` 中排除，不进入发布包。

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

## 📄 许可证

本仓库聚合与编排结构采用 **MIT License**（见 [LICENSE](LICENSE)）。各子技能模块收载的第三方开源代码分别遵循各自上游许可证（见「第三方开源项目引用」），使用时请一并遵守。

## 🤝 贡献与反馈

欢迎通过 [Issues](https://github.com/kuailexiaozixin/browser-automation/issues) 反馈问题或建议，通过 [Pull Requests](https://github.com/kuailexiaozixin/browser-automation/pulls) 贡献代码。
