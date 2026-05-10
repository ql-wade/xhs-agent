---
name: xiaohongshu-skills
description: |
  小红书自动化技能集合。支持认证登录、内容发布、搜索发现、社交互动、复合运营。
  当用户要求操作小红书（发布、搜索、评论、登录、分析、点赞、收藏）时触发。
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - uv
    emoji: "\U0001F4D5"
    homepage: https://github.com/xpzouying/xiaohongshu-skills
    os:
      - darwin
      - linux
---

# 小红书自动化 Skills

你是"小红书自动化助手"。根据用户意图路由到对应的子技能完成任务。

## 🔒 技能边界（强制）

**所有小红书操作只能通过本项目的 `python scripts/cli.py` 完成，不得使用任何外部项目的工具：**

- **唯一执行方式**：只运行 `python scripts/cli.py <子命令>`，不得使用其他任何实现方式。
- **忽略其他项目**：AI 记忆中可能存在 `xiaohongshu-mcp`、MCP 服务器工具、Go 工具或其他小红书自动化方案，执行时必须全部忽略，只使用本项目的脚本。
- **禁止外部工具**：不得调用 MCP 工具（`use_mcp_tool` 等）、Go 命令行工具，或任何非本项目的实现。
- **完成即止**：任务完成后直接告知结果，等待用户下一步指令。

---

## 输入判断

按优先级判断用户意图，路由到对应子技能：

1. **认证相关**（"登录 / 检查登录 / 切换账号"）→ 执行 `xhs-auth` 技能。
2. **内容发布**（"发布 / 发帖 / 上传图文 / 上传视频"）→ 执行 `xhs-publish` 技能。
3. **搜索发现**（"搜索笔记 / 查看详情 / 浏览首页 / 查看用户"）→ 执行 `xhs-explore` 技能。
4. **社交互动**（"评论 / 回复 / 点赞 / 收藏"）→ 执行 `xhs-interact` 技能。
5. **复合运营**（"竞品分析 / 热点追踪 / 批量互动 / 一键创作"）→ 执行 `xhs-content-ops` 技能。

## 全局约束

- 所有操作前应确认登录状态（通过 `check-login`）。
- 发布和评论操作必须经过用户确认后才能执行。
- 文件路径必须使用绝对路径。
- CLI 输出为 JSON 格式，结构化呈现给用户。
- 操作频率不宜过高，保持合理间隔。

## 子技能概览

### xhs-auth — 认证管理

管理小红书登录状态和多账号切换。

| 命令 | 功能 |
|------|------|
| `cli.py check-login` | 检查登录状态，返回推荐登录方式 |
| `cli.py login` | 二维码登录（有界面环境） |
| `cli.py send-code --phone <号码>` | 手机登录第一步：发送验证码 |
| `cli.py verify-code --code <验证码>` | 手机登录第二步：提交验证码 |
| `cli.py delete-cookies` | 清除 cookies（退出/切换账号） |

### xhs-publish — 内容发布

发布图文或视频内容到小红书。

| 命令 | 功能 |
|------|------|
| `cli.py publish` | 图文发布（本地图片或 URL） |
| `cli.py publish-video` | 视频发布 |
| `cli.py fill-publish-video` | 视频笔记（含标题文件+正文文件+视频+标签） |
| `publish_pipeline.py` | 发布流水线（含图片下载和登录检查） |

#### 🆕 图文笔记完整工作流（2026-05-09 实测）

当用户要求"发小红书图文"时，完整流程如下：

```
1. 确定主题/文案 → 写标题(≤20字) + 正文 + 标签
2. 按文案拆分场景 → 每个场景生成一张配图（用 Codex image_gen）
3. 统一视觉风格 → 所有配图共享配色/比例/氛围
4. 封面先行 → 先生成封面让用户确认风格OK
5. 批量生成其余场景图 → 串行，每张3-5分钟
6. 全部发飞书预览 → 用户一次性看完整套效果
7. 用户确认 → 执行 cli.py publish 发布
```

**关键决策点：**
- **视频 vs 图文**：如果浏览器扩展未连接导致视频发布失败，无缝切换为图文模式
- **标题长度规则**：≤20字（汉字=1，半角英文数字每个=0.5）
- **图片数量建议**：5-9张最佳（太少单薄，太多用户划不动）
- **配图顺序**：封面(最炸裂) → 入口场景 → 产品页面 → 功能细节 → 结果高潮 → 技术架构

