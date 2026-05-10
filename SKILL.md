---
name: xhs-agent
description: |
  小红书 AI 提效技能包。内容发布、热点发现、AI 辅助创作、Obsidian 集成。
  基于 xpzouying/xiaohongshu-skills 二次迭代开发。
version: 1.0.0
---

# XHS-Agent — 小红书 AI 提效技能包

**AI 负责效率，你负责灵魂。**

## 这是什么

XHS-Agent 是一套小红书内容创作与管理的 AI 技能包。帮助创作者用 AI Agent（Claude Code / Codex / Hermes）提升小红书运营效率。

### 起源

本项目基于 [xpzouying/xiaohongshu-skills](https://github.com/xpzouying/xiaohongshu-skills) 进行**二次迭代开发**，主要改进：

- 🎯 **定位重塑**：从「自动化工具」→「AI 提效 + 内容管理」
- ✍️ **文档重写**：从调试日记 → 用户使用指南
- 🔧 **实战验证**：端到端发布流程已通过实测，踩坑记录已内化为健壮的代码逻辑
- 🎨 **推广就绪**：营销级 README + Codex AI 生成配图

> 感谢上游项目 xpzouying/xiaohongshu-skills 提供的 CDP 引擎和基础架构。

## 包含哪些技能

| 技能 | 说明 | 入口 |
|------|------|------|
| 📝 **xhs-publish** | 图文/视频/长文发布，支持预览+审核模式 | [skills/xhs-publish/SKILL.md](./skills/xhs-publish/SKILL.md) |
| 🔍 **xhs-explore** | 热点搜索、笔记详情、竞品分析、用户画像 | [skills/xhs-explore/SKILL.md](./skills/xhs-explore/SKILL.md) |

## 快速上手

```bash
# 1. 克隆
git clone https://github.com/ql-wade/xhs-agent.git
cd xhs-agent

# 2. 安装依赖
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# 3. 启动 Chrome（开启远程调试）
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 --remote-allow-origins="*" &

# 4. 登录小红书（扫码）
python3 scripts/cdp_publish.py --host 127.0.0.1 --port 9222 get-login-qrcode

# 5. 发布笔记
python3 scripts/publish_pipeline.py \
  --host 127.0.0.1 --port 9222 \
  --title-file ./title.txt \
  --content-file ./content.txt \
  --images ./img1.png ./img2.png
```

详细使用说明请阅读各技能的 SKILL.md。

## 项目结构

```
xhs-agent/
├── README.md                    # 项目介绍（本文件）
├── SKILL.md                     # 总入口（本文件）
├── LICENSE                      # MIT
│
├── skills/
│   ├── xhs-publish/             # 发布技能
│   └── xhs-explore/             # 探索技能
│
├── scripts/                     # CDP 引擎
│   ├── publish_pipeline.py      # 发布流水线（主入口）
│   ├── cdp_publish.py           # CDP 协议层
│   ├── cli.py                   # CLI 子命令
│   └── xhs/                     # 业务模块
│
├── extension/                   # Chrome Bridge 扩展（可选）
└── assets/                      # 推广素材
```

## License

MIT © 2025 ql-wade

基于 [xpzouying/xiaohongshu-skills](https://github.com/xpzouying/xiaohongshu-skills) (MIT) 二次开发。
