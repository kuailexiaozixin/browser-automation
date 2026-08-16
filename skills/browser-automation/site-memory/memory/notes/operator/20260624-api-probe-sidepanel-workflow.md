---
name: API Probe 侧边栏连接与查看流程
summary: 通过 Playwright CDP 连接 Edge 扩展 sidepanel 页面的完整操作步骤
tags: [API Probe, CDP, Edge, sidepanel, Playwright]
noteTypes: [operator]
---

## 目标
连接已运行的 Edge 浏览器，查看 API Probe 插件侧边栏内容。

## 前置条件
- Edge 浏览器已运行（带远程调试端口）
- API Probe 插件 ID: ogpknbiolepcbcbkfinffgajgjeeomak
- 扩展源代码位置: D:\api-probe-extension（unpacked 加载）

## 操作步骤

### 步骤 1: 读取 Edge CDP 连接信息
```python
port_file = os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\DevToolsActivePort")
with open(port_file) as f:
    port = int(f.readline().strip())
    ws_path = f.readline().strip()
ws_url = f"ws://127.0.0.1:{port}{ws_path}"
```

### 步骤 2: 通过 PowerShell CDP 获取所有 targets
```powershell
$ws.ConnectAsync([Uri]$wsUrl).Wait()
$msg = @{id=1; method="Target.getTargets"} | ConvertTo-Json
$ws.SendAsync([ArraySegment[byte]]$bytes).Wait()
```
返回中找到 type="page"、url 含扩展 ID 的 target。

### 步骤 3: 激活 target
```powershell
$msg = @{id=1; method="Target.activateTarget"; params=@{targetId="CF4728..."}} | ConvertTo-Json
```

### 步骤 4: 使用 Playwright async_playwright 连接并查看页面
```python
async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp(ws_url)
    context = browser.contexts[0]
    # 遍历 pages 找到含扩展 ID 的页面
    for pg in context.pages:
        if "ogpknbiolepcbcbkfinffgajgjeeomak" in pg.url:
            probe_page = pg
```

### 步骤 5: 使用 CDP Session 在扩展页面上执行 JS
```python
cdp = await context.new_cdp_session(probe_page)
result = await cdp.send("Runtime.evaluate", {
    "expression": "document.body.innerText",
    "returnByValue": True
})
```

## 已知要点
- Edge HTTP CDP 端点（/json、/json/list）返回 404，必须用 WebSocket 连接
- 扩展 sidepanel 页面的 DOM/Runtime 域在浏览器级 WebSocket 不可用，必须通过 Playwright CDP Session 操作
- 扩展页面 target 的 title 字段显示为插件名称（如 "API Probe"），可用于直接识别
