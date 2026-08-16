---
name: 灵犀专业版界面一比一复刻流程
summary: 依据 lingxi.cn/docs 文档一比一复刻灵犀专业版界面与功能，完整流程：静态文档抓取 → 设计系统提取 → Web 应用构建 → 逻辑测试
tags: [灵犀, Lingxi, 界面复刻, 静态抓取, Web应用, 设计系统]
noteTypes: [operator]
---

# 目标
依据 https://www.lingxi.cn/docs 文档一比一复刻灵犀专业版（Lingxi Pro）的界面和功能，构建完整 Web 应用。

# 前置条件
- Python requests 可用（页面为 Astro 静态 SSR，无需 JS 渲染）
- Node.js 可用（语法验证、逻辑测试）
- 灵犀设计系统 token 已从官方 CSS 提取

# 操作步骤

## 阶段一：静态文档抓取（无浏览器）
1. requests.get("https://www.lingxi.cn/docs") 返回 200，76832 字节，为 Astro 静态站
2. **编码坑**：PowerShell 控制台显示 UTF-8 中文乱码，必须将 HTML/结果写入 UTF-8 文件后用 read 工具读取
3. 用正则提取 article 结构：每个 <article id="XX-xxx"> 含 data-heading-map 属性和 docs-section-content 正文
4. 分别保存 6 个章节到独立 txt：01-getting-started / 04-core-capabilities / 05-modes / 06-credits / 07-best-practices / 09-changelog

## 阶段二：设计系统提取
从 BaseLayout.Di1BI6NV.css 提取关键 token：
- lx 色板：coral #ee4565 / magenta #b22dca / violet #7f57eb / blue #3e7ae4 / teal #379eb4 / mint #4aa99b / amber #d5950c
- primary: #1e5fc7, hover #1a51ab
- 深色主题：paper #05050c / text #f2f0ea / dim #8a877f
- 浅色主题：paper #fff / text #14131a / dim #6b685f
- 字体：font-sans "Noto Sans SC", "Manrope"；font-brand "SF Pro Display"
- 特色元素：grain 噪点纹理、cursor-dot/cursor-ring 光标、lx-spectrum-conic 频谱光球、fluid-ball 特效

## 阶段三：Web 应用构建（D:/WPS灵犀过程文件/lingxi-pro-replica/）
- index.html：左侧会话栏（项目分组+对话列表+用户卡片）、中间对话区（标题栏+消息+输入框）、右侧执行步骤面板、设置/项目/模型/授权弹窗
- css/styles.css：完整设计系统，深浅双主题，全部组件样式
- js/app.js：数据模型（projects/sessions/memoryCore/memoryKnowledge/schedules/skills/datasources）+ 模拟回复引擎 + 执行步骤动画 + 设置面板渲染
- assets/img/logo.svg：频谱渐变 logo

## 阶段四：验证
1. node --check 验证 JS 语法
2. python -m http.server 8234 启动本地服务，requests 验证所有资源 200
3. **DOM shim 逻辑测试**：Node 中伪造 DOM 环境（FakeElement + localStorage + matchMedia），eval 加载 app.js 后测试 26 项全部通过（初始化/会话/面板渲染/数据结构）

# 已知要点
- **Edge CDP 无法连接**：DevToolsActivePort 文件过期（Edge 重启未更新），9222 端口虽被 msedge 监听但 WebSocket 握手 403/超时。技能禁止启动新浏览器实例，故改用 DOM shim 无浏览器验证
- **PowerShell 中文输出乱码**：一切中文内容写 UTF-8 文件再 read，或 Python 输出到文件
- **run_code 参数坑**：pwsh 调用偶尔报 "missing required property description"，用变量拼接参数对象可规避
- **JS 模板字符串**：run_code 代码中嵌套反引号模板字符串会冲突，改用 Python heredoc 写文件
- **脚本运行方式**：双击「启动灵犀专业版复刻.bat」或 python -m http.server 8234 --directory 项目目录
