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
    emoji: "🔍"
    os:
      - darwin
      - linux
---

# XHS-Explore — 小红书内容发现

搜索热门内容、分析竞品笔记、研究用户画像。**为你的创作提供数据支撑。**

## 核心能力

| 能力 | 说明 | 典型场景 |
|------|------|----------|
| 🔍 **搜索笔记** | 按关键词搜索，支持多维度筛选 | 找热点、调研竞品 |
| 📰 **首页推荐** | 获取个性化 Feed 流 | 发现趋势话题 |
| 📖 **笔记详情** | 完整正文 + 图片 + 全部评论 | 深度分析爆款 |
| 👤 **用户主页** | 博主资料 + 笔记列表 + 粉丝数据 | 竞品分析 |

---

## 快速开始

### 前提条件

与 [xhs-publish](../xhs-publish/SKILL.md) 共享环境：
- Chrome 以调试模式运行在 `9222` 端口
- 已登录小红书（参考 xhs-publish 的「第2步：登录」）

### 搜索笔记

```bash
# 基础搜索
python3 scripts/cli.py search-feeds --keyword "AI工具"

# 按点赞排序，只要图文
python3 scripts/cli.py search-feeds \
  --keyword "AI效率" \
  --sort-by 最多点赞 \
  --note-type 图文

# 一周内发布的最新内容
python3 scripts/cli.py search-feeds \
  --keyword "独立开发" \
  --sort-by 最新 \
  --publish-time 一周内
```

### 筛选参数一览

| 参数 | 可选值 | 说明 |
|------|--------|------|
| `--sort-by` | 综合 / 最新 / 最多点赞 / 最多评论 / 最多收藏 | 排序方式 |
| `--note-type` | 不限 / 视频 / 图文 | 内容类型 |
| `--publish-time` | 不限 / 一天内 / 一周内 / 半年内 | 发布时间 |
| `--search-scope` | 不限 / 已看过 / 未看过 / 已关注 | 浏览范围 |

### 获取笔记详情

从搜索结果中拿到 `feed_id` 和 `xsec_token` 后：

```bash
# 基础详情（正文 + 图片 + 互动数据）
python3 scripts/cli.py get-feed-detail \
  --feed-id <ID> \
  --xsec-token <TOKEN>

# 加载全部评论（用于舆情分析）
python3 scripts/cli.py get-feed-detail \
  --feed-id <ID> \
  --xsec-token <TOKEN> \
  --load-all-comments

# 加载评论并展开子回复（深度分析）
python3 scripts/cli.py get-feed-detail \
  --feed-id <ID> \
  --xsec-token <TOKEN> \
  --load-all-comments \
  --click-more-replies \
  --max-replies-threshold 10
```

### 首页推荐流

```bash
# 获取当前首页推荐（个性化 Feed）
python3 scripts/cli.py list-feeds
```

输出包含每条笔记的标题、封面、作者、互动数据。

### 用户主页

```bash
# 查看博主资料和代表作
python3 scripts/cli.py user-profile \
  --user-id <USER_ID> \
  --xsec-token <TOKEN>
```

输出：基本信息、粉丝/关注数、笔记列表、互动率等。

---

## 与 AI Agent 配合使用

### 场景1：热点选题

```
你: "帮我看看小红书上AI工具方向最近什么火"
Agent → search-feeds("AI工具", sort=最多点赞, time=一周内)
     → 分析 Top 10 笔记的共同特征
     → 推荐选题方向 + 参考标题
```

### 场景2：竞品分析

```
你: "分析一下这个博主的爆款策略"
Agent → user-profile(博主ID)
     → get-feed-detail(Top3 笔记)
     → 总结：选题规律 / 发布节奏 / 文案风格 / 互动技巧
     → 输出可执行建议
```

### 场景3：评论区洞察

```
你: "这篇笔记的评论大家在讨论什么"
Agent → get-feed-detail(笔记ID, load-all-comments, expand-replies)
     → 提取高频关键词 / 情感倾向 / 用户痛点
     → 输出评论分析报告
```

---

## 输出格式说明

所有命令输出 **JSON 格式**：

```json
{
  "feeds": [
    {
      "id": "笔记ID",
      "xsec_token": "安全令牌",
      "note_card": {
        "display_title": "笔记标题",
        "user": { "nickname": "作者名" },
        "interact_info": { "liked_count": "点赞数" }
      }
    }
  ],
  "count": 10
}
```

> 💡 **`feed_id` + `xsec_token` 是配对的** —— 从搜索结果获取后传给 `get-feed-detail` 使用。

---

## 常见问题

### Q: 搜索结果为空？

A: 尝试：
- 更换关键词（更具体或更宽泛）
- 调整筛选条件（如去掉时间限制）
- 切换 `--search-scope` 为「不限」

### Q: 提示未登录？

A: 重新扫码登录：
```bash
python3 scripts/cdp_publish.py --host 127.0.0.1 --port 9222 get-login-qrcode
```

### Q: 详情获取失败？

A: 可能原因：
- `feed_id` 或 `xsec_token` 不匹配或过期 → 重新搜索获取最新的
- 笔记已删除或设为私密 → 换一篇试试
- 请求频率过高 → 等 5-10 秒再试

### Q: 如何控制请求频率？

A: 内置了随机延迟（Timing jitter），避免被风控。如需自定义：
- 连续多次操作之间手动间隔 3-5 秒
- 不要对同一页面频繁刷新

---

## 数据安全

| 原则 | 说明 |
|------|------|
| 本地操作 | 通过 CDP 操控你自己的浏览器，数据不经过第三方 |
| 登录态隔离 | 使用专用 Chrome Profile，不影响日常浏览 |
| 频率保护 | 内置速率限制，防止误触发平台风控 |
| 仅读操作 | 本技能只读取公开数据，不修改任何内容 |

---

## License

MIT © 2025 ql-wade

[GitHub](https://github.com/ql-wade/xhs-agent) · [Issues](https://github.com/ql-wade/xhs-agent/issues)
