# 小红书 GitHub 替代工具调研（2026-05-09）

## 调研背景

原 xiaohongshu-skills 的 Bridge 扩展方案在 openclaw 环境下不可用（Chrome 禁扩展），用户要求「去 GitHub 找小红书技能」。

## 候选项目对比

| 项目 | Stars | 方案 | 部署方式 | 评估结果 |
|------|-------|------|----------|----------|
| **[xpzouying/xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)** | ⭐13.4K | MCP 协议 | Docker | ❌ Docker 拉取镜像失败（网络问题） |
| **[dreammis/social-auto-upload](https://github.com/dreammis/social-auto-upload)** | ⭐10.8K | 多平台上传 | Playwright + 浏览器 | ⚠️ 功能太重，需要完整浏览器环境 |
| **[white0dew/XiaohongshuSkills](https://github.com/white0dew/XiaohongshuSkills)** | ⭐2.7K | **纯 CDP** | Python venv | ✅ **选用！轻量、直接、已验证成功** |
| [BetaStreetOmnis/xhs_ai_publisher](https://github.com/BetaStreetOmnis/xhs_ai_publisher) | ⭐1.9K | AI 辅助发布 | Python | 未深入评估 |
| [jackwener/xiaohongshu-cli](https://github.com/jackwener/xiaohongshu-cli) | ⭐1.8K | CLI 工具 | Node.js | 未深入评估 |

## 最终选择：white0dew/XiaohongshuSkills

### 选择理由

1. **纯 CDP，零依赖**：不需要任何浏览器扩展、不需要 Docker
2. **`--host --port` 参数**：可以连接任意已有 Chrome 实例（包括用户手动启动的）
3. **`--preview` 模式**：先填充内容让用户确认，再决定是否发布
4. **代码质量高**：结构清晰，错误处理完善
5. **社区活跃**：最近有更新，Issue 响应及时

### 部署步骤

```bash
cd /tmp && git clone --depth 1 https://github.com/white0dew/XiaohongshuSkills.git
cd XiaohongshuSkills
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -q
# 额外安装 websocket-client（CDP 连接需要）
.venv/bin/pip install websocket-client -q
```

### 核心脚本

| 脚本 | 功能 |
|------|------|
| `scripts/publish_pipeline.py` | 一键发布流水线（登录检测→填表→发布） |
| `scripts/cdp_publish.py` | CDP 底层操作（登录检查、二维码获取） |
| `scripts/chrome_launcher.py` | Chrome 进程管理 |

### 实测结果（2026-05-09）

- ✅ 8/8 图片上传成功
- ✅ 标题填充成功（20字）
- ✅ 正文填充成功（1526字）
- ✅ 16 个话题标签全部选中
- ✅ `--preview` 模式正常工作（只填不发布）
- ✅ CDP 截图验证通过（3张预览截图发飞书）

### 注意事项

1. **必须先有已登录的 Chrome**：CDP 只是操控手段，登录态来自 Chrome 的 cookie
2. **二维码登录流程**：`get-login-qrcode` → 发飞书 → 用户扫 → `check-login` 确认
3. **图片路径用绝对路径**：相对路径可能解析失败
4. **标签在正文最后一行**：脚本自动识别 `#标签1 #标签2` 格式并选中对应话题
5. **超时设置**：大图上传可能较慢，建议 timeout 设为 180s+
