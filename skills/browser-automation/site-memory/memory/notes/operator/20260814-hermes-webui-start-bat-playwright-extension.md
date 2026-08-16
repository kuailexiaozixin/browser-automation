---
name: hermes-webui用start-webui.bat启动及playwright扩展模式测试
summary: 用 git bash 启动 start-webui.bat 冒烟 Hermes WebUI，并用 playwright-cli extension 模式连接 Edge 做浏览器测试的完整流程
tags: [hermes-webui, start-webui.bat, playwright-cli, extension, Edge, CDP]
noteTypes: [operator]
---

## 目标
启动本地 hermes-webui 案例（03-nesquena-hermes-webui）并用 playwright 扩展模式做浏览器冒烟测试。

## 前置条件
- hermes_cli 通过 pip 装在 `python-env\Lib\site-packages`（非标准 hermes-agent 根目录）。
- 案例目录有 `start-webui.bat`（一键启动脚本）。
- Edge 已装 Playwright 扩展（ID `mmlmfjhmonkocbjadbfplnigmagldckm`）+ 已设 `PLAYWRIGHT_MCP_EXTENSION_TOKEN`。

## 操作步骤
1. **启动 server（= start-webui.bat 效果，沙箱禁 cmd 所以用 git bash 等价命令）**：
   ```
   cd <03-nesquena-hermes-webui>
   PYTHONHOME= PYTHONPATH= \
   HERMES_WEBUI_AGENT_DIR="<python-env>\Lib\site-packages" \
   "<python-env>\python.exe" server.py
   ```
   或用 git bash 直接 `./start-webui.bat`（后台）。
2. **验证监听**：`netstat -ano | grep :8787` 应有 LISTENING；日志出现 `Hermes Web UI listening on http://127.0.0.1:8787`。
3. **playwright-cli extension 模式连接 Edge**（HOME 必须指到可写目录，否则 EPERM）：
   ```
   cd <可写目录，如工作区>
   export HOME="<可写目录>"
   npx playwright cli attach --extension=msedge        # 建 session: msedge
   npx playwright cli --s=msedge goto http://localhost:8787
   npx playwright cli --s=msedge eval "() => document.title"
   npx playwright cli --s=msedge screenshot --filename shot.png --full-page
   ```

## 已知要点
- **start-webui.bat 两大坑**：(a) 必须 GBK/ANSI 编码保存（UTF-8 中文路径会被 cmd 按 GBK 拆碎成"不是内部或外部命令"）；(b) 启动前必须 `set "PYTHONHOME="` + `set "PYTHONPATH="`，否则 python-env 会加载被 PYTHONHOME 指向的其它 Python（如 3.13）标准库，报 `SRE module mismatch`。
- **hermes-agent 发现**：webui 的 start.ps1 只搜标准 hermes-agent 目录（~/.hermes/hermes-agent 等），找不到 pip 装的 hermes_cli。必须显式 `HERMES_WEBUI_AGENT_DIR` 指向 site-packages。
- **playwright-cli HOME/EPERM**：`D:\nodejs` 不可写导致 `.playwright-cli` 创建失败，需把 HOME 指到可写目录再运行。
- WebUI 页面 console 的 error 多来自 Edge 扩展（翻译/油猴）CSP report-only 提示，非应用问题。
- server 默认绑定 127.0.0.1:8787，未设密码时本机任意进程可读 API（提示设 HERMES_WEBUI_PASSWORD）。
- 操作完毕不得关闭 Edge 浏览器。
