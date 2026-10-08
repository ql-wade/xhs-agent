# XHS-Agent

小红书 AI 提效技能包。基于 [xpzouying/xiaohongshu-skills](https://github.com/xpzouying/xiaohongshu-skills) 二次迭代开发。

## 核心技能

- `xhs-publish` — 内容发布（图文/视频/长文）
- `xhs-explore` — 内容发现（搜索/详情/用户）

## 快速开始

发布前阅读 `skills/xhs-publish/SKILL.md`，按用户指定执行环境选择浏览器；CLI 为 Extension Bridge 版。

```bash
pip install -e .
python3 scripts/cli.py check-login
python3 scripts/cli.py fill-publish --title-file ./title.txt --content-file ./content.txt --images ./img.png
```

填写后在当前页核验预览、去重和授权，再提交一次；命令成功不等于平台接受或公开可播放。

详细说明见各技能的 SKILL.md。