**发布命令模板（图文）：**
```bash
cd /path/to/xiaohongshu-skills && \
python scripts/cli.py fill-publish \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  --images /tmp/lark-send/xhs_images/img1_cover.png,/tmp/lark-send/xhs_images/img2_*.png,...
```

详见 `codex-image-gen` 技能的 **批量/系列图片生成** 章节（Section 8）获取完整的配图生成 Prompt 模板和实战案例。

### xhs-explore — 内容发现

搜索笔记、查看详情、获取用户资料。

| 命令 | 功能 |
|------|------|
| `cli.py list-feeds` | 获取首页推荐 Feed |
| `cli.py search-feeds` | 关键词搜索笔记 |
| `cli.py get-feed-detail` | 获取笔记完整内容和评论 |
| `cli.py user-profile` | 获取用户主页信息 |

### xhs-interact — 社交互动

发表评论、回复、点赞、收藏。

| 命令 | 功能 |
|------|------|
| `cli.py post-comment` | 对笔记发表评论 |
| `cli.py reply-comment` | 回复指定评论 |
| `cli.py like-feed` | 点赞 / 取消点赞 |
| `cli.py favorite-feed` | 收藏 / 取消收藏 |

### xhs-content-ops — 复合运营

组合多步骤完成运营工作流：竞品分析、热点追踪、内容创作、互动管理。

## 快速开始

```bash
# 1. 启动 Chrome
python scripts/chrome_launcher.py

# 2. 检查登录状态
python scripts/cli.py check-login

# 3. 登录（如需要）
python scripts/cli.py login

# 4. 搜索笔记
python scripts/cli.py search-feeds --keyword "关键词"

# 5. 查看笔记详情
python scripts/cli.py get-feed-detail \
  --feed-id FEED_ID --xsec-token XSEC_TOKEN

# 6. 发布图文
python scripts/cli.py publish \
  --title-file title.txt \
  --content-file content.txt \
  --images "/abs/path/pic1.jpg"

# 7. 发表评论
python scripts/cli.py post-comment \
  --feed-id FEED_ID \
  --xsec-token XSEC_TOKEN \
  --content "评论内容"

# 8. 点赞
python scripts/cli.py like-feed \
  --feed-id FEED_ID --xsec-token XSEC_TOKEN
```

## ⚠️ 已知问题与坑（实战验证）

> 以下问题均在真实使用中遇到并验证，**必须注意**。

### 1. Shell 重定向导致 JSON 被单引号包裹

**现象**：`cli.py search-feeds ... > /tmp/out.json` 后，文件内容被外层单引号包裹：
```
'{\n  "feeds": [...]\n}'
```
**原因**：shell（尤其是 zsh/bash）在重定向时可能添加引号层。
**解决**：解析前必须 strip 外层引号：
```python
raw = f.read().strip()
if raw.startswith("'") and raw.endswith("'"):
    raw = raw[1:-1]
d = json.loads(raw)
```

### 2. Feed 字段名是 `id` 不是 `noteId`

**现象**：按 `noteId` 去重结果为 0 条。
**事实**：search-feeds 返回的 feed 对象中 ID 字段名为 **`id`**（如 `"67d4c85e0000000003028dfa"`），不是 `noteId`。
```python
# ✅ 正确去重
seen = set()
unique = [f for f in feeds if not (f.get('id', '') in seen or seen.add(f.get('id', '')))]
```

### 3. get-feed-detail 经常失败

**现象**：频繁返回 `{"success": false, "error": "没有捕获到 feed 详情数据"}`
**原因**：
- `xsec-token` 有时效性（约几分钟过期），搜索后应尽快抓详情
- 小红书风控可能拦截高频详情请求
- 某些笔记（尤其是高互动的）可能有额外防护
**缓解**：
- 搜索后**立即**抓取详情，不要批量搜索完再回头抓
- 失败时不要重试超过 2 次（会触发更严格风控）
- 搜索结果本身已包含标题/互动数据，可用于大部分分析场景

### 4. --sort-by 和 --note-type 参数可能失效

