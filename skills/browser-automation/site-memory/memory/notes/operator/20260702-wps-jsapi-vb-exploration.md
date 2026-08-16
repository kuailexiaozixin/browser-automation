---
name: WPS JSAPI VB交互探索
summary: 尝试获取WPS开放平台JSAPI文档并探索VB与JS交互方式
tags: [WPS, JSAPI, VB, VBA, JSA, 加载项]
noteTypes: [operator]
---

## 目标
获取WPS开放平台关于JSAPI的文档，特别是VB/JS交互相关内容。

## 前置条件
- Edge浏览器已运行
- 已安装requests、playwright等Python库
- 已初始化site-memory（init-memory-root.mjs）

## 操作步骤

### 步骤1: 尝试直接获取页面内容
```python
import requests
url = "https://open.wps.cn/documents/app-integration-dev/wps365/client/wpsoffice/jsapi/go-to-js-from-vb"
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

### 步骤4: 搜索替代方案
通过search搜索WPS JSAPI和VB交互相关内容，获取：
- WPS宏的两种模式（JS宏和VBA宏）
- JSA可以通过ActiveXObject调用VBA工程中的类模块
- WPS加载项使用Web技术栈（HTML/CSS/JS）

### 步骤5: 尝试访问旧版JSAPI文档
访问 `https://open.wps.cn/previous/docs/client/js-api/` 相关页面
**结果：** 返回空壳内容或"文档不存在"

## 已知要点
- WPS开放平台目前正在改版或维护，很多旧版文档链接已失效
- WPS支持两种宏：JS宏（JSA，默认）和VBA宏（需单独安装插件）
- JSA可以通过`new ActiveXObject`调用VBA工程中的类模块，实现跨语言互操作
- WPS加载项使用Web技术栈，通过RPC协议与WPS内核通信
- 旧版JSAPI文档路径：`https://open.wps.cn/previous/docs/client/js-api/`

## 当前WPS开放平台状态
- 主页 open.wps.cn 加载超时或返回空内容
- 客户端二次开发页面返回"文档不存在"
- 旧版文档路径 /previous/docs/client/js-api/ 部分页面可访问但内容为空
