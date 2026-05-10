# 小红书 GitHub 开源工具对比

> 2026-05-09 搜索 `gh search repos "xiaohongshu" --sort stars` 结果

## 推荐用于发布的工具

### 1. white0dew/XiaohongshuSkills ⭐2.7K ⭐ 首选备选
- **地址**：https://github.com/white0dew/XiaohongshuSkills
- **语言**：Python（CDP 协议）
- **核心能力**：图文/视频发布、登录管理、内容抓取、评论互动、数据看板
- **优势**：纯 CDP 无需扩展、支持 `--preview` 模式、`--host/--port` 连接远程 Chrome
- **适用场景**：Bridge 扩展不可用时的替代方案
- **部署**：`git clone → pip install -r requirements.txt → python scripts/publish_pipeline.py`
- **注意**：README 标注"目前仅测试 Windows"，但 macOS CDP 同样可用

### 2. xpzouying/xiaohongshu-mcp ⭐13.4K （最高星）
- **地址**：https://github.com/xpzouying/xiaohongshu-mcp
- **语言**：Go（MCP Server + Docker）
- **核心能力**：MCP 协议接口、登录、发布图文/视频、搜索、互动
- **优势**：最流行、Docker 一键部署、有浏览器插件版(x-mcp)零配置
- **部署**：`docker pull xpzouying/xiaohongshu-mcp && docker compose up -d`
- **注意**：需要 Docker 环境；国内拉镜像可能慢；插件版更适合非技术用户

### 3. jackwener/xiaohongshu-cli ⭐1.8K
- **地址**：https://github.com/jackwener/xiaohongshu-cli
- **语言**：未知（CLI 工具）
- **核心能力**：通过逆向 API 实现 CLI 搜索/阅读/互动
- **注意**：基于逆向 API，可能不稳定；主要用于数据获取而非发布

### 4. dreammis/social-auto-upload ⭐10.8K
- **地址**：https://github.com/dreammis/social-auto-upload
- **核心能力**：多平台自动上传（抖音/小红书/视频号/TikTok/YouTube/B站）
- **注意**：通用型工具，小红书只是支持的平台之一，针对性不如前两个

## 选择决策树

```
需要发布小红书？
├─ Bridge 扩展能连上？
│  └─ ✅ → 用本技能 cli.py fill-publish / click-publish
│
├─ 有 Docker 环境？
│  └─ ✅ → 用 xiaohongshu-mcp（Docker 部署最简单）
│
├─ 有 Python + Chrome CDP 端口？
│  └─ ✅ → 用 XiaohongshuSkills publish_pipeline.py
│
└─ 都没有？
   └─ 启动 Chrome + 加载扩展 → 重试 Bridge 或 XiaohongshuSkills
```

## 相关项目（信息参考）

| 项目 | Stars | 用途 |
|------|-------|------|
| JoeanAmier/XHS-Downloader | 11K | 作品链接提取/采集 |
| putyy/res-downloader | 17K | 多平台资源下载器 |
| HisMax/RedInk | 5.2K | AI 图文生成（Banana Dev SDK） |
| BetaStreetOmnis/xhs_ai_publisher | 1.9K | PyQt GUI 发布工具 |
| white0dew/XiaohongshuSkills | 2.7K | 自动发布/评论/检索 Skill |
