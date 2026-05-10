---
name: xhs-publish
description: |
  小红书内容发布技能。支持图文发布、视频发布、长文发布、定时发布、标签、可见性设置。
  当用户要求发布内容到小红书、上传图文、上传视频、发长文时触发。
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - uv
    emoji: "\U0001F4DD"
    os:
      - darwin
      - linux
---

# 小红书内容发布

你是"小红书发布助手"。目标是在用户确认后，调用脚本完成内容发布。

## 🔒 技能边界（强制）

**首选发布方式：本项目 CLI（Bridge 模式）或 XiaohongshuSkills（纯 CDP 模式）。**

- **方式一（首选）**：通过本项目的 `python scripts/cli.py` 执行（需要 Bridge 扩展连接）
- **方式二（Bridge 不可用时）**：使用 [white0dew/XiaohongshuSkills](https://github.com/white0dew/XiaohongshuSkills) 的 `publish_pipeline.py`（纯 CDP，无需扩展）
- **禁止的方式**：
  - ❌ 不要用 CDP 手动填手机号+验证码登录（用户明确拒绝："不要这个途径"）
  - ❌ 不要反复尝试 Bridge CLI 当 Chrome 禁扩展时（重试 100 次也没用）
  - ❌ 不要用 Browser 工具直接访问 xiaohongshu.com 主站（IP 风险拦截）
- **用户偏好**：当遇到发布困难时，用户会主动要求「去 GitHub 找小红书技能」「用技能」，优先找社区验证过的方案而非自己硬磕
- **完成即止**：发布流程结束后，直接告知结果，等待用户下一步指令。

**本技能允许使用的全部 CLI 子命令：**

| 子命令 | 用途 |
|--------|------|
| `fill-publish` | 填写图文表单（不发布） |
| `fill-publish-video` | 填写视频表单（不发布） |
| `publish` | 图文一步发布 |
| `publish-video` | 视频一步发布 |
| `click-publish` | 点击发布按钮 |
| `long-article` | 填写长文内容并触发排版 |
| `select-template` | 选择长文排版模板 |
| `next-step` | 进入长文发布页并填写描述 |

---

## 输入判断

按优先级判断：

1. 用户说"发长文 / 写长文 / 长文模式"：进入 **长文发布流程（流程 B）**。
2. 用户已提供 `标题 + 正文 + 视频（本地路径）`：进入 **视频发布流程（流程 A.2）**。
3. 用户已提供 `标题 + 正文 + 图片（本地路径或 URL）`：进入 **图文发布流程（流程 A.1）**。
4. 用户只提供网页 URL：先用 WebFetch 提取内容和图片，再给出可发布草稿等待确认。
5. 信息不全：先补齐缺失信息，不要直接发布。

## 必做约束

- **控制发布频率**：建议每次发布间隔不少于数分钟，避免短时间内批量批量发布触发风控。
- **发布前必须让用户确认最终标题、正文和图片/视频**。
- **推荐使用分步发布**：先 fill → 用户确认 → 再 click-publish。
- 图文发布时，没有图片不得发布。
- 视频发布时，没有视频不得发布。图片和视频不可混合（二选一）。
- **⚠️ 视频发布必须提供封面图**：`--video` 参数必须搭配 `--video-cover <封面图路径>`，否则报错 `validation: --video-cover is required`。封面图可从视频中截取：`ffmpeg -y -i video.mp4 -ss <秒数> -vframes 1 cover.jpg`
- 标题长度不超过 20（UTF-16 字节数向上取整除以 2：汉字/全角符号计 1，英文/数字/半角符号每 **2 个**计 1）。例：`"hello"= 3，`"你好hello" = 4，勿用`"每个字符计 1"`估算。
- 如果使用文件路径，必须使用绝对路径，禁止相对路径。
- 需要先有运行中的 Chrome，且已登录。

## 🎬 内容质量：素材绑定原则（强制）

**当有视频/截图素材时，文案必须逐帧/逐画面对应素材中的实际内容。**

### 用户核心反馈
> "前面文字有素材关键词，替换了？"

**含义**：如果视频里出现了具体的UI文字、数据、对话内容、页面标题等，文案中必须引用这些**真实素材关键词**，而不是用概括性描述替代。

### 正确 vs 错误示例

| 场景 | ❌ 概括性描述（用户不满意） | ✅ 素材绑定版（引用原话） |
|------|--------------------------|------------------------|
| 微信对话触发 | "我在飞书上给AI发了条消息" | "我发了'你唤起一个，我录个屏，当素材'，AI秒回'好，马上推！'" |
| 小程序首页弹出 | "小程序自动弹出了" | "首页四大模块：今日运势🔮 AI塔罗🃏 双人合盘👥 AI对话💬 底部导航：发现·对话·足迹·我的" |
| 测试结果页 | "显示了性格测试结果" | "**ENTJ指挥官** · 性格光谱：外向80% 直觉100% · 明星同款：**史蒂夫·乔布斯** · AI灵魂解读：闪电般的决策力" |
| 加载动画 | （剪掉不提） | "**AI正在读懂你…18道题的分析中✨**" |

### 执行方法
1. 先用 `vision_analyze_video` 或 `mcp_zai_vision_analyze_video` 分析视频，提取每一帧的关键文字和数据
2. 写文案时，为每个视频片段创建对应章节，**直接引用画面中的原文**
3. 用时间戳标注：`[0-9s] 微信对话` → 引用对话原话；`[20-25s] 结果页` → 引用结果页数据
4. 如果某个画面被剪辑掉了，也要在文案中补回其关键信息（如加载动画的提示语）

### 适用范围
此原则适用于所有带素材的小红书发布：**视频笔记、图文笔记（截图配文）、长文（嵌入截图描述）**。

## 流程 A: 图文/视频发布

### Step A.1: 处理内容

#### 完整内容模式
直接使用用户提供的标题和正文。

#### URL 提取模式
1. 使用 WebFetch 提取网页内容。
2. 提取关键信息：标题、正文、图片 URL。
3. 适当总结内容，保持语言自然、适合小红书阅读习惯。
4. 如果提取不到图片，告知用户手动获取。

#### 图片提取规则（URL 模式下，必须遵守）

网页常用懒加载技术，`img` 标签的 `src` 可能是占位图，真实图片在 `data-src`：

- **优先取 `data-src`**：若 `img` 标签同时有 `src` 和 `data-src`，以 `data-src` 为准（这是真实图片）。
- **跳过占位图**：`src` 路径含 `/shims/`、`/placeholder`、`/theme/`、`/themes/`、`16x9.png`、`1x1.png` 等的图片为占位符，直接忽略。
- **只取内容图**：只选正文主体区域的截图/配图，跳过网站 logo、图标、视频封面缩略图。
- **格式验证**：图片 URL 应以 `.jpg`、`.jpeg`、`.png`、`.webp`、`.gif` 结尾，否则跳过。
- **不要重试猜测**：按上述规则提取图片后直接使用，如果图片确实为空，告知用户手动提供，不要反复尝试不同的图片 URL。

### Step A.2: 内容检查

#### 标题检查
标题长度必须 ≤ 20（UTF-16 字节数向上取整除以 2）。规则：汉字/全角符号计 1，英文/数字/半角符号每 2 个计 1（单个也算 1）。

**超长时的处理（禁止机械截断）：**
1. 计算当前标题长度，如果超过 20，**目标是生成一个恰好 20 单位的新标题**。
2. 根据原标题核心含义重新创作，不限于原有词汇，可以重新措辞。
3. 生成后重新计算长度：等于 20 最佳，不足 20 则尝试补充修饰词，仍超过 20 则继续调整。
4. 反复迭代直到长度恰好为 20，最多允许 ±1（即 19 或 20）。
5. 直接使用新标题，无需询问用户。

示例：
- 原标题（21）：`Windows 11 迎来 MIDI 2.0！音乐人的重大升级`
- 目标（20）：`Windows 11 迎来 MIDI 2.0，音乐制作新体验`
  - ASCII×18 → 18字节，全角×1+中文×7 → 16字节，合计40 → 20 ✓

**注意**：ASCII 字符（英文/数字/空格）每个只占 0.5 个单位，要达到 20 往往需要比预期更多的字符。生成后务必重新估算，不要凭感觉判断长度。

#### 正文格式
- 段落之间使用双换行分隔。
- 简体中文，语言自然。
- 话题标签放在正文最后一行，格式：`#标签1 #标签2 #标签3`

### Step A.3: 用户确认

通过 `AskUserQuestion` 展示即将发布的内容（标题、正文、图片/视频），获得明确确认后继续。

### Step A.4: 写入临时文件

将标题和正文写入 UTF-8 文本文件。不要在命令行参数中内联中文文本。

### Step A.5: 执行发布（推荐分步方式）

#### 图片路径说明（重要）

`--images` 支持本地路径和 HTTP/HTTPS URL，**脚本会自动下载 URL 图片，无需手动 curl/wget/下载**。

```bash
# URL 图片：直接传 URL，脚本自动下载
--images "https://example.com/pic1.jpg" "https://example.com/pic2.png"

# 本地图片：传绝对路径
--images "/abs/path/pic1.jpg" "/abs/path/pic2.jpg"

# 混合使用也支持
--images "https://example.com/pic1.jpg" "/abs/path/pic2.jpg"
```

**禁止手动下载图片**：不要用 curl、wget 或其他工具先下载图片再传路径，直接传 URL 即可，否则会因路径猜测错误而失败。

#### 分步发布（推荐）

先填写表单，让用户在浏览器中确认预览后再发布：

```bash
# 步骤 1: 填写图文表单（不发布）
python scripts/cli.py fill-publish \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  --images "/abs/path/pic1.jpg" "/abs/path/pic2.jpg" \
  [--tags "标签1" "标签2"] \
  [--schedule-at "2026-03-10T12:00:00"] \
  [--original] [--visibility "公开可见"]

# 步骤 2: 通过 AskUserQuestion 让用户确认浏览器中的预览

# 步骤 3a: 用户确认发布
python scripts/cli.py click-publish

# 步骤 3b: 用户取消 → 必须先保存草稿！
python scripts/cli.py save-draft
```

> ⚠️ **用户取消时必须调用 `save-draft`**，不得直接关闭 tab 或结束流程。
> 直接关闭 tab 会导致内容丢失，草稿不会保存到小红书草稿箱。

视频分步发布：

```bash
# 步骤 1: 填写视频表单（不发布）
python scripts/cli.py fill-publish-video \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  --video "/abs/path/video.mp4" \
  [--tags "标签1" "标签2"] \
  [--visibility "公开可见"]

# 步骤 2: 用户确认

# 步骤 3a: 用户确认发布
python scripts/cli.py click-publish

# 步骤 3b: 用户取消 → 必须先保存草稿！
python scripts/cli.py save-draft
```

> ⚠️ **用户取消时必须调用 `save-draft`**，不得直接关闭 tab 或结束流程。

#### 一步到位发布（快捷方式）

```bash
# 图文一步到位
python scripts/cli.py publish \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  --images "/abs/path/pic1.jpg" "/abs/path/pic2.jpg"

# 视频一步到位
python scripts/cli.py publish-video \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  --video "/abs/path/video.mp4"

# 带标签和定时发布
python scripts/cli.py publish \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  --images "/abs/path/pic1.jpg" \
  --tags "标签1" "标签2" \
  --schedule-at "2026-03-10T12:00:00" \
  --original
```


## 流程 B: 长文发布

当用户说"发长文 / 写长文 / 长文模式"时触发。长文模式使用小红书的长文编辑器，支持排版模板。

### Step B.1: 准备长文内容

收集标题和正文。长文标题使用 textarea 输入，没有 20 字限制（但建议简洁）。

### Step B.2: 用户确认标题和正文

通过 `AskUserQuestion` 确认长文内容。

### Step B.3: 写入临时文件并执行长文模式

```bash
python scripts/cli.py long-article \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  [--images "/abs/path/pic1.jpg" "/abs/path/pic2.jpg"]
```

该命令会：
1. 导航到发布页
2. 点击"写长文" tab
3. 点击"新的创作"
4. 填写标题和正文
5. 点击"一键排版"
6. 返回 JSON 包含 `templates` 列表

### Step B.4: 选择排版模板

通过 `AskUserQuestion` 展示可用模板列表，让用户选择：

```bash
python scripts/cli.py select-template --name "用户选择的模板名"
```

### Step B.5: 进入发布页

```bash
# 点击下一步，填写发布页描述（正文摘要，不超过 1000 字）
python scripts/cli.py next-step \
  --content-file /tmp/xhs_description.txt
```

注意：发布页的描述编辑器是独立的，需要单独填入内容。如果描述超过 1000 字，脚本会自动截断到 800 字。

### Step B.6: 用户确认并发布

```bash
# 用户在浏览器中确认预览后
python scripts/cli.py click-publish
```

## 处理输出

- Exit code 0：成功。输出 JSON 包含 `success`, `title`, `images`/`video`/`templates`, `status`。
- Exit code 1：未登录，提示用户先登录（参考 xhs-auth）。
- Exit code 2：错误，报告 JSON 中的 `error` 字段。

### 视频剪辑工作流

当需要从录屏素材制作小红书视频笔记时，参见 **[references/video-editing-workflow.md](references/video-editing-workflow.md)**：
- ffmpeg concat demuxer 拼接（稳定，避免 filter_complex 音视频不匹配）
- 自动截取封面图（--video-cover 必需）
- 精华片段选取策略
- 飞书预览 + 小红书发布完整命令

### HyperFrames 视频案例场景（S5）设计

当视频需要「真实案例」「热点故事」来增强说服力时，参见 **[references/hyperframes-video-case-study.md](references/hyperframes-video-case-study.md)**：
- S5 场景设计公式（案例标签+大标题+数据卡片+金句）
- HTML/CSS/GSAP 完整模板（复制即用）
- 已验证的案例库和 Codex 出图 Prompt
- 时间轴安排：S5 放最后作为「最终一击」

### 小红书热点选题研究

当用户要求找热点题材、选爆款方向时，参见 **[references/xhs-hot-topic-research.md](references/xhs-hot-topic-research.md)**：
- 5 大选题方向（平台事件/赚钱/数据冲击/人设/细分热点）
- 创作者后台数据获取方法（CDP 操作）
- 人设故事公式（最高转化率模板）
- 搜索引擎全挂时的备选方案

### 🆕 图文模式：AI 生成配图工作流（2026-05-09 实测）

当用户说"算了按图片来介绍吧"/"生成图片来发"等从视频切换到图文模式时：

#### 方案选择优先级

| 优先级 | 方案 | 可行性 | 质量 |
|--------|------|--------|------|
| 1️⃣ | **Codex image_gen 生成封面+内容图** | ✅ 稳定可用 | ⭐⭐⭐⭐⭐ 9/10 |
| 2️⃣ | 微信开发者工具 CDP 截图 | ❌ 不可靠 | — |
| 3️⃣ | 用户提供的现有图片 | ✅ 直接使用 | 取决于素材 |

#### 方案1：Codex 生成小红书风格封面图（推荐 ✅）

**实测效果：9/10 分，黑金科技风，信息密度高但不杂乱。**

完整调用方式参见 **[codex-image-gen](../creative/codex-image-gen)** 技能的「社交媒体封面图」章节。

核心要点：
- 使用 `pty=True` 启动 Codex（必须！）
- Prompt 中明确指定：**3:4 竖屏比例、中文平台美学、中心辐射式构图**
- 关键元素：产品截图居中 + 技术栈图标环绕 + 中文大字标题 + 卖点口号
- 配色建议：深色底（#1a1a2e）+ 金色高光（#FFD700）= 小红书爆款视觉
- 生成后用 `vision_analyze` 验证文字可读性，再发飞书让用户确认

**Prompt 模板（已验证 9/10）：**
```
Create a Xiaohongshu (Little Red Book) cover image for a post about '<主题>'.

STYLE: Modern tech illustration, warm color palette (purple #1a1a2e + gold #FFD700 + white),
Chinese social media aesthetic, eye-catching thumbnail format (3:4 vertical ratio).

CONTENT TO VISUALIZE (must include ALL elements):
Central visual: <产品核心画面>
Surrounding elements: <技术实现相关图标，环绕排列>
Text overlay (Chinese, bold, modern font):
Main title: '<主标题>'
Subtitle: '<副标题/卖点>'
Small tag: '<价值承诺>'

MOOD: Exciting, futuristic but accessible.
Quality: Professional illustration, suitable for social media viral content.
Use image_gen tool.
```

#### 批量生成多张配图的实操模式（2026-05-09 验证）

当需要为图文笔记生成 **N 张不同场景的配图** 时：

**顺序队列模式（唯一可靠方式）：**
```
启动图1 → wait完成 → find最新png → 复制到输出目录 → 启动图2 → ...
```
每张图独立一个 Codex 进程，串行执行。不要并行启动多个——API 连接会冲突。

**查找最新生成图片的方法：**
```bash
# 用参考文件的时间戳找更新的图片
find ~/.codex/generated_images -name "*.png" -newer /path/to/previous_image.png -type f

# 或按目录修改时间找最新的
ls -lt ~/.codex/generated_images/ | head -3
# 最新目录下就是刚生成的图
ls ~/.codex/generated_images/<latest-dir>/*.png
```

**Codex 进程管理要点：**
- 每张图耗时约 3-5 分钟，消耗 ~20K tokens
- 启动后用 `process wait` 轮询，每次 clamped 60s
- 若日志出现 `tls handshake eof` + `Reconnecting... 5/5`：**必须 kill 进程重新启动**
- 进程退出后检查新目录是否创建：`ls -lt ~/.codex/generated_images/ | head -3`
- 图片路径格式：`~/.codex/generated_images/<session-id>/ig_<hex>.png`

**用户关键偏好 — 真机截图处理：**
> 用户原话：「不是替换，是增加」
>
> 当用户提供真实截图（如小程序真机录屏/手机拍照）时：
> - ❌ 不要删除已有的 AI 生成配图去「替换」
> - ✅ 将真机截图作为**额外一张**追加到配图列表末尾
> - 真机截图比 AI 生成图更有说服力（真实性证明），通常放在最后一张作为「实锤」

**本次实测成功的 8 张配图结构（模板）：**
| # | 类型 | 内容 | 来源 |
|---|------|------|------|
| 1 | 封面 | 主题海报（产品居中+技术图标环绕） | Codex |
| 2-6 | 场景图 | 各功能页面的 AI 示意图 | Codex（每张独立 prompt）|
| 7 | 架构图 | 技术链路流程图 | Codex |
| 8 | 真机截图 | 实际产品截图（新增！） | 用户拍摄 |

### 🆕 实测经验（2026-05-09）

#### 图文配图批量生成工作流（已验证 ✅）
当用户要求「按剧本生成图片」发小红书图文时：
1. **按文案拆分场景** → 每个关键画面一张图（封面+各功能页+架构图+真机截图）
2. **统一视觉风格**：暗夜紫 #1a1a2e + 香槟金 #FFD700 + 星尘粒子 + 3:4竖版
3. **Codex 逐张生成**（pty=True，每张~3-5分钟），保存到统一目录 `/tmp/lark-send/xhs_images/`
4. **真机截图作为最后一张**（用户原话：「加入这个」= 增加，不是替换！❌ 不要删除已有图）
5. 全部生成完 → 批量发飞书预览 → 用户确认 → 发布

#### 图片管理铁律（用户纠正）
> 用户明确说「不是替换，是增加」—— 当用户提供新截图/新素材时，**追加到图片列表末尾**，不要删除已有配图。除非用户明确说「替换」「不用那张了」。

#### 发布通道实测结果（2026-05-09 更新）

| 通道 | 结果 | 说明 |
|------|------|------|
| `browser_navigate` → xiaohongshu.com | ❌ IP风险 300012 | Browser工具的Chrome实例被标记 |
| `browser_navigate` → creator.xiaohongshu.com | ⚠️ 可打开但需登录 | 登录表单的input需用JS Console操作 |
| `python scripts/cli.py fill-publish` | ⚠️ 需Bridge扩展 | Bridge未连接时失败，连上后可用 |
| **CDP 手动填验证码登录** | ❌ **用户明确拒绝** | 用户原话："不要这个途径""用技能"。验证码过期快(~60s)，手动中继不可行 |
| **white0dew/XiaohongshuSkills** | ✅ **已验证成功** | 纯 CDP，无需扩展。8图+标题+正文+16标签全部填充成功 |
| **用户Chrome + Bridge + CLI** | ✅ 最佳 | 走用户正常IP，Bridge 连上时最稳定 |

**通道选择优先级（2026-05-09 实测确认）：**
1. **XiaohongshuSkills（纯 CDP）** → 最可靠，无依赖，已验证 ✅
2. Bridge CLI 能连上 → 用本技能 `cli.py`
3. 都不行 → 让用户扫码登录后重试
4. ❌ 不要尝试 CDP 手动填验证码（用户明确拒绝）

#### ⚠️ 正文1000字硬限制（2026-05-09 实测踩坑 #1 重要！）

**这是本次发布最大的坑，没有任何错误提示！**

| 现象 | 详情 |
|------|------|
| 超限后点「发布」 | **按钮完全没反应**，不报错、不弹窗、不变色 |
| 页面底部提示 | 「正文最多支持1000字」（小字，在编辑器下方） |
| 根因 | 小红书 Creator 平台图文笔记正文上限 = **1000字**（UTF-16编码单位） |

**正确做法：**
```bash
# 发布前务必检查正文字数
wc -m /tmp/xhs_content.txt
# 必须 ≤ 1000，建议 ≤ 900 留余量
```

**压缩策略（2026-05-09 验证）：**
- 原文 1628字 → 压缩到 731字 → 发布成功
- 保留：核心故事线 + 关键数据 + 金句结尾
- 删除：冗余描述、重复强调、过度细节
- 标签不算入正文字数（标签在正文末尾，系统单独解析）

**检测方法：**
```python
# 通过 CDP 检查编辑器当前字数
js = "document.querySelector('.tiptap.ProseMirror').textContent.length"
# 返回值 > 1000 则无法发布
```

#### publish_pipeline.py 参数陷阱（2026-05-09 实测踩坑 #2）

| 坑点 | 详情 |
|------|------|
| ❌ `--tags` 参数不存在 | 会报 `unrecognized arguments: --tags` |
| ✅ 标签从正文末尾提取 | 最后一行格式：`#标签1 #标签2 #标签3` |
| ✅ 正式发布参数 | 用 `--auto-publish` 或**去掉 `--preview`** |
| ❌ 文件名必须准确 | `img8_xxx.jpg` 实际可能叫 `img7_xxx.jpg` → `Image file not found` |

**正确命令模板：**
```bash
# 预览（只填不发布）✅
.venv/bin/python3 scripts/publish_pipeline.py \
  --host 127.0.0.1 --port 9222 --preview \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  --images /path/to/img1.png /path/to/img2.png ...

# 正式发布（去掉 --preview）✅
.venv/bin/python3 scripts/publish_pipeline.py \
  --host 127.0.0.1 --port 9222 \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  --images /path/to/img1.png /path/to/img2.png ...
# 注意：没有 --tags 参数！没有 --auto-publish 也行（默认就发布）
```

#### Chrome 多标签页迷宫（2026-05-09 实测踩坑 #3）

**Creator 平台会打开多个标签页，必须找到有内容的那个！**

```bash
# 列出所有标签页（注意：tab ID 是完整的，不是截断的）
curl -s http://127.0.0.1:9222/json | python3 -c "
import json,sys
for t in json.load(sys.stdin):
    if t.get('url',''):  # 过滤掉空标签
        print(f'{t[\"id\"]}  |  {t[\"title\"][:50]}  |  {t[\"url\"][:80]}')
"
```

**典型输出（本次实测）：**
```
93108A910FACBB2D1454280B252DC078  |  小红书创作服务平台  |  .../publish?from=tab_switch  ← 空白新建页
9C2EA948797928A478F3FC598A909AC1  |  小红书创作服务平台  |  .../publish               ← 视频上传页
B9B540502036240B0383CCC977D4A1C8  |  小红书创作服务平台  |  .../publish?from=tab_switch  ← ✅ 有内容的页！
970A5689C11CDF63  |  小红书创作服务平台  |  .../new/home              ← 首页
```

**识别正确标签的方法：**
```python
js = """(() => {
    const body = document.body.innerText.substring(0, 200);
    const pubBtn = document.querySelector('button.d-button-default.--color-static.bold');
    return JSON.stringify({
        snippet: body,
        btnText: pubBtn ? pubBtn.textContent.trim() : 'no btn',
        url: location.href
    });
})()"""
# 有内容的页：snippet 包含标题/正文文字，btnText = "发布"
# 空白页：snippet 只有导航栏文字，btnText = "上传视频"/其他
```

> ⚠️ **CDP 连接时 tab ID 必须完整！** `/json` 返回的是完整 ID（如 `93108A910FACBB2D1454280B252DC078`），截断后连不上（报 `No such target id`）。

#### 发布按钮点击方式（2026-05-09 实测踩坑 #4）

**JS click() 不够！需要 CDP 真实鼠标事件。**

| 方式 | 结果 |
|------|------|
| `btn.click()` (JS) | ❌ 无反应 |
| `elementFromPoint` + click | ❌ 点到了子元素 SPAN，仍无反应 |
| **CDP `Input.dispatchMouseEvent`** | ✅ 成功！ |

**正确的点击方法：**
```python
import json, websocket, time

ws = websocket.create_connection(
    'ws://127.0.0.1:9222/devtools/page/<FULL_TAB_ID>', timeout=15)

def cdp(method, params={}):
    ws.send(json.dumps({'id': 1, 'method': method, 'params': params}))
    return json.loads(ws.recv())

# 1. 滚动按钮到视野中心
cdp('Runtime.evaluate', {'expression': '''(() => {
    const btns = [...document.querySelectorAll('button')];
    const pub = btns.find(b => (b.textContent||'').trim() === '\\u53d1\\u5e03');
    if (pub) { pub.scrollIntoView({block: 'center'}); return 'ok'; }
    return 'not found';
})()'''})
time.sleep(1)

# 2. 获取按钮中心坐标
r = cdp('Runtime.evaluate', {'expression': '''(() => {
    const btns = [...document.querySelectorAll('button')];
    const pub = btns.find(b => (b.textContent||'').trim() === '\\u53d1\\u5e03');
    if (!pub) return '{"error":"not found"}';
    const rect = pub.getBoundingClientRect();
    return JSON.stringify({x: rect.x+rect.width/2, y: rect.y+rect.height/2});
})()'''})
coords = json.loads(r['result']['result']['value'])

# 3. 真实鼠标事件序列
x, y = int(coords['x']), int(coords['y'])
cdp('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': x, 'y': y})
time.sleep(0.2)
cdp('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})
time.sleep(0.05)
cdp('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})

# 4. 等待结果（8秒左右）
time.sleep(8)

# 5. 验证：URL 含 &published=true 表示成功
r = cdp('Runtime.evaluate', {'expression': 'location.href'})
print('URL:', r['result']['result']['value'])
# 成功: https://creator.xiaohongshu.com/publish/publish?...&published=true
```

#### Tiptap ProseMirror 编辑器操作（2026-05-09 实测）

小红书正文编辑器是基于 **Tiptap（ProseMirror）** 的富文本编辑器。

**选择器：** `div.tiptap.ProseMirror` 或 `div.tiptap.ProseMirror-focused`

**清空内容：**
```javascript
const editor = document.querySelector('.tiptap.ProseMirror');
editor.focus();
document.execCommand('selectAll', false, null);
document.execCommand('delete', false, null);
```

**插入文本（分批避免太长）：**
```javascript
editor.focus();
document.execCommand('insertText', false, '第一段内容...');
// 分段插入，每段 ≤200 字符
```

**获取当前字数：**
```javascript
document.querySelector('.tiptap.ProseMirror').textContent.length
```

#### websocket-client 依赖（2026-05-09 实测）

XiaohongshuSkills 的 venv **默认不包含 websocket-client**，需要手动安装：
```bash
/tmp/XiaohongshuSkills/.venv/bin/pip install websocket-client -q
```
否则 `import websocket` 会报 `ModuleNotFoundError`。

#### 完整发布工作流（2026-05-09 端到端验证 ✅）

```
┌─────────────────────────────────────────────────────┐
│  第0步：环境准备                                      │
│  • Clone XiaohongshuSkills + pip install             │
│  • 启动 Chrome --remote-debugging-port=9222          │
│  • pip install websocket-client（venv内）            │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│  第1步：扫码登录                                      │
│  • cdp_publish.py get-login-qrcode                   │
│  • base64→PNG→发飞书                                 │
│  • 用户扫 → 登录成功                                 │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│  第2步：准备素材                                      │
│  • 标题 ≤20字（UTF-16计算）                           │
│  • 正文 ≤1000字！（wc -m 检查）                      │
│  • 标签写在正文末尾 #tag1 #tag2                       │
│  • 图片准备好绝对路径                                  │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│  第3步：预览填充（--preview）                         │
│  • publish_pipeline.py --preview ...                 │
│  • 自动完成：上传图片 + 填标题 + 填正文 + 选标签       │
│  ⚠️ 没有 --tags 参数！标签从正文提取                  │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│  第4步：截图确认                                      │
│  • CDP Page.captureScreenshot                        │
│  • ⚠️ 数据在 r["result"]["data"] 不在 r["data"]      │
│  • 发飞书让用户看                                     │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│  第5步：用户确认 → 正式发布                            │
│  方式A：去掉 --preview 重跑 pipeline（推荐）          │
│  方式B：CDP 直接点发布按钮（见上方点击方法）           │
│  • 验证 URL 含 &published=true                       │
└─────────────────────────────────────────────────────┘
```

#### 🔧 备选方案：white0dew/XiaohongshuSkills（纯 CDP，无需扩展）⭐ **已验证可用 ✅**

当 Bridge 方案不可用时（Chrome 禁扩展、Bridge 连不上），使用 **纯 CDP 发布工具**作为替代。

**项目地址**：https://github.com/white0dew/XiaohongshuSkills （⭐2.7K，2026-05-09 更新）

**2026-05-09 实测成功：** 8张图片 + 标题 + 正文(1526字) + 16个话题标签全部自动填充成功！

**为什么推荐：**
- ✅ **纯 CDP 操控**，不需要任何浏览器扩展
- ✅ `publish_pipeline.py` 一键发布入口
- ✅ 支持 `--preview` 预览模式（只填不发布）→ 用户确认后再发布
- ✅ 支持 `--host/--port` 连接远程/已有 Chrome
- ✅ 支持 `--headless` 无头模式、多账号、定时发布
- ✅ 内置登录检测 + 二维码导出（`get-login-qrcode` 返回 base64 PNG）
- ✅ 自动检测正文最后一行的话题标签（`#标签1 #标签2` 格式）

**快速部署与使用（已验证 ✅）：**

```bash
# 1. Clone + 安装依赖
cd /tmp && git clone --depth 1 https://github.com/white0dew/XiaohongshuSkills.git
cd XiaohongshuSkills && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt -q

# 2. 检查登录状态（连接已有 Chrome）
.venv/bin/python3 scripts/cdp_publish.py --host 127.0.0.1 --port <CDP_PORT> check-login
# 输出: Login confirmed. / NOT LOGGED IN.

# 3. 获取二维码（未登录时）→ 返回 JSON 含 qrcode_base64 字段
.venv/bin/python3 scripts/cdp_publish.py --host 127.0.0.1 --port <CDP_PORT> get-login-qrcode

# 4. 预览模式发布（只填内容不点发布）✅ 已验证成功
.venv/bin/python3 scripts/publish_pipeline.py \
  --host 127.0.0.1 --port <CDP_PORT> --preview \
  --title-file /path/to/title.txt \
  --content-file /path/to/content.txt \
  --images "/path/to/img1.jpg" "/path/to/img2.jpg"
# 输出: FILL_STATUS: READY_TO_PUBLISH / Done.

# 5. 正式发布（去掉 --preview）
.venv/bin/python3 scripts/publish_pipeline.py \
  --host 127.0.0.1 --port <CDP_PORT> \
  --title-file /path/to/title.txt \
  --content-file /path/to/content.txt \
  --images "/path/to/img1.jpg" "/path/to/img2.jpg"
```

**实测输出示例（8图+标题+正文+16标签）：**
```
[pipeline] Step 2: Checking login status... Login confirmed.
[pipeline] Step 4: Filling form...
[cdp_publish] Image 1/8 submitted... Waiting for uploaded image previews: 1/1
[cdp_publish] Image 2/8 submitted... Waiting for uploaded image previews: 2/2
... (8/8 全部成功)
[cdp_publish] Title set.
[cdp_publish] Content set via selector: div.tiptap.ProseMirror
[pipeline] Step 4.1: Selecting 16 topic tag(s)...
[pipeline] Topic selected: #AI编程 ... #乔布斯
FILL_STATUS: READY_TO_PUBLISH
[pipeline] Preview mode is on, skipping publish click.
[pipeline] Done.
```

**核心命令速查：**

| 命令 | 用途 |
|------|------|
| `cdp_publish.py check-login` | 检查登录状态 |
| `cdp_publish.py get-login-qrcode` | 获取登录二维码（base64 PNG） |
| `cdp_publish.py login` | 弹窗扫码登录 |
| `publish_pipeline.py --preview ...` | 填写表单预览 |
| `publish_pipeline.py ...` | 填写 + 自动发布 |
| `chrome_launcher.py` | 启动/重启/关闭测试 Chrome |

**与本技能的关系：**
- 本技能 = **Bridge 扩展模式**（需要 Chrome 加载 XHS Bridge 扩展）
- XiaohongshuSkills = **纯 CDP 模式**（不需要扩展，更通用）
- **优先级**：Bridge 能连上时用本技能；连不上或环境受限时切换到 XiaohongshuSkills
- 两者的素材格式兼容（都支持 `--title-file`、`--content-file`、`--images`）
- **用户偏好**：遇到困难时用户会主动要求「去 GitHub 找技能」，优先找社区方案

#### 发布成功验证（2026-05-09 实测）

| 验证方式 | 成功标志 |
|----------|---------|
| URL 变化 | 包含 `&published=true` |
| 页面跳转 | 回到空白的新建发布页 |
| 草稿箱数量 | 不变（已发布的不会进草稿） |

**发布后的 CDP 截图：**
```python
# 发布成功后页面约 86KB（空白新建页）
# 发布前有内容的页约 368KB
# 如果截图大小骤降 + URL 变化 = 成功
```

---

## 📢 工作流 G：GitHub 开源项目 → 小红书推广发布（2026-05-10 新增 + 定位修正）

当用户说「把这个技能发到 GitHub」「包装一下开源」「做个能营销推广的」时触发。

### ⚠️⚠️ 核心定位（用户明确纠正，不可偏离！）

> **「AI 负责效率，你负责灵魂。」**

**用户原话（逐字记录）：**
1. 「注意突出提高效率部分，因为接口发布可能封禁，我们只是提高效率，管理，同时可以通过obsidian管理」
2. 「也可以一键发布，但是推荐人工必须审核，更带有自己思想」

**❌ 错误定位（不要这样写）：**
- ❌ 「全自动运营小红书」「一键批量发布」「替代人工」
- ❌ 「Agent 替代运营团队」「零人工干预」
- ❌ 任何暗示绕过平台风控/批量自动化操作的文案

**✅ 正确定位（必须这样写）：**
- ✅ **AI 提效工具箱** — 写文案、出配图、管内容库、辅助填表
- ✅ **Obsidian 原生集成** — 笔记即草稿，知识库即内容工厂
- ✅ **两种模式**：
  - 🚀 一键发布 → 日常低风险内容省时间
  - ✋ 审核发布（**推荐**）→ AI 出初稿 + 你注入思想 + 确认发布
- ✅ **人机协作** — AI 是副驾驶，你是机长
- ✅ **安全合规** — 开源可审计，不刷量不绕过风控

**为什么这样定位？**
- 平台接口发布可能触发封禁 → 不能主打「全自动发布」
- 用户的核心差异化是「自己的思想」→ 不是 AI 流水线内容
- Obsidian 是用户的工作习惯 → 必须作为核心卖点突出

### 完整链路

```
┌─────────────────────────────────────────────────────────────┐
│  第1步：确定归属                                             │
│  • 确认 repo 是用户自己的还是 fork 的                         │
│  • fork 的需要推到用户自己的 GitHub 账号下                     │
│  • 重新命名 repo（推荐：xhs-agent）                           │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  第2步：Codex 生成推广配图（2-3张）                           │
│  • 封面图：项目名 + 提效卖点 + 工作流卡片                      │
│  • 架构图：AI Agent → XHS-Agent → 小红书（CDP协议）          │
│  • 风格统一：暗色底(#0a0a1a) + 霓虹色线条 + 毛玻璃卡片        │
│  • 比例：3:4 竖版（适配小红书+GitHub social preview）         │
│  • 必须 pty=True，每张串行出图                                │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  第3步：重写 README（营销级）                                 │
│  • Hook 第一句：「AI 负责效率，你负责灵魂」                    │
│  • 核心卖点：提效 10x / Obsidian集成 / 两种发布模式           │
│  • 效率对比表：传统流程 vs XHS-Agent（每环节节省%）           │
│  • 安全设计章节：为什么推荐审核模式（注入思想的4个维度）       │
│  • Star History / License / Quick Start 缺一不可             │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  第4步：写小红书推广文案                                     │
│  • 标题 ≤20 字，带「开源」「AI」「提效」等关键词               │
│  • 正文结构：它是什么 → 能做什么 → 为什么需要人工审核 → 链接  │
│  • 必须强调：不是自动发帖机器人，是提效+管理工具              │
│  • 配图 = 第2步生成的推广图                                   │
│  • 正文 ≤1000 字！（wc -m 检查，建议 ≤800 留余量）           │
│  • 标签：#AI工具 #开源 #Obsidian #效率工具 #内容管理          │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  第5步：发布到小红书                                         │
│  • 使用 publish_pipeline.py 或 fill-publish + click-publish   │
│  • 发布后在评论区置顶 GitHub 链接                            │
└─────────────────────────────────────────────────────────────┘
```

### Codex 推广配图 Prompt 模板（已验证 9/10）

**封面图模板（2026-05-10 实测）：**
```
Use $image-gen.
Create a PREMIUM GitHub project cover image for 'XHS-Agent' (AI efficiency tool for Xiaohongshu).
STYLE: Apple product page quality. Dark premium background (#0a0a1a).
Neon cyan (#00D4FF) accent lines. Glassmorphism cards floating in 3D space.
Particle network background. 3:4 vertical ratio for social media.

CENTRAL VISUAL:
- A glowing AI agent brain icon at center (minimalist line-art)
- Surrounding arc of 6 floating glass cards showing workflow steps:
  ①AI写文案 ②AI出图 ③Obsidian同步 ④内容管理 ⑤辅助填表 ⑥你确认发布
- Each card: small icon + Chinese text

TEXT OVERLAY (Chinese):
Top: 「AI Agent 自动运营小红书」
Center-large: XHS-Agent
Bottom badge: ⭐ GitHub Open Source · Agent 提效 10x
Bottom-small: AI负责效率 · 你负责灵魂

MOOD: Premium, professional, developer-friendly.
Not "bot-like" or "automation spam". Think Vercel/Linear quality.
Premium tech illustration. Use image_gen tool.
```

**架构图模板（2026-05-10 实测 9/10）：**
```
Use $image-gen.
Create a PREMIUM architecture diagram for XHS-Agent.
STYLE: Dark futuristic tech diagram (#0a0a1a background).
Neon cyan (#00D4FF) lines connecting components. Glassmorphism cards.
3:4 vertical ratio.

ARCHITECTURE (clean flow diagram):
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│  AI Agent   │───▶│  XHS-Agent   │───▶│  Xiaohongshu     │
│  (Claude/   │    │  Skill Pack  │    │  Creator Platform│
│   Codex)    │    │              │    │                  │
└─────────────┘    └──────┬───────┘    └────────┬─────────┘
                          │                      │
                   ┌──────┼──────┐         ┌────┼────┐
                   ▼      ▼      ▼         ▼    ▼    ▢
                [发布]  [互动] [探索]   [图文][视频][长文]

TEXT:
Top: 「XHS-Agent 架构」
Bottom: Natural Language → AI Assist → You Confirm → Publish
Use image_gen tool.
```

### 小红书推广文案模板（定位修正版 2026-05-10）

**标题公式：** `[动作] + [AI/开源] + [提效结果]`
- ✅ 「开源小红书AI提效工具」（11字）
- ✅ 「AI帮我管小红书内容库」（11字）
- ✅ 「用Obsidian管理小红书」（14字）
- ❌ 「我开源了自动发帖Agent」（❌ 违反定位——不是自动发帖）

**正文结构（≤800字安全线）：**
```
第1段：它是什么（2-3句）
  「开源了一个小红书AI提效工具
   不是自动发帖机器人」

第2段：核心定位（关键！体现用户纠正的哲学）
  「它能帮你：10秒出文案初稿 / 1分钟AI生成配图 /
   Obsidian笔记直接变草稿 / 自动填表一键发布
   但真正涨粉的从来不是AI生成的流水线内容
   而是你注入的思想和独特视角」

第3段：两种模式（体现灵活性）
  「🚀 一键发布（日常分享省时间）
   ✋ 审核发布（精品内容注入灵魂）←推荐这个」

第4段：数据 + CTA
  「实测提效10x。支持Claude Code/Codex/Hermes。
   纯开源免费。GitHub搜 xhs-agent 或评论区要链接」

标签行（不占正文字数）：
#AI工具 #开源 #Obsidian #效率工具 #内容管理 #AI编程
```

### README 核心章节要点（营销级）

**必须包含的章节和卖点：**

1. **一句话 Slogan**：「AI 负责效率，你负责灵魂。」
2. **效率对比表**（每环节传统 vs Agent 时间对比，总计 ~10x）
3. **能力矩阵**（4大模块：内容创作 / 内容管理 / 数据洞察 / 发布辅助）
4. **Obsidian 集成**（独立大章，含 Mermaid 流程图 + 功能对照表）
5. **两种发布模式**（一键 vs 审核，含「为什么推荐审核」的4点解释）
6. **安全设计**（我们不做什么 + 我们专注什么）
7. **推荐工作流**（每日15分钟管理例程的时间线）
8. **免责声明**（仅供个人学习提效，遵守平台规则）

### 推广发布 Checklist

- [ ] Repo 已推到用户自己的 GitHub（不是 fork 或上游 repo）
- [ ] README 定位正确（❌ 没有「全自动发布」「零人工干预」等违规表述）
- [ ] README 包含 Obsidian 集成章节
- [ ] README 包含两种发布模式的说明
- [ ] 推广配图已生成（封面+架构，最少2张）
- [ ] 标题 ≤20 字（UTF-16 计算）
- [ ] 正文 ≤1000 字（wc -m 检查，建议 ≤800）
- [ ] 文案体现「AI提效+人工审核+注入思想」定位
- [ ] GitHub 链接在正文或评论区
- [ ] 发布后回复评论引导 Star

> **⚠️ 关键认知：** 小红书允许在正文中放 GitHub 链接（不会被屏蔽），但链接不可点击。最佳实践是**正文放完整 URL + 评论区置顶可点击版本**。
>
> **⚠️⚠️ 定位红线：** 绝不在任何公开物料（README/小红书文案/Twitter/知乎）中使用「自动发帖」「批量发布」「零人工」「替代运营」等可能触犯平台规则或误导用户的表述。本项目 = AI 辅助创作 + 内容管理工具，不是自动化 bot。

---

#### 本次发布完整参数记录（2026-05-09 实战存档）

**最终成功的命令：**
```bash
cd /tmp/XiaohongshuSkills && \
.venv/bin/python3 scripts/publish_pipeline.py \
  --host 127.0.0.1 --port 9222 \
  --preview \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  --images \
    "/tmp/lark-send/xhs_images/img1_cover.png" \
    "/tmp/lark-send/xhs_images/img2_feishu_chat.png" \
    "/tmp/lark-send/xhs_images/img3_homepage.png" \
    "/tmp/lark-send/xhs_images/img4_mbti_test.png" \
    "/tmp/lark-send/xhs_images/img5_entj_result.png" \
    "/tmp/lark-send/xhs_images/img6_synastry.png" \
    "/tmp/lark-send/xhs_images/img7_architecture.png" \
    "/tmp/lark-send/xhs_images/img7_real_homepage.jpg"
```

**素材清单：**
| # | 文件 | 内容 | 大小 |
|---|------|------|------|
| 1 | img1_cover.png | AI智能体主题海报 | 2.1MB |
| 2 | img2_feishu_chat.png | 飞书「马上推！」对话 | 1.8MB |
| 3 | img3_homepage.png | 四大模块首页 | 1.9MB |
| 4 | img4_mbti_test.png | MBTI 18道题界面 | 1.8MB |
| 5 | img5_entj_result.png | ENTJ乔布斯结果页 | 1.9MB |
| 6 | img6_synastry.png | 星盘交汇合盘 | 2.2MB |
| 7 | img7_architecture.png | 技术链路架构图 | 2.1MB |
| 8 | img7_real_homepage.jpg | 真机首页截图 | 951KB |

**正文压缩记录：**
- v1: 1628字 → ❌ 超限，发布按钮无反应
- v2: 781字 → ✅ 发布成功

**标题：** `AI智能体做塔罗小程序，飞书一发手机就弹出`（恰好20字 ✅）

**标签（16个）：** #AI编程 #智能体 #小程序开发 #独立开发 #塔罗 #MBTI #ENTJ #AI工具 #效率提升 #产品经理 #远程开发 #飞书 #微信小程序 #Codex #HermesAgent #乔布斯

#### 📱 登录方式选择：二维码 > 短信验证码 ⚠️ 重要

**实测结论（2026-05-09）：短信验证码手动中继不可行！用户明确要求用二维码。**

| 方式 | 可行性 | 用户态度 |
|------|--------|----------|
| ❌ 短信验证码手动中继 | **不可行** | 用户明确说："不要这个途径""用二维码吧" |
| ✅ **二维码扫码** | **可靠** | 用户首选，有效期长(2-5min)，扫完即登录 |
| ✅ Bridge + 已登录 Cookie | 最快 | 如果 Cookie 未过期 |

**为什么短信不可行：**
- 验证码有效期 ~60s，倒计时 60s 后才能重发
- 手动中继链路：发短信 → 用户看到 → 告诉 Agent → 填入 → 点登录 → 过期了
- 实测 3 次全部失败：「验证码不匹配」「验证码已过期」
- 即使加速操作，从点击发送到收到+填入+点登录，窗口太窄

**二维码登录完整流程（2026-05-09 已验证 ✅）：**

**方式 A：用 XiaohongshuSkills 的 `get-login-qrcode`（推荐）**
```bash
# 获取二维码（自动切换到扫码模式 + 提取 base64）
.venv/bin/python3 scripts/cdp_publish.py --host 127.0.0.1 --port <CDP_PORT> get-login-qrcode
# 输出 JSON: {"qrcode_base64": "iVBORw0KGgo..."}
# 解码为 PNG → 发飞书 → 用户扫 → 登录成功
```

**方式 B：手动 CDP 提取二维码（备用，当 get-login-qrcode 不可用时）**
1. **切换到扫码模式**：点击登录表单右上角的二维码图标（`img.css-wemwzq`，64x64）
2. **提取真正的二维码图片**：页面中有多个 img 元素，找到 `naturalWidth === 196` 且 `src` 以 `data:image/png;base64,` 开头的那个（class=`css-1lhmg90`）
3. **保存并发送**：解码 base64 为 PNG 文件 → 通过飞书发送给用户
4. **等待扫码**：用户用小红书 App 扫码后，页面自动跳转到 Creator 发布页

> ⚠️ **不要混淆二维码元素！** 登录页有多个 img：
> - 128x128 图标（小红书 logo）→ ❌ 不是二维码
> - 196x196 真正的二维码（class css-1lhmg90）→ ✅ 这个才是
> - 288x288 背景/装饰图 → ❌ 不是二维码

5. **验证登录状态**：
```bash
.venv/bin/python3 scripts/cdp_publish.py --host 127.0.0.1 --port <CDP_PORT> check-login
# 输出: Login confirmed.
```

6. **继续发布流程**：登录确认后直接执行 `publish_pipeline.py`

> **⚠️ 不要再用 CDP 手动填手机号+验证码的方式登录。** 用户已明确拒绝此途径。除非能自动化接收短信（如接码平台 API），否则不要尝试。

#### ⚠️ Bridge 连接故障排查（2026-05-09 实测，已验证 ✅）

**根因：openclaw 的 Chrome 禁用了扩展！**

Browser 工具启动的 Chrome 实例带有 `--disable-extensions` 参数，导致 XHS Bridge 扩展**无法加载**。CLI 的 Bridge 协议依赖浏览器端扩展注入，所以永远连不上。

**诊断步骤（按顺序执行）：**

```bash
# 1. 检查 bridge_server 进程是否存活
ps aux | grep bridge_server | grep -v grep

# 2. 检查 bridge 是否真的在监听端口
lsof -p <bridge_pid> -i -P -n | grep LISTEN

# 3. 检查 Chrome 启动参数是否禁用扩展
ps aux | grep "Chrome.*remote-debugging" | grep -v grep | head -1 \
  | grep -o "\-\-disable-extensions"

# 4. 确认是 openclaw 的隔离 Chrome 还是用户正常 Chrome
ps aux | grep "Chrome.*user-data-dir" | grep -v grep | head -1 \
  | grep -o "user-data-dir=[^ ]*"
```

**僵尸 Bridge 处理流程：**
```bash
kill <old_bridge_pid> 2>/dev/null
cd /Users/li.qing/.hermes/skills/xiaohongshu-skills
.venv/bin/python3 scripts/bridge_server.py &
sleep 2 && lsof -i -P -n | grep python3 | grep LISTEN
```

**关键认知：**
- Bridge 是 **C/S 架构**：`bridge_server.py`（Python 端）+ Chrome 扩展（浏览器端）
- 只有两端都活着才能通信。server 僵尸 OR Chrome 禁扩展 → 都报「扩展未连接」
- **不要反复重试 CLI 命令**——如果 Chrome 有 `--disable-extensions`，重试 100 次也没用
- 正确做法优先级：**XiaohongshuSkills(纯CDP) > 用户手动扫码 > Bridge CLI**

---

### 🔧 CDP 直连 Chrome（备用方案，仅用于启动/截图/二维码提取）

当需要操控 Chrome 但 Bridge 不可用时使用。**注意：不要用此方式手动填验证码登录！** 用户已明确拒绝。

**Step 1: 安装 websocket-client 到 venv**
```bash
uv pip install --python /path/to/xiaohongshu-skills/.venv/bin/python3 websocket-client
```

**Step 2: 启动带扩展的 Chrome（关键参数！）**
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --remote-allow-origins="*" \          # ⚠️ 必须！否则 WebSocket 连接报 403
  --user-data-dir="/Users/li.qing/.hermes/chrome-xhs-profile" \
  --load-extension="/Users/li.qing/.hermes/skills/xiaohongshu-skills/extension" \
  --no-first-run \
  --no-default-browser-check \
  "https://creator.xiaohongshu.com/publish/publish" &>/dev/null &
```

> **⚠️ `--remote-allow-origins="*"` 是必须的！** 没有它会报：
> `WebSocketBadStatusException: Handshake status 403 Forbidden`

**Step 3: Python CDP 连接模板（含截图 + 二维码提取）**
```python
import json, time, base64, os, websocket

tabs = json.loads(__import__("urllib.request", fromlist=[""]).urlopen(
    "http://127.0.0.1:9222/json").read())
ws = websocket.create_connection(tabs[0]["webSocketDebuggerUrl"], timeout=30)
_id = [0]

def cdp(method, params=None):
    _id[0] += 1
    msg = {"id": _id[0], "method": method}
    if params: msg["params"] = params
    ws.send(json.dumps(msg))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == _id[0]: return resp

def js(expr):
    r = cdp("Runtime.evaluate", {"expression": expr})
    result = r.get("result",{}).get("result",{})
    if "exceptionDetails" in r.get("result",{}):
        return f"Error: {r['result']['exceptionDetails'].get('text','?')}"
    return result.get("value")

# ── 截图（注意 response 结构！）──
# ⚠️ CDP Page.captureScreenshot 返回 {id:N, result:{data:"base64..."}}
#    用 r.get("data") 会拿到 None/空！必须用 r["result"]["data"]
cdp("Page.bringToFront", {})
time.sleep(1)
r = cdp("Page.captureScreenshot", {"format": "png"})
b64 = r["result"]["data"]           # ← 正确取法
with open("/tmp/screenshot.png","wb") as f:
    f.write(base64.b64decode(b64))

# ── 切换到扫码模式 + 提取二维码 ──
# 1. 点击右上角二维码图标（img.css-wemwzq, 64x64）
js("document.querySelector('img.css-wemwzq')?.click()")
time.sleep(3)

# 2. 提取真正的二维码图片（196x196 那个，class css-1lhmg90）
qr_b64 = js("""(() => {
  for (const el of document.querySelectorAll('img')) {
    const w = el.naturalWidth || el.width;
    if (w === 196 && el.src?.startsWith('data:image')) return el.src.split(',')[1];
  }
  return null;
})()""")
if qr_b64:
    with open("/tmp/xhs_qrcode.png","wb") as f:
        f.write(base64.b64decode(qr_b64))
    # 发飞书让用户扫
    os.system("cp /tmp/xhs_qrcode.png /tmp/lark-send/ && cd /tmp/lark-send && "
              "lark-cli im +messages-send --chat-id <CHAT_ID> --image ./xhs_qrcode.png")
```

**⚠️ CDP 截图 Gotcha（2026-05-09 实测踩坑）：**
| 错误写法 | 结果 | 正确写法 |
|----------|------|----------|
| `r.get("data")` | **空/None** ❌ | `r["result"]["data"]` ✅ |
| `base64.b64decode(r.get("data",""))` | 0 字节文件 ❌ | `base64.b64decode(r["result"]["data"])` ✅ |

原因：websocket-client 解析 JSON 后，CDP 的 `{id, result: {data}}` 结构中 `data` 在 `result` 内部，不在顶层。

---

### Creator 平台登录坑点（2026-05-09 实测）

| 坑点 | 详情 | 解决 |
|------|------|------|
| **验证码过期快** | 验证码有效期很短，从发到填+登录要在 ~60s 内完成 | 收到后立即填入，不要等 |
| **按钮文字变化** | 首次点击后「发送验证码」→ 倒计时 Ns → 「重新发送」 | 匹配两个文字：`t==='发送验证码'\|\|t==='重新发送'` |
| **验证码不匹配/已过期** | 页面显示对应错误提示 | 必须重新发送，旧码作废 |
| **React input 不响应** | 直接赋值 `input.value='xxx'` 不触发 React 状态更新 | 必须用 `nativeInputValueSetter` + dispatchEvent |
| **CDP WebSocket 403** | 缺少 `--remote-allow-origins=*` 导致连接被拒 | 启动 Chrome 时加上该参数 |
| **用户说端口 7897** | 可能是代理端口（Clash），不是 Chrome CDP | `lsof -i :7897` 查看进程名确认 |

**⚠️ 端口识别经验：** 用户说「我本地 XX 端口」时，先用 `lsof -i :PORT \| grep LISTEN` 确认进程名。常见混淆：
- **7897** → 通常是 Clash/V2Ray 代理
- **9222/9229** → Chrome remote-debugging
- **18800** → openclaw Browser 工具的 Chrome
- **9333** → XHS Bridge server

#### Creator平台登录操作（通过Browser工具）
当需要在Creator平台登录时：
1. `browser_navigate` 到 `https://creator.xiaohongshu.com/publish/publish`
2. 页面可能有iframe或React渲染，`browser_snapshot` 可能显示空
3. 用 `browser_console` 查找input：`Array.from(document.querySelectorAll('input')).map(...)`
4. 通过JS填值+dispatchEvent：
   ```js
   const input = document.querySelectorAll('input')[index];
   input.value = '手机号';
   input.dispatchEvent(new Event('input', {bubbles: true}));
   ```
5. 点击发送验证码：用JS查找包含「发送验证码」文本的元素并click
6. 等用户反馈验证码

#### 方案2：微信开发者工具 CDP 截图（❌ 不推荐）

**2026-05-09 实测失败：**

```bash
# IDE Server 启动成功，端口 58332
script -q /dev/null "$CLI" open --project "$PROJECT" --appid "$APPID"
# 输出: ✔ IDE server started successfully, listening on http://127.0.0.1:58332

# 但 CDP 端点返回 404！
curl "http://127.0.0.1:58332/json"  # HTTP Error 404: Not Found
# 扫描 58000-58400 全范围也找不到 CDP endpoint
```

**根因分析：**
- 微信开发者工具 CLI 的 `open` 命令启动的 IDE Server **不暴露标准 Chrome DevTools Protocol 端点**
- `/json` 路径返回 404，说明这不是一个标准的 CDP 调试服务
- 即使 IDE Server 显示 started，也无法通过 HTTP API 获取页面列表或执行截图

**结论：不要尝试用 CDP 截取小程序界面。** 替代方案：
- 用用户提供的录屏/截图
- 用 Codex AI 生成示意图
- 让用户手动截图提供

## 常用参数

| 参数 | 说明 |
|------|------|
| `--title-file path` | 标题文件路径（必须） |
| `--content-file path` | 正文文件路径（必须） |
| `--images path1 path2` | 图片路径/URL 列表（图文必须） |
| `--video path` | 视频文件路径（视频必须） |
| `--tags tag1 tag2` | 话题标签列表 |
| `--schedule-at ISO8601` | 定时发布时间 |
| `--original` | 声明原创 |
| `--visibility` | 可见范围 |

## 失败处理

- **登录失败**：提示用户重新扫码登录并重试（参考 xhs-auth）。
- **图片下载失败**：提示更换图片 URL 或改用本地图片。
- **视频处理超时**：视频上传后需等待处理（最长 10 分钟），超时后提示重试。
- **标题过长**：自动缩短标题，保持语义。
- **页面选择器失效**：提示检查脚本中的选择器定义。
- **模板加载超时**：长文模式下模板可能加载缓慢，等待 15 秒后超时。
- **用户取消发布**：必须运行 `save-draft` 保存草稿，再告知用户已保存到草稿箱，不得直接关闭 tab。
