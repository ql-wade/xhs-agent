# XHS-Agent

小红书 AI 提效技能包。基于 [xpzouying/xiaohongshu-skills](https://github.com/xpzouying/xiaohongshu-skills) 二次迭代开发。

## 核心技能

- `xhs-publish` — 内容发布（图文/视频/长文）
- `xhs-explore` — 内容发现（搜索/详情/用户）

## 快速开始

```bash
pip install -r requirements.txt
python3 scripts/cdp_publish.py --host 127.0.0.1 --port 9222 check-login
python3 scripts/publish_pipeline.py --host 127.0.0.1 --port 9222 \
  --title-file ./title.txt --content-file ./content.txt --images ./img.png
```

详细说明见各技能的 SKILL.md。