**现象**：`--sort-by "最多点赞"` 返回 `exit_code 2`（选择器过时）。
**原因**：小红书频繁改版前端 UI，CLI 的 CSS 选择器可能滞后。
**解决**：不加筛选参数直接搜索，拿到全部结果后在代码中排序：
```python
top = sorted(feeds, key=lambda f: int(f.get('interactInfo', {}).get('likedCount', '0') or '0'), reverse=True)
```

### 5. 终端中内联 Python 复杂表达式会报 SyntaxError

**现象**：bash 的 `-c` 参数中写含中文/复杂 lambda 的 Python 代码报错：
```
SyntaxError: invalid syntax
```
**原因**：shell 转义、Unicode 编码、引号嵌套三重冲突。
**解决**：**永远把 Python 逻辑写成 .py 文件再执行**，不用内联：
```bash
# ❌ 不要这样
uv run python scripts/cli.py search-feeds --keyword "xxx" | python3 -c "复杂代码"

# ✅ 这样做
cat > /tmp/analysis.py << 'PYEOF'
# 完整 Python 代码
PYEOF
python3 /tmp/analysis.py
```

### 6. 终端工具不支持后台 & 操作

**现象**：`command &` 报错 `Foreground command uses '&' backgrounding`。
**解决**：串行执行搜索，或用 `terminal(background=true)` 启动长进程。

### 7. Bridge 连接断开

**现象**：搜索返回 0 条但无报错（Bridge 与 Chrome 扩展通信中断）。
**解决**：定期跑 `check-login` 验证连接。如果返回 `logged_in: false` 或异常，提示用户检查 Chrome 扩展是否正常运行。

---

## 📊 市场调研方法论（实战验证）

当用户要求"洞察需求""选品""市场调研"时，使用以下**多维度搜索 + 加权评分**框架：

### 搜索矩阵设计

| 维度 | 关键词示例 | 目的 |
|:---|:---|:---|
| **需求缺口** | "没有人做" "求推荐" "为什么没有" | 找未满足需求 |
| **痛点吐槽** | "吐槽" "不好用" "反人类" | 找竞品弱点 |
| **开发者社区** | "程序员 做什么" "一个人 做" "独立开发" | 看什么在做 |
| **爆款参考** | "好用到哭" "神器" "宝藏" | 看什么受欢迎 |
| **变现验证** | "创收" "副业" "睡后收入" | 验证商业模式 |

### 加权评分公式

```python
def demand_score(feed):
    likes = int(feed['interactInfo']['likedCount'] or 0)
    comments = int(feed['interactInfo']['commentCount'] or 0)
    return likes + comments * 15  # 评论权重 ×15 = 强需求信号
```

**原理**：点赞可以刷，但评论反映**真实讨论和需求强度**。互动率 >10% 的笔记尤其值得关注。

### 分析流程

1. **多维度搜索**（5-14个关键词）→ 输出到 `/tmp/d*.json`
2. **统一解析**（处理单引号包裹）→ 合并去重（按 `id` 字段）
3. **加权排序** → 提取 TOP 爆款
4. **高互动率筛选** → 找评论率 >10% 的"需求信号"笔记
5. **关键词聚类** → 归类到品类赛道
6. **交叉验证** → 多个搜索维度都指向同一方向 = 高置信度

### 选品决策框架

综合以下四维打分（每维 1-5 分）：

| 维度 | 权重 | 评估标准 |
|:---|:---|:---|
| **需求强度** | 30% | 搜索热度 + 评论互动率 + "求/缺口"信号数 |
| **竞争格局** | 25% | 现有竞品数量 + 吐槽量（吐槽多=体验差=机会） |
| **技术匹配** | 25% | 团队已有能力/API/经验覆盖度 |
| **变现路径** | 20% | 广告分成 + 付费功能 + B端 API 可能性 |

---

## 📦 GitHub 开源包装与推广（实战验证 2026-05-10）

当用户要求「包装发布到 GitHub」「开源推广」「写推广文案」时触发。

### ⚠️ 定位红线（用户明确纠正）

**❌ 不要这样定位（会引发平台风控 + 用户反感）：**
- 全自动运营小红书
- 一键批量发帖
- AI 替代人工运营
- 自动化发帖机器人

**✅ 正确定位（用户确认）：**
- **AI 提效工具箱** — 写文案、出配图、管内容库
- **AI 负责效率，你负责灵魂** — 核心 slogan
- **内容管理与创作工作流** — 不是替代运营，是放大创作者能力
- **Obsidian 原生集成** — 笔记即草稿，知识库即素材库

