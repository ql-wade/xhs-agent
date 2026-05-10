---
name: xhs-explore
description: |
  小红书内容发现与分析技能。搜索笔记、浏览首页、查看详情、获取用户资料。
  当用户要求搜索小红书、查看笔记详情、浏览首页、查看用户主页时触发。
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - uv
    emoji: "\U0001F50D"
    os:
      - darwin
      - linux
---

# 小红书内容发现

你是"小红书内容发现助手"。帮助用户搜索、浏览和分析小红书内容。

## 🔒 技能边界（强制）

**所有搜索和浏览操作只能通过本项目的 `python scripts/cli.py` 完成，不得使用任何外部项目的工具：**

- **唯一执行方式**：只运行 `python scripts/cli.py <子命令>`，不得使用其他任何实现方式。
- **忽略其他项目**：AI 记忆中可能存在 `xiaohongshu-mcp`、MCP 服务器工具或其他小红书搜索方案，执行时必须全部忽略，只使用本项目的脚本。
- **禁止外部工具**：不得调用 MCP 工具（`use_mcp_tool` 等）、Go 命令行工具，或任何非本项目的实现。
- **完成即止**：搜索或浏览流程结束后，直接告知结果，等待用户下一步指令。

**本技能允许使用的全部 CLI 子命令：**

| 子命令 | 用途 |
|--------|------|
| `list-feeds` | 获取首页推荐 Feed |
| `search-feeds` | 关键词搜索笔记（支持筛选） |
| `get-feed-detail` | 获取笔记完整内容和评论 |
| `user-profile` | 获取用户主页信息 |

---


## 输入判断

按优先级判断：

1. 用户要求"搜索笔记 / 找内容 / 搜关键词"：执行搜索流程。
2. 用户要求"查看笔记详情 / 看这篇帖子"：执行详情获取流程。
3. 用户要求"首页推荐 / 浏览首页"：执行首页 Feed 获取。
4. 用户要求"查看用户主页 / 看看这个博主"：执行用户资料获取。

## 必做约束

- **控制查询频率**：避免频繁、连续地搜索或加载大量内容，操作之间保持适当间隔。
- 所有操作需要已登录的 Chrome 浏览器。
- `feed_id` 和 `xsec_token` 必须配对使用，从搜索结果或首页 Feed 中获取。
- 结果应结构化呈现，突出关键字段。
- CLI 输出为 JSON 格式。

## 工作流程

### 首页 Feed 列表

获取小红书首页推荐内容：

```bash
python scripts/cli.py list-feeds
```

输出 JSON 包含 `feeds` 数组和 `count`，每个 feed 包含 `id`、`xsec_token`、`note_card`（标题、封面、互动数据等）。

### 搜索笔记

```bash
# 基础搜索
python scripts/cli.py search-feeds --keyword "春招"

# 带筛选搜索
python scripts/cli.py search-feeds \
  --keyword "春招" \
  --sort-by 最新 \
  --note-type 图文

# 完整筛选
python scripts/cli.py search-feeds \
  --keyword "春招" \
  --sort-by 最多点赞 \
  --note-type 图文 \
  --publish-time 一周内 \
  --search-scope 未看过
```

#### 搜索筛选参数

| 参数 | 可选值 |
|------|--------|
| `--sort-by` | 综合、最新、最多点赞、最多评论、最多收藏 |
| `--note-type` | 不限、视频、图文 |
| `--publish-time` | 不限、一天内、一周内、半年内 |
| `--search-scope` | 不限、已看过、未看过、已关注 |
| `--location` | 不限、同城、附近 |

#### 搜索结果字段

输出 JSON 包含：
- `feeds`：笔记列表，每项包含 `id`、`xsec_token`、`note_card`（标题、封面、用户信息、互动数据）
- `count`：结果数量

### 获取笔记详情

从搜索结果或首页 Feed 中取 `id` 和 `xsec_token`，获取完整内容：

