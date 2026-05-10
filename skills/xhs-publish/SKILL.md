---
name: xhs-publish
description: |
  小红书内容发布技能。支持图文/视频/长文发布、内容预览、标签管理。
  适用于：AI Agent（Claude Code/Codex/Hermes）辅助小红书内容创作与发布。
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
    emoji: "📝"
    os:
      - darwin
      - linux
---

# XHS-Publish — 小红书智能发布

用 AI Agent 辅助你在小红书发布内容。**你负责灵魂，AI 负责效率。**

## 核心定位

```
┌─────────────────────────────────────────────┐
│  AI 做的：写文案 · 出配图 · 管素材 · 填表单  │
│  你做的：审核 · 注入思想 · 点最终发布        │
└─────────────────────────────────────────────┘
```

- ✅ **提效工具** — 不是自动发帖机器人
- ✅ **人机协作** — AI 出初稿，你注入独特视角后发布
- ✅ **安全合规** — 用你自己的浏览器登录，操作透明可审计

---

## 快速开始（3步）

### 第1步：环境准备

```bash
# 克隆项目
git clone https://github.com/ql-wade/xhs-agent.git
cd xhs-agent

# 安装依赖
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 启动 Chrome（开启远程调试）
# macOS:
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 --remote-allow-origins="*" &
# Linux:
google-chrome --remote-debugging-port=9222 --remote-allow-origins="*" &
```

### 第2步：登录小红书

```bash
# 检查是否已登录
python3 scripts/cdp_publish.py --host 127.0.0.1 --port 9222 check-login

# 如果未登录，获取二维码扫码
python3 scripts/cdp_publish.py --host 127.0.0.1 --port 9222 get-login-qrcode
# → 输出 base64 二维码图片，用手机小红书 App 扫码即可
```

> 💡 **推荐二维码登录**。短信验证码有效期短（~60秒），手动中继容易过期。

### 第3步：发布内容

```bash
# 图文笔记
python3 scripts/publish_pipeline.py \
  --host 127.0.0.1 --port 9222 \
  --title-file ./title.txt \
  --content-file ./content.txt \
  --images ./img1.png ./img2.png

# 视频笔记（需要封面图）
python3 scripts/publish_pipeline.py \
  --host 127.0.0.1 --port 9222 \
  --title-file ./title.txt \
  --content-file ./content.txt \
  --video ./video.mp4 \
  --video-cover ./cover.jpg
```

**推荐先预览再发布：**

```bash
# 预览模式（只填不发布，在浏览器里确认）
python3 scripts/publish_pipeline.py \
  --host 127.0.0.1 --port 9222 --preview \
  --title-file ./title.txt \
  --content-file ./content.txt \
  --images ./img1.png ./img2.png

# 浏览器确认无误后，去掉 --preview 正式发布
```

---

## 内容格式规范

### 标题

| 规则 | 说明 |
|------|------|
| 长度限制 | ≤ 20 字符（UTF-16 计算：汉字=1，英文/数字每2个=1） |
| 计算示例 | `"开源小红书AI提效"` = 9字 ✅；`"Hello World Test"` = 8字 ✅ |

### 正文

| 规则 | 说明 |
|------|------|
| 长度限制 | **≤ 1000 字符**（超限后发布按钮无反应，不报错！） |
| 格式 | 普通文本，段落间空行分隔 |
| 标签 | 写在正文最后一行：`#标签1 #标签2 #标签3` |
| 标签说明 | 从正文末尾自动提取，不需要 `--tags` 参数 |

### content.txt 示例

```
这是正文第一段，介绍你的主题。

这是第二段，可以展开细节。

第三段放总结或行动号召。

#AI工具 #开源 #效率工具 #知识管理
```

> ⚠️ **检查正文字数**：`wc -m content.txt` 必须 ≤ 1000，建议 ≤ 800 留余量。

### 图片

| 规则 | 说明 |
|------|------|
| 格式 | jpg / png / webp |
| 路径 | 支持绝对路径或 URL（URL 自动下载） |
| 数量 | 最多 18 张 |
| 大小 | 单张 ≤ 10MB（建议 ≤ 2MB 上传更快） |

### 视频

| 规则 | 说明 |
|------|------|
| 格式 | mp4 / mov / quicktime |
| 封面图 | **必须**提供 `--video-cover`（可从视频截取） |
| 截取封面 | `ffmpeg -y -i video.mp4 -ss 00:03 -vframes 1 cover.jpg` |

---

## 发布模式

### 模式一：一步发布（快捷）

适合日常低风险内容，信任 AI 输出时直接发布：

```bash
python3 scripts/publish_pipeline.py \
  --host 127.0.0.1 --port 9222 \
  --title-file ./title.txt \
  --content-file ./content.txt \
  --images ./img1.png
```

### 模式二：分步发布（推荐）

适合精品内容，需要审核和修改：

```bash
# Step 1: 填充表单（不发布）
python3 scripts/cli.py fill-publish \
  --title-file ./title.txt \
  --content-file ./content.txt \
  --images ./img1.png ./img2.png

# Step 2: 在浏览器中预览确认
# → 此时可以手动修改标题/正文/调整图片顺序

# Step 3a: 确认无误 → 发布
python3 scripts/cli.py click-publish

# Step 3b: 要取消 → 先保存草稿！
python3 scripts/cli.py save-draft
```