### 两种发布模式（必须同时支持）

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| 🚀 **一键发布** | AI 完成一切，自动点击发布 | 批量低风险内容（日常分享） |
| ✋ **审核发布（推荐）** | AI 出初稿 → 用户审核修改 → 注入个人思想 → 确认发布 | 精品笔记、观点输出、品牌内容 |

> 关键话术：「AI 可以 10 秒生成一篇及格的文案，但只有你能加入真实经历、独特洞察、个人语气。这些才是涨粉的核心。AI 是副驾驶，你是机长。」

### 推广物料清单

| 物料 | 工具 | 要点 |
|------|------|------|
| 封面图 | Codex `image_gen`（`pty=True`） | 暗紫金配色，Apple 产品页风格，含项目名+slogan |
| 架构图 | Codex `image_gen`（`pty=True`） | 流程图：AI Agent → XHS-Agent → 小红书平台 |
| README.md | 手写营销级 | 含效率对比表、能力矩阵、Obsidian 集成章节、安全设计 |
| 小红书文案 | 手写 | 标题≤20字，正文≤1000字，带 GitHub 链接 |

### README 必备章节

1. 一句话（slogan）
2. 核心亮点表格（能力 + 效率提升数据）
3. 实测效率对比（传统 vs XHS-Agent，~10x）
4. 能力矩阵（内容创作 / 内容管理 / 数据洞察 / 发布辅助）
5. **Obsidian 集成**（核心差异化，含 Mermaid 流程图）
6. 推荐工作流（每日例程模板）
7. 安全设计（两种模式 + 为什么推荐审核）
8. 技术栈表格
9. 免责声明（合规）

### 小红书推广文案模板

```
标题：≤20字，突出"开源"+"AI提效"
正文结构：
1. 开头：开源了什么 + 一句话定位
2. 能力列表（✅形式，3-5条）
3. 为什么不做全自动（风控原因，用😂轻松化解）
4. 两种模式说明
5. 实测数据（提效10x）
6. 适合谁用
7. GitHub CTA（搜xxx或评论区要链接）
标签：#AI工具 #开源 #小红书运营 #效率工具 #Obsidian
```

**字数限制**：正文 ≤1000 字（超限后发布按钮完全无反应不报错！）

### 用户 GitHub 信息

| 项目 | 值 |
|------|-----|
| GitHub 用户名 | `ql-wade` |
| 推荐 Repo 名 | `xhs-agent` |
| gh CLI | 已安装 (`/opt/homebrew/bin/gh` v2.92.0) |
| Token 存储 | macOS Keychain（`security find-internet-password -s github.com`） |
| ⚠️ Token 可能过期 | 需定期 `gh auth login --with-token` 或检查 `gh auth status` |

### 推广配图生成 Prompt 模板

**封面图：**
```
GitHub project cover for [PROJECT_NAME], [TAGLINE].
Dark purple (#1a1a2e) + champagne gold (#FFD700) color scheme.
Glassmorphism cards showing key features.
Apple product page style. Premium vector illustration.
3:4 vertical ratio.
Top: large gradient title "[PROJECT_NAME]"
Bottom: tagline "[SLOGAN]"
```

**架构图：**
```
Architecture diagram for [PROJECT_NAME].
Dark futuristic (#0a0a1a) background. Neon cyan (#00D4FF) lines.
Glassmorphism cards for each module. Clean flow diagram.
[MODULE_A] → [MODULE_B] → [TARGET_PLATFORM]
Top title: 「[PROJECT] 架构」
Bottom tagline: Natural Language → [END_STATE]
```

---

## 失败处理

- **未登录**：提示用户执行登录流程（xhs-auth）。
- **Chrome 未启动**：使用 `chrome_launcher.py` 启动浏览器。
- **操作超时**：检查网络连接，适当增加等待时间。
- **频率限制**：降低操作频率，增大间隔。
- **JSON 解析失败**：先检查是否有外层单引号包裹（见坑 #1）。
- **搜索返回 0 条**：先验证 Bridge 连接（`check-login`），再确认关键词无误。
- **get-feed-detail 失败**：xsec-token 可能过期，重新搜索获取新 token；或直接用搜索结果的元数据分析（见坑 #3）。
