---
name: GitHub 仓库 README 与 CDN 包信息抓取
summary: 从 GitHub 仓库获取 README 内容及项目元数据，包括 GitHub API 方式 vs 页面解析方式的选择、npm/jsDelivr CDN 文件清单枚举、版本号获取等
tags: [GitHub, README, CDN, 元数据, 包管理, npm, jsDelivr]
noteTypes: [operator]
---

# 目标

从 GitHub 仓库（如开源 CSS 框架、JS 库、Python 包的 GitHub 页面）获取 README 内容、项目版本号、许可证、CDN 文件清单等信息，为后续生成技能参考文件提供数据源。

# 前置条件

- Python requests 可用（无需浏览器，GitHub 页面为 SSR）
- 已知 GitHub 仓库的 owner/repo 名称（如 `picocss/pico`）

# 操作步骤

## 阶段一：选择信息获取方式

GitHub 仓库信息获取有三种方式，按优先级选择：

### 方式 A：GitHub API（推荐，最可靠）

```python
import requests

# 获取 README（raw 格式）
url = f"https://api.github.com/repos/{owner}/{repo}/readme"
r = requests.get(url, headers={
    "Accept": "application/vnd.github.raw+json",
    "User-Agent": "Mozilla/5.0"
}, timeout=10)
readme_text = r.text  # 纯文本格式，含原始 Markdown 内容
```

**优势**：
- 返回纯 Markdown 文本（非 HTML），无样式干扰
- 不包含 GitHub 页面 UI 元素（导航、按钮、广告等）
- 不受 GitHub 页面结构变更影响
- 认证后（加 `Authorization: Bearer token`）可提高速率限制

**限制**：
- 未认证的 API 请求速率限制为 60 次/小时，通常够用
- 需要准确的 `owner/repo` 名称

### 方式 B：GitHub 页面解析（兜底）

当 API 方式不可用或需要页面特定信息（如 stars count、文档链接）时：

```python
from bs4 import BeautifulSoup

url = f"https://github.com/{owner}/{repo}"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
soup = BeautifulSoup(r.text, 'html.parser')

# 提取 README
article = soup.find('article')
if article:
    for h in article.find_all(['h1','h2','h3','h4']):
        print(f"  {h.name}: {h.get_text(strip=True)}")

# 提取描述（meta description）
for meta in soup.find_all('meta'):
    if meta.get('name') == 'description':
        print(f"描述: {meta.get('content')}")

# 提取仓库元数据
stars = soup.select_one('[data-hydro-click*="star"]')
if stars:
    print(f"Stars: {stars.get_text(strip=True)}")
```

**注意事项**：
- GitHub 页面结构经常变化，CSS 选择器可能失效
- 大量无关 UI 元素需要过滤（导航栏、侧边栏、标签页等）
- README 中嵌入的图片链接可能需要转换（相对路径 → 绝对路径）

### 方式 C：Jina Reader（备选）

```python
url = f"https://r.jina.ai/https://github.com/{owner}/{repo}"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
```

**注意**：Jina Reader 在国内网络环境下可能频繁超时，不推荐作为主要方式。

## 阶段二：从 npm 包获取版本和 CDN 文件清单

### 2.1 获取最新版本号

```python
# 方式 1: npm registry API
r = requests.get(f"https://registry.npmjs.org/@{scope}/{name}/latest",
                 headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
version = r.json().get('version')
print(f"版本: {version}")

# 方式 2: jsDelivr API
r = requests.get(f"https://data.jsdelivr.com/v1/packages/npm/@{scope}/{name}",
                 headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
data = r.json()
print(f"最新版本: {data.get('tags', {}).get('latest', 'unknown')}")
```

### 2.2 枚举 CDN 文件清单

```python
# jsDelivr CDN 目录列表
r = requests.get(f"https://cdn.jsdelivr.net/npm/@{scope}/{name}@{version}/css/",
                 headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
from bs4 import BeautifulSoup
soup = BeautifulSoup(r.text, 'html.parser')

css_files = []
for a in soup.find_all('a'):
    href = a.get('href', '')
    if href.endswith('.css') or href.endswith('.min.css'):
        css_files.append(href)
```

### 2.3 验证文件存在性

```python
known_files = [
    "pico.min.css",
    "pico.css",
    "pico.classless.min.css",
    "pico.amber.min.css",
    # ...
]
available = {}
for f in known_files:
    url = f"https://cdn.jsdelivr.net/npm/@{scope}/{name}@{version}/css/{f}"
    r = requests.head(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
    available[f] = r.status_code == 200
```

## 阶段三：内容清洗与结构化

### 3.1 README 结构化提取要点

GitHub README 通常包含以下可提取的结构：

| 信息类型 | 提取方式 |
|---------|---------|
| 项目描述 | `soup.find('meta', {'name': 'description'})['content']` |
| 安装方式 | 在 README 中搜索 `Install`、`Quick start`、`Getting started` 等标题 |
| API 文档链接 | 搜索 `## Documentation`、`## API` 等章节 |
| 许可证 | 搜索 `## License`、`## Copyright` 章节 |
| 徽章信息 | `soup.find_all('img', alt=re.compile(r'npm\|build\|license\|version'))` |

### 3.2 颜色主题的命名模式

许多 CSS 框架提供多个主题变体，文件命名通常遵循以下模式：

```
{base}[.{variant}][.{color}].min.css
```

例如 PicoCSS:
- `pico.min.css` — 默认
- `pico.amber.min.css` — 琥珀色
- `pico.classless.blue.min.css` — 无类 + 蓝色
- `pico.conditional.conditional.amber.min.css` — 条件 + 琥珀色
- `pico.fluid.classless.conditional.red.min.css` — 流式 + 无类 + 条件 + 红色

**关键经验**：通过遍历 CDN 目录列表获取全部文件，然后按文件名后缀自动分类总结，远比手动枚举可靠。总组合数 = 颜色数 × 变体数。

## 阶段四：结合 README 与子页面构建参考文档

典型工作流：

```python
# 1. 从 GitHub README 获取概述、安装方式、基础用法
readme = fetch_github_readme(owner, repo)

# 2. 从 CDN 枚举所有可用的文件变体
cdn_files = enumerate_cdn_files(scope, name, version)

# 3. 从文档站抓取所有子页面的详细内容
docs = fetch_doc_subpages("https://框架站点/docs")

# 4. 合并为参考文档
#    - GitHub README → 概述章节
#    - CDN 文件清单 → 安装/主题章节
#    - 文档子页面 → 各组件/功能章节
```

# 已知要点

- **API 优先**：GitHub API 读取 README 始终比页面解析更稳定，优先使用。仅在需要页面特有信息（近期活动、讨论数等）时才解析 HTML。
- **README 是概述的最佳来源**：GitHub README 通常包含项目定位、核心卖点、安装方式、基础示例等最浓缩的信息，是生成参考文件"概述"章节的首选数据源。
- **CDN 文件命名遵循组合模式**：`{base}.{variant}.{color}.min.css`，同类型文件通过命名模式自动识别变体数量比手动计数更可靠。
- **版本号约束**：CDN URL 中的版本号`@2` 或 `@2.1.1` 必须与实际包版本一致。从 npm registry 或 jsDelivr API 获取最新版本号，不要硬编码。
- **HEAD 请求验证**：对已知的可能文件名使用 `requests.head()` 验证存在性，比 `GET` 请求更轻量（仅返回响应头，不下载整个文件）。
- **CDN 文件较多时**：同一框架的文件组合可能超过 100 个（如 PicoCSS v2 有 100+ CDN 组合），建议按命名模式分类汇总而非逐一列出。
