---
name: xhs-explore
description: |
  小红书内容发现与分析技能。搜索笔记、浏览首页、查看详情、获取用户资料。
version: 1.0.0
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

| 参数 | 可选值 |
|------|--------|
| `--sort-by` | 综合 / 最新 / 最多点赞 / 最多评论 / 最多收藏 |
| `--note-type` | 不限 / 视频 / 图文 |
| `--publish-time` | 不限 / 一天内 / 一周内 / 半年内 |
| `--search-scope` | 不限 / 已看过 / 未看过 / 已关注 |

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
```

### 首页推荐流 & 用户主页

```bash
# 首页 Feed
python3 scripts/cli.py list-feeds

# 用户主页
python3 scripts/cli.py user-profile \
  --user-id <USER_ID> \
  --xsec-token <TOKEN>
```

---

## 与 AI Agent 配合使用

### 场景1：热点选题

```
你: "帮我看看小红书上AI工具方向最近什么火"
Agent → 搜索 + 分析 Top 10 → 推荐选题方向 + 参考标题
```

### 场景2：竞品分析

```
你: "分析一下这个博主的爆款策略"
Agent → 用户主页 + Top3 笔记详情 → 总结规律 → 输出建议
```

### 场景3：评论区洞察

```
你: "这篇笔记的评论大家在讨论什么"
Agent → 全部评论 + 子回复 → 提取关键词/情感/痛点 → 分析报告
```

---

## 输出格式

所有命令输出 **JSON 格式**：

```json
{
  "feeds": [{
    "id": "笔记ID",
    "xsec_token": "安全令牌",
    "note_card": {
      "display_title": "标题",
      "user": { "nickname": "作者名" },
      "interact_info": { "liked_count": "点赞数" }
    }
  }],
  "count": 10
}
```

> 💡 `feed_id` + `xsec_token` 配对使用 —— 从搜索结果获取后传给 `get-feed-detail`。

---

## 常见问题

### Q: 搜索结果为空？
A: 更换关键词或放宽筛选条件。

### Q: 提示未登录？
A: 重新扫码：`cdp_publish.py get-login-qrcode`

### Q: 详情获取失败？
A: feed_id/xsec_token 过期或不匹配 → 重新搜索获取最新的；或笔记已删除/私密。

### Q: 如何控制请求频率？
A: 内置随机延迟保护。连续操作间隔建议 3-5 秒。

---

## 数据安全

| 原则 | 说明 |
|------|------|
| 本地操作 | CDP 操控你自己的浏览器，数据不经过第三方 |
| 仅读操作 | 只读取公开数据，不修改任何内容 |
| 频率保护 | 内置速率限制，防止误触发风控 |

---

## License

MIT © 2025 ql-wade

基于 [xpzouying/xiaohongshu-skills](https://github.com/xpzouying/xiaohongshu-skills) 二次开发。
