# 小红书批量配图 Prompt 模板（已验证 2026-05-09）

> 统一风格：暗夜紫 `#1a1a2e` + 香槟金 `#FFD700` + 星尘粒子 + 3:4 竖版
> 调用方式：`codex --dangerously-bypass-approvals-and-sandbox exec "PROMPT" < /dev/null 2>&1` （**必须 pty=True**）

## 通用模板前缀（每张图都带）

```
Create a Xiaohongshu content image (3:4 vertical, dark purple #1a1a2e + gold #FFD700 style, starry particles).
```

## 图1：封面（9/10 ✅）

核心要素：中心手机展示产品 + 技术图标环绕 + 中文大字标题
- 中央：iPhone展示小程序界面（塔罗/占卜）
- 环绕：Hermes AI机器人、代码窗口、飞书气泡、Docker图标
- 文字：主标题(超大金字) + 副标题 + 价值承诺tag

## 图2：触发场景（飞书对话）

场景：聊天界面截图
- 手机屏幕显示对话气泡
- 用户消息 + AI回复（引用真实对话原话）
- 咖啡杯元素暗示「远程/不在电脑前」

## 图3-N：各功能页面

通用结构：
- iPhone显示具体页面UI
- 页面标题 + 核心交互元素（卡片/按钮/进度条）
- 文字overlay：页面名称 + 一句话描述 + AI相关tag

## 图N：技术架构图

结构：左到右流程图 + 金色箭头连接
- 节点：Hermes Agent → Codex → Docker → 手机
- 底部：人类角色（产品经理+QA）+ 咖啡杯

## 最后一张：真机截图（用户要求增加，不替换）

> 用户明确：「不是替换，是增加」—— 真机截图追加到图片列表末尾作为最后一张。

## 出图时间参考

| 图片类型 | 平均耗时 | tokens |
|---------|---------|--------|
| 封面/场景类 | 3-5 min | ~20K |
| UI界面类 | 4-6 min | ~20K |
| 架构图 | 4-5 min | ~20K |
| API抖动重连 | 额外+2min | — |

## API 连接问题处理

Codex 偶发 TLS handshake eof：
- 症状：`ERROR: Reconnecting... N/5` 循环
- 处理：kill 进程 → 重新启动同一命令（通常第二次就恢复）
- 不要连续重试超过2次，等30秒再试