> ⚠️ **取消时必须 `save-draft`**，直接关闭会丢失内容。

---

## 与 AI Agent 配合使用

### Claude Code

```bash
# 在 Claude Code 中调用
/subagent "帮我写一篇关于XX的小红书文案，然后用xhs-publish发布"
```

Agent 会自动：
1. 生成符合规范的标题 + 正文
2. 调用 Codex/DALL-E 生成配图
3. 执行 publish_pipeline.py 发布
4. 向你汇报结果

### Codex

```bash
cd your-project
codex exec "用 xhs-publish 技能发一篇小红书笔记，主题是：AI编程提效"
```

### Hermes Agent

技能加载后会自动识别「发小红书」「发布到小红书」等意图，触发完整发布流程。

### Obsidian 工作流

```
Obsidian 笔记 → AI 增强 → 小红书草稿 → 你审核 → 发布
```

1. 在 Obsidian 中写好笔记（YAML frontmatter + Markdown 正文）
2. 用 Agent 将笔记转为小红书格式（标题 ≤20字，正文 ≤1000字）
3. 自动生成配图
4. 预览确认 → 发布
5. 发布后的链接和数据回写到 Obsidian

---

## 常见问题

### Q: 登录过期了怎么办？

A: 重新执行 `get-login-qrcode` 扫码即可。登录状态缓存 12 小时。

### Q: 发布按钮点了没反应？

A: 最常见原因是**正文超过 1000 字**。检查方法：
```bash
wc -m content.txt   # 必须 ≤ 1000
```
压缩正文到 800 字以内再试。

### Q: 图片上传失败？

A: 检查：
- 文件路径是否正确（必须绝对路径）
- 图片格式是否支持（jpg/png/webp）
- 单张大小是否超 10MB
- 网络是否通畅（CDP 通过本地 Chrome 发请求）

### Q: 标签没有生效？

A: 不需要 `--tags` 参数。把标签写在正文最后一行：
```
正文内容...

#标签1 #标签2 #标签3
```
脚本会自动从末尾提取。

### Q: 如何定时发布？

A: 使用 `--schedule-at` 参数（ISO 8601 格式）：
```bash
--schedule-at "2026-05-10T20:00:00"
```
注意：定时需要保持 Chrome 运行和登录状态。

### Q: 支持多账号吗？

A: 支持。每个账号用不同的 Chrome user-data-dir：
```bash
--user-data-dir="/path/to/profile-2"
```
或者启动多个 Chrome 实例用不同端口。

### Q: Bridge 扩展是什么？必须装吗？

A: Bridge 扩展是可选增强功能（本项目 `extension/` 目录）。它能让 CLI 和浏览器通信更稳定。但如果你的 Chrome 无法加载扩展，**纯 CDP 模式也能正常工作**——这就是 `publish_pipeline.py` 的默认模式。

---

## 项目结构

```
xhs-agent/
├── README.md                    # 项目介绍与营销文档
├── SKILL.md                     # 本文件（使用指南）
├── LICENSE                      # MIT 开源协议
├── requirements.txt             # Python 依赖
├── pyproject.toml               # 项目配置
│
├── scripts/                     # 🔧 核心引擎
│   ├── publish_pipeline.py      # 主入口：一键发布流水线
│   ├── cdp_publish.py           # CDP 协议层（操控浏览器）
│   ├── cli.py                   # CLI 子命令（fill/click/save）
│   ├── chrome_launcher.py       # Chrome 生命周期管理
│   └── xhs/                     # 业务模块
│       ├── publish.py            # 图文发布逻辑
│       ├── publish_video.py      # 视频发布逻辑
│       ├── publish_long_article.py # 长文发布逻辑
│       ├── login.py              # 登录（二维码）
│       ├── search.py             # 搜索发现
│       ├── feeds.py              # 信息流
│       ├── cdp.py                # CDP 底层封装
│       └── selectors.py          # 页面选择器定义
│
├── skills/
│   ├── xhs-publish/             # 📝 发布技能（本技能）
│   │   ├── SKILL.md             #    Agent 调用指南
│   │   └── references/          #    参考文档
│   └── xhs-explore/             # 🔍 探索技能（热点发现）
│
├── extension/                   # 🌐 Chrome Bridge 扩展（可选）
│   ├── manifest.json
│   ├── background.js
│   └── content.js
│
└── assets/                      # 🎨 推广素材
    ├── cover_agent.png          #    GitHub 封面图
    └── architecture.png         #    架构图
```

---

## 安全与合规

| 原则 | 说明 |
|------|------|
| 本地优先 | 所有数据存储在你本地，Token 不经过第三方服务器 |
| 操作透明 | 通过 CDP 操控你自己的浏览器，每一步可见 |
| 人工决策 | 推荐审核模式 —— AI 准备，你做最终决定 |
| 平台遵守 | 不刷量、不绕过风控、不批量恶意操作 |
| 开源审计 | 全部代码可审查，无后门 |

---

## License

MIT © 2025 ql-wade

[GitHub](https://github.com/ql-wade/xhs-agent) · [Issues](https://github.com/ql-wade/xhs-agent/issues) · [Discussions](https://github.com/ql-wade/xhs-agent/discussions)
