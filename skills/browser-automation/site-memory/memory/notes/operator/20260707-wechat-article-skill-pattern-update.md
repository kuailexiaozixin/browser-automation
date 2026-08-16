---
name: 微信公众号文章获取与 skill-pattern 更新
summary: 通过 CDP 连接 Edge 浏览器打开微信公众号文章，获取内容后补充到 skill-pattern 技能中
tags: [浏览器自动化, CDP, Edge, 微信公众号, skill-pattern, SSL]
noteTypes: [operator]
---

# 目标
获取微信公众号文章 https://mp.weixin.qq.com/s/kLriFc8yBEqtG31Isja7sw 的内容，将北大提出的 SSL Skill 编写规范补充到 skill-pattern 技能中。

# 前置条件
- Edge 浏览器已安装并开启远程调试（DevToolsActivePort 文件存在）
- 已安装 Python websocket-client 库

# 操作步骤

## 1. 读取 DevToolsActivePort
```python
port_file = os.path.expanduser("~\AppData\Local\Microsoft\Edge\User Data\DevToolsActivePort")
with open(port_file) as f:
    port = int(f.readline().strip())
    ws_path = f.readline().strip()
ws_url = f"ws://127.0.0.1:{port}{ws_path}"
```

## 2. 通过 CDP WebSocket 连接 Edge
```python
ws = websocket.create_connection(ws_url, suppress_origin=True)
```

## 3. 创建新标签页打开目标 URL
```python
create_cmd = {
    "id": 1,
    "method": "Target.createTarget",
    "params": {"url": "https://mp.weixin.qq.com/s/kLriFc8yBEqtG31Isja7sw", "newWindow": False}
}
ws.send(json.dumps(create_cmd))
result = json.loads(ws.recv())
target_id = result["result"]["targetId"]
```

## 4. 附加到目标并获取 Session ID
```python
attach_cmd = {
    "id": 2,
    "method": "Target.attachToTarget",
    "params": {"targetId": target_id, "flatten": True}
}
ws.send(json.dumps(attach_cmd))
# 等待 Target.attachedToTarget 事件获取 session_id
```

## 5. 获取页面 HTML
```python
html_cmd = {
    "id": 3,
    "method": "Runtime.evaluate",
    "params": {"expression": "document.documentElement.outerHTML", "returnByValue": True},
    "sessionId": session_id
}
ws.send(json.dumps(html_cmd))
html_result = json.loads(ws.recv())
html_content = html_result["result"]["result"]["value"]
```

## 6. 解析文章内容
使用 BeautifulSoup 解析 HTML，提取 rich_media_content 中的正文。

## 7. 更新 skill-pattern 技能
- 在 references/ 下创建 ssl-representation.md，详细记录 SSL 三层表示法
- 在 SKILL.md 中添加 SSL 表示层章节和引用

# 已知要点
- 微信公众号文章有时会触发人机验证，需用户手动完成
- Target.attachToTarget 返回的 session_id 通过事件推送（Target.attachedToTarget），不在响应中
- 使用 websocket-client 的 suppress_origin=True 参数避免 Edge 返回 403
