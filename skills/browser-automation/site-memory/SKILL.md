---
name: site-memory
description: 持久记忆系统，为浏览器自动化任务提供跨会话的上下文保持能力。基于 Markdown 文件存储，支持索引管理、语义召回、多种笔记类型。**强制启用，记忆存储于本技能专属目录。**
---

# site-memory - 持久记忆子系统

**强制启用规则**：使用 browser-automation 技能时，必须自动启动 site-memory 子技能，记忆存储于本子技能专属目录。

## 记忆存储目录

```
browser-automation/site-memory/memory/
├── INDEX.md                 # 记忆索引（自动生成）
├── manifest.json            # 笔记清单（自动生成）
└── notes/                   # 笔记目录
    ├── operator/            # 操作记录（自动登录、下载等）
    ├── guidance/            # 用户偏好/规则
    ├── context/             # 上下文信息（当前任务状态）
    └── reference/           # 参考资料
```

## 笔记格式

```markdown
---
name: 登录偏好
summary: 用户偏好使用扫码登录
tags: [登录, 偏好, 扫码]
noteTypes: [guidance]
---

当需要登录时，优先使用扫码登录方式而非账号密码。
```

## 强制集成规则

### 1. 任务开始时
自动执行召回，无需手动干预：
```bash
node site-memory/scripts/build-recall-input.mjs --task "<当前任务描述>" --recent-tools "browser,download"
```

### 2. 任务执行中
根据召回的记忆调整行为（如用户偏好登录方式）

### 3. 任务结束后（可选）
将重要信息写入记忆：
```bash
# 在 notes/operator/ 下记录操作
# 在 notes/context/ 下记录任务状态
```

## 快速使用

### 初始化（首次）
```bash
node site-memory/scripts/init-memory-root.mjs
```

### 手动创建笔记
在 `site-memory/memory/notes/` 对应类型目录下创建 `.md` 文件

### 召回记忆
```bash
node site-memory/scripts/build-recall-input.mjs --task "自动登录并下载报表" --recent-tools "browser,login"
```

### 读取召回内容
```bash
node site-memory/scripts/read-recalled-files.mjs --files "note1.md,note2.md"
```

## 笔记类型说明

| 类型 | 用途 | 存放目录 |
|------|------|----------|
| `operator` | 操作记录 | `notes/operator/` |
| `guidance` | 用户偏好/规则 | `notes/guidance/` |
| `context` | 上下文信息 | `notes/context/` |
| `reference` | 参考资料 | `notes/reference/` |
**强制规则（不可跳过）**：
1. **Pre-Flight**：任务开始前必须按序执行初始化 → 召回 → 读取 → 注入上下文，四步缺一不可
2. **Post-Flight**：任务结束后必须将操作记录或上下文写入对应笔记目录
3. **记忆存储**：所有数据必须存储在 `site-memory/memory/` 专属目录，不可使用其他位置
4. **违规处理**：跳过 Pre-Flight / Post-Flight 任意步骤 = 违反本技能强制规则
