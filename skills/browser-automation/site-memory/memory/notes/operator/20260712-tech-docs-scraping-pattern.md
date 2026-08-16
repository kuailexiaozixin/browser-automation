---
name: 技术文档网站结构化抓取
summary: 从技术文档网站（如 picocss.com/docs）批量抓取所有子页面内容，提取正文、代码示例、组件结构，覆盖导航菜单识别、内容容器定位、子页面前置探测等完整流程
tags: [浏览器自动化, 静态抓取, 技术文档, 批量爬取, HTML解析, 内容提取]
noteTypes: [operator]
---

# 目标

从技术文档网站（如 CSS 框架、UI 库、工具链的官方文档站）批量获取所有子页面 HTML，提取正文内容、代码示例、组件文档，汇总为结构化的本地参考文件。

# 前置条件

- Python requests + BeautifulSoup 可用（页面为静态 SSR，无需 JS 渲染）
- 目标文档站点的 URL 结构已知（如 `/docs/grid`、`/docs/forms` 等命名模式）
- 若页面依赖 JavaScript 动态加载内容，则需要回退到 CDP WebSocket 方案

# 操作步骤

## 阶段一：站点结构探测

### 1.0 确定渲染方式

优先用 `requests.get(url)` 尝试获取首页/文档首页：

```python
r = requests.get("https://目标站点/docs", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
```

- 若返回的 HTML 包含完整正文内容 → 静态 SSR，直接用 requests + BeautifulSoup
- 若返回为空白壳（`<div id="root"></div>` 等）→ 需 CDP 浏览器渲染或 Jina Reader
- **不要为静态页面启动浏览器**，这是不必要的开销

### 1.1 提取导航结构

目标站点的文档首页通常包含完整的侧边栏/导航菜单，列出所有子页面链接。解析方式：

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, 'html.parser')

# 策略 A：查找主导航区域
nav = soup.find('nav')  # 或 sidebar / aside
links = set()
for a in nav.find_all('a', href=True):
    href = a['href']
    if href.startswith('/docs/') or href.startswith('/docs'):
        links.add(href)

# 策略 B：查找导航列表
aside = soup.find('aside', id='documentation-menu')
if aside:
    for a in aside.find_all('a', href=True):
        links.add(a['href'])

# 策略 C：从页面所有链接中筛选（兜底）
all_links = [a['href'] for a in soup.find_all('a', href=True)
             if '/docs/' in a['href'] or '/doc/' in a['href']]
```

**关键经验**：技术文档站点的导航菜单通常使用 `<aside>`、`<nav>` 或 `<div class="sidebar">` 包裹。优先用 id 定位（如 `id="documentation-menu"`），若没有则按 class 名称匹配。如果导航菜单是 JS 动态渲染（如 react-router），则需要 CDP 浏览器方案。

### 1.2 构建待抓取 URL 列表

```python
base_url = "https://目标站点"
all_urls = {}

for link in links:
    full_url = link if link.startswith('http') else base_url + link
    name = link.rstrip('/').split('/')[-1] or 'index'
    all_urls[name] = full_url
```

### 1.3 前检查：先抓 3-5 个验证结构

批量抓取前，先抓取首页和 2-3 个子页面，确认页面结构一致，避免后续大规模抓取全部失败。

## 阶段二：批量抓取

### 2.0 批量请求（无须浏览器）

```python
fetched = {}
for name, url in all_urls.items():
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        fetched[name] = (r.text, r.status_code)
        print(f"✓ {name}: {r.status_code} ({len(r.text)} chars)")
    except Exception as e:
        print(f"✗ {name}: {e}")
```

**注意**：
- 静态文档站对批量请求容忍度高，无需刻意延迟
- 若部分子页面返回 404，记录下来即可，不影响其他页面
- 子页面数量超过 30 时，考虑加入 `time.sleep(0.3)` 避免触发限流

### 2.1 内容定位——识别正文容器

技术文档的页面布局通常为：
```
<main>
  <nav>侧边栏</nav>                    ← 需跳过
  <aside id="documentation-menu">导航</aside>  ← 需跳过
  <div id="content">                   ← 正文容器
    <section>...</section>
    <section>...</section>
  </div>
</main>
```

核心经验：**从 `<main>` 中排除导航元素后，正文通常在最后一个非导航块**。

```python
def get_content_div(soup):
    """尝试多种策略定位正文容器"""
    # 策略 1: 按 id 或 class 直接定位（最常见）
    for selector in ['div#content', 'div.content', 'main', 'article', '.doc-content', '.markdown-body']:
        el = soup.select_one(selector)
        if el:
            return el

    # 策略 2: 从 <main> 中排除导航
    main = soup.find('main')
    if main:
        for child in main.children:
            if child.name not in ('nav', 'aside', 'script', 'style'):
                return child  # 第一个非导航子元素

    # 策略 3: 直接反选
    main = soup.find('main')
    if main:
        for el in main.find_all(['div', 'section'], recursive=False):
            cls = ' '.join(el.get('class', []))
            if 'sidebar' not in cls and 'nav' not in cls and 'toc' not in cls:
                return el

    return None
