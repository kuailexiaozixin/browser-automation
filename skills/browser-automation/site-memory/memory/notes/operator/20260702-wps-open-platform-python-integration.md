---
name: WPS开放平台Python集成方案检索
summary: 检索WPS开放平台文档状态并整理Python调用WPS接口的完整方案
tags: [WPS, Python, COM, REST API, WebOffice, pywpsrpc]
noteTypes: [operator]
---

## 目标
获取WPS开放平台关于WPS365客户端集成模式的文档内容，并整理Python调用WPS接口的方案。

## 前置条件
- Edge浏览器已运行
- 已安装requests、playwright等Python库
- 已初始化site-memory（init-memory-root.mjs）

## 操作步骤

### 步骤1: 尝试直接获取页面内容
```python
import requests
url = "https://open.wps.cn/documents/app-integration-dev/wps365/client/wpsoffice/wps-integration-mode/"
resp = requests.get(url)
print(resp.text[:3000])
```
**结果：** 返回200但内容为空壳HTML，说明是SPA页面，需要浏览器渲染。

### 步骤2: 尝试Jina Reader API
```python
url = "https://r.jina.ai/https://open.wps.cn/..."
```
**结果：** 返回空内容，无法获取。

### 步骤3: 使用Playwright CDP连接已运行的Edge
```python
import asyncio
import os
from playwright.async_api import async_playwright

port_file = os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\DevToolsActivePort")
with open(port_file) as f:
    port = int(f.readline().strip())
    ws_path = f.readline().strip()
ws_url = f"ws://127.0.0.1:{port}{ws_path}"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = await context.new_page()
        await page.goto("https://open.wps.cn/...", wait_until="networkidle")
        text = await page.evaluate("() => document.body.innerText")
        print(text)
asyncio.run(main())
```
**结果：** 页面显示"您访问的文档不存在，请联系管理员"，说明该URL已失效。

### 步骤4: 使用search工具检索替代方案
通过search搜索WPS Python集成相关文档，获取：
- COM接口方案（win32com）
- WPS-SDK-Python
- pywpsrpc（Linux）
- WebOffice REST API
- WPS365 OpenAPI

### 步骤5: 整理并输出完整方案
将检索到的信息整理成结构化文档，包含：
1. 原始链接状态说明
2. 5种Python调用WPS的方式
3. 适用场景对比表
4. 代码示例

## 已知要点
- WPS开放平台的SPA页面无法通过requests直接获取内容
- 必须通过Playwright CDP或browser-use等浏览器自动化工具获取渲染后内容
- open.wps.cn的部分文档URL可能已变更或失效，需通过search获取最新信息
- COM接口仅支持Windows，pywpsrpc支持Linux
- WebOffice API需要申请开发者权限