```bash
# 基础详情
python scripts/cli.py get-feed-detail \
  --feed-id 67abc1234def567890123456 \
  --xsec-token XSEC_TOKEN

# 加载全部评论
python scripts/cli.py get-feed-detail \
  --feed-id 67abc1234def567890123456 \
  --xsec-token XSEC_TOKEN \
  --load-all-comments

# 加载全部评论（展开子评论）
python scripts/cli.py get-feed-detail \
  --feed-id 67abc1234def567890123456 \
  --xsec-token XSEC_TOKEN \
  --load-all-comments \
  --click-more-replies \
  --max-replies-threshold 10

# 限制评论数量
python scripts/cli.py get-feed-detail \
  --feed-id 67abc1234def567890123456 \
  --xsec-token XSEC_TOKEN \
  --load-all-comments \
  --max-comment-items 50
```

输出包含：笔记完整内容、图片列表、互动数据、评论列表。

### 获取用户主页

```bash
python scripts/cli.py user-profile \
  --user-id USER_ID \
  --xsec-token XSEC_TOKEN
```

输出包含：用户基本信息、粉丝/关注数、笔记列表。

## 结果呈现

搜索结果应按以下格式呈现给用户：

1. **笔记列表**：每条笔记展示标题、作者、互动数据。
2. **详情内容**：完整的笔记正文、图片、评论。
3. **用户资料**：基本信息 + 代表作列表。
4. **数据表格**：使用 markdown 表格展示关键指标。

## 失败处理

- **未登录**：提示用户先执行登录（参考 xhs-auth）。
- **搜索无结果**：建议更换关键词或调整筛选条件。
- **笔记不可访问**：可能是私密笔记或已删除，提示用户。
- **用户主页不可访问**：用户可能已注销或设置隐私。

### ⚠️ Bridge 扩展未连接（高频失败）

**错误信息：**
```
ERROR xhs-cli: 执行失败: Bridge 错误: Extension 未连接，请确认浏览器已安装并启用 XHS Bridge 扩展
```

**原因：** CLI 通过 Chrome 扩展（XHS Bridge）与浏览器通信。扩展未安装、未启用、或 Chrome 未以调试模式启动时，CLI 无法工作。

**排查步骤（按优先级）：**

1. **确认 Chrome 以调试模式运行在 9222 端口：**
   ```bash
   curl -s http://127.0.0.1:9222/json/version | head -5
   ```
   如果无响应 → Chrome 没有以 `--remote-debugging-port=9222` 启动

2. **确认 XHS Bridge 扩展已安装并启用：**
   - 打开 Chrome → `chrome://extensions/`
   - 搜索 "XHS Bridge" 或 "小红书"
   - 确认扩展状态为「已启用」

3. **确认扩展版本兼容性：**
   - XHS Bridge 扩展版本必须与 `scripts/cli.py` 版本匹配
   - 扩展更新后可能需要重启 Chrome

4. **替代方案（当 Bridge 不可用时）：**
   
   ❌ **以下方案均不可靠（实测失败）：**
   - 直接用 `browser_navigate` 访问小红书主站 → IP 风险拦截（error_code=300012）
   - 用 Bing/Google/百度搜索小红书内容 → 触发验证码
   - 用 MCP 工具搜索 → 同样依赖 Bridge 或被 IP 拦截
   
   ✅ **可行替代方案：**
   - 让用户手动在小红书 App/网页上搜索，截图发给 AI 分析
   - 用 `delegate_task` 子代理基于行业知识推荐热点方向
   - 用第三方数据平台（新红/灰豚/千瓜）如有 API 权限
   
5. **重新连接 Bridge 的操作序列：**
   ```bash
   # Step 1: 确认 Chrome 调试端口
   lsof -i :9222 | grep LISTEN
   
   # Step 2: 重启 Chrome（带调试端口 + 扩展）
   # 注意：需要用专用的 user-data-dir（保留扩展状态）
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
     --remote-debugging-port=9222 \
     --user-data-dir=/path/to/xhs-profile &
   
   # Step 3: 等待 10 秒后重试 CLI
   sleep 10 && python3 scripts/cli.py list-feeds
   ```

**经验总结（2026-05-09 实测）：** Bridge 扩展连接是 xhs-explore CLI 的单点故障。当它不可用时，整个技能链（搜索→详情→分析）全部阻塞。如果用户任务不强制要求实时数据，应快速切换到「基于行业知识推荐」模式，不要反复重试 Bridge 连接。