```

**关键经验**：技术文档站点的正文容器命名高度不统一，建议准备 3-4 种定位策略按优先级尝试。

### 2.2 分段提取正文

```python
def extract_sections(content_el):
    """提取正文中的结构化内容"""
    parts = []
    for el in content_el.children:
        if not el.name:
            continue
        tag = el.name
        text = el.get_text(strip=True)
        if not text:
            continue

        if tag.startswith('h'):
            level = int(tag[1])
            parts.append(('heading', level, text))
        elif tag == 'p':
            parts.append(('text', text))
        elif tag == 'pre':
            parts.append(('code', el.get_text().strip()))
        elif tag in ('ul', 'ol'):
            items = [li.get_text(strip=True) for li in el.find_all('li') if li.get_text(strip=True)]
            if items:
                parts.append(('list', items))
        elif tag == 'table':
            rows = []
            for tr in el.find_all('tr'):
                row = [c.get_text(strip=True) for c in tr.find_all(['th', 'td'])]
                if any(row):
                    rows.append(row)
            if rows:
                parts.append(('table', rows))
    return parts
```

**关键经验**：
- `content_el.children` 通常按渲染顺序排列，是文档正文的天然分段
- 部分技术文档在 `<section>` 内部再做二级分段，需要递归处理
- `<pre>` 代码块中可能混入交互式 demo（如实时编辑器），需用 `len(el.get_text()) > 30` 过滤掉短 demo

### 2.3 识别并跳过交互式 Demo

部分技术文档在正文中嵌入"点击试试"类交互 demo（如 CSS Grid 在线沙盒）。这些 demo 通常包含大量无关的内部 HTML，直接提取作为代码示例会导致参考文件膨胀且无意义。

**识别特征**：
- `<div>` 内含输入框、按钮等交互元素
- text 很短（<50 字符）但内部 HTML 很长
- 被 `<div class="demo">`、`<div class="playground">` 等包裹

```python
def is_interactive_demo(el):
    """判断是否交互式 demo 块"""
    if not el.name == 'div':
        return False
    cls = ' '.join(el.get('class', []))
    if any(kw in cls for kw in ['demo', 'playground', 'sandbox', 'interactive']):
        return True
    text = el.get_text(strip=True)
    html_len = len(str(el))
    return len(text) < 80 and html_len > 2000
```

## 阶段三：内容清洗与结构化

### 3.1 汇总并排版

所有子页面抓取完成后，将内容汇总为本地 Markdown 参考文件：

```python
def build_reference(all_content):
    lines = []
    for name, parts in sorted(all_content.items()):
        lines.append(f"## {name}")
        for part in parts:
            if part[0] == 'heading':
                prefix = '#' * part[1]
                lines.append(f"\n{prefix} {part[2]}")
            elif part[0] == 'text':
                lines.append(f"\n{part[1]}")
            elif part[0] == 'code':
                lines.append(f"\n```html\n{part[2]}\n```")
            elif part[0] == 'list':
                lines.append('\n' + '\n'.join(f"- {li}" for li in part[1]))
            elif part[0] == 'table':
                # 格式化为 Markdown 表格
                hdr = ' | '.join(part[1][0])
                lines.append(f"\n| {hdr} |")
                lines.append(f"| {' | '.join(['---']*len(part[1][0]))} |")
                for row in part[1][1:]:
                    lines.append(f"| {' | '.join(row)} |")
    return '\n'.join(lines)
```

### 3.2 额外子页面前置探测

**关键经验**：技术文档的导航菜单中列出的所有子页面 URL 并不一定都有值。部分页面可能是"Coming Soon"占位符，访问返回 404 或几乎没有正文内容（<200 字符），应在汇总时标记或排除。

## 阶段四：回退方案

### 4.1 何时需要 CDP 浏览器

仅当以下情况时回退到 CDP WebSocket 方案：
- 页面返回的 HTML 不含正文（仅 `<div id="root"></div>` 之类的 SPA 壳）
- 内容通过异步 API 加载（查看 Network 面板确认）
- 页面依赖 `onload` 事件渲染（如 JS 注入内容）
- 目标站点有 Cloudflare / Turnstile 等反爬校验

### 4.2 CDP 方案（见 wechat-article 笔记）

# 已知要点

- **静态优先原则**：技术文档站点多为静态 SSR（如基于 Hugo、Docusaurus、VitePress），优先用 requests 而非浏览器。浏览器只用于 SPA 文档站。
- **导航结构是关键入口**：技术文档的导航菜单通常包含所有子页面的完整 URL 列表，这是批量抓取的"目录"。
- **内容容器命名不统一**：`#content`、`.content`、`main`、`article`、`.doc-content`、`.markdown-body`、`.prose` 都可能是正文容器，准备多套定位策略。
- **演示 demo 需跳过**：交互式 demo（如 CodePen 嵌入、CSS Grid 沙盒、实时编辑器）会引入大量无关 HTML，必须用启发式规则排除。
- **子页面存在空内容**：导航菜单可能列出"占位"页面（内容为空或极少），需通过内容长度过滤。
- **CDN 文件枚举**：若需要获取 CDN 文件清单（如 CSS 框架的多个主题变体），使用 jsDelivr API 或 CDN 目录列表，比逐一猜测更可靠：`https://data.jsdelivr.com/v1/packages/npm/@picocss/pico/files`
