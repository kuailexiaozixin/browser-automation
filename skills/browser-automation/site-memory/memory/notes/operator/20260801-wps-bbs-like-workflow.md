---
name: WPS论坛bbs.wps.cn帖子点赞操作流程
summary: bbs.wps.cn 帖子点赞按钮定位与点击，避免误点收藏按钮
kind: operator
---

## 目标
在 bbs.wps.cn/topic/<id> 帖子页为帖子主体点赞。

## 前置条件
- 本地 Edge 浏览器已登录 WPS 社区（顶部有用户头像标识）。
- 通过 cdp-use/browser 模块连接已运行的 Edge。

## 操作步骤
1. `browser.navigate(url)` 打开帖子页。
2. 帖子操作栏位于 `.topic-actions`，内含多个 `.action` 子元素，用图标类名区分：
   - `icon-share-all` → 分享
   - `icon-fav`（带 liked 类，文本"N +1"）→ 收藏（不是点赞，勿点）
   - `icon-cmmt` → 评论数
   - `icon-collect`（文本"+1"）→ 【真正的点赞按钮】
   - `icon-top`（hidden）→ 置顶
3. 定位 `i.icon-collect` 所在 `.action`，执行 `scrollIntoView` 后派发 pointerdown/mousedown/pointerup/mouseup/click 完整鼠标事件序列触发 Vue。
4. 验证：点赞后该按钮 class 变为含 `collected`（如 `action collected collected-animat`），文本从"+1"变为"N +1"。

## 已知要点
- 点赞数字显示在按钮文本中（如"1 +1"）；收藏按钮的 liked 类名不代表点赞，避免误点收藏。
- 仅 `el.click()` 可能不触发 Vue 处理，需派发完整鼠标事件序列。
- 已登录后无需验证码；若未登录点击会出现登录提示，需 request_manual。
