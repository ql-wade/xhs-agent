# 小红书视频剪辑工作流（ffmpeg）

> 从录屏素材到小红书视频笔记的完整剪辑流程。2026-05-09 实战验证。

## 场景

用户录制了手机/电脑屏幕操作视频（如小程序演示、AI交互过程），需要：
1. 剪掉冗余片段（终端滚动、加载等待、技术细节）
2. 保留精华画面（对话触发、页面弹出、结果展示）
3. 拼接成 15-30 秒短视频（小红书最佳时长）
4. 提取封面图用于发布

## 推荐工具链

| 工具 | 用途 | 安装 |
|------|------|------|
| `ffmpeg` | 裁剪、拼接、截封面 | `brew install ffmpeg` |
| `ffprobe` | 检查视频参数 | 随 ffmpeg 安装 |

## Step 1: 分析原视频

```bash
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4 | python3 -c "
import json,sys
d=json.load(sys.stdin)
f=d['format']
print(f'时长: {float(f[\"duration\"]):.1f}秒')
print(f'分辨率: {d[\"streams\"][0][\"width\"]}x{d[\"streams\"][0][\"height\"]}')
print(f'帧率: {d[\"streams\"][0].get(\"r_frame_rate\",\"?\")}')
print(f'大小: {int(f[\"size\"])/1024/1024:.1f}MB')
"
```

## Step 2: 定义精华片段

先用 `vision_analyze_video` 分析视频内容，标记每个时间段的画面和保留价值：

```
时间范围    画面内容                    保留原因
─────────────────────────────────────────────────
0-9s       微信对话：发指令+AI回复      ✅ 开头钩子，展示触发方式
10-16s     终端消息滚动                 ❌ 技术细节，观众不关心
17-21s     小程序首页弹出               ✅ 核心展示！
22-24s     飞书通知弹窗                 ✅ 证明飞书→微信联动
25-30s     MBTI答题                    ✅ 功能体验
31-38s     "AI正在读懂你..."加载动画   ⚠️ 可加速或剪掉
39-42s     ENTJ结果页                   ✅ 高潮收尾
```

## Step 3: 裁剪 + 拼接（concat demuxer 方式）⭐ 推荐

**为什么不用 filter_complex concat？**
- filter_complex 的 `[i:a]atempo,asetpts` 音频滤波器与 `concat` 视频滤波器的输出类型不匹配
- 会报错：`Media type mismatch between audio output and video input`
- **concat demuxer 更稳定**，直接拼接编码后的文件段

### Python 一键脚本

```python
import subprocess, os

input_video = "/path/to/recording.mp4"
output_dir = "/tmp/lark-send"  # 或 /tmp/xhs-publish
os.makedirs(output_dir, exist_ok=True)

# 精华片段定义：(开始秒, 结束秒)
segments = [
    (0, 9),    # 微信对话
    (17, 21),  # 小程序首页弹出
    (22, 24),  # 飞书通知
    (25, 30),  # MBTI答题
    (38, 43),  # 结果页
]

# 逐段裁剪
segment_files = []
for i, (start, end) in enumerate(segments):
    seg_file = f"{output_dir}/seg_{i:02d}.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start), "-to", str(end),
        "-i", input_video,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-avoid_negative_ts", "make_zero",
        seg_file
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    status = "✅" if r.returncode == 0 else "❌"
    print(f"{status} 片段{i}: {start}-{end}s")
    segment_files.append(seg_file)

# 写入 concat 列表
concat_list = f"{output_dir}/concat_list.txt"
with open(concat_list, "w") as f:
    for sf in segment_files:
        f.write(f"file '{sf}'\n")

# 拼接
output_video = f"{output_dir}/xhs_demo.mp4"
cmd = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0",
    "-i", concat_list,
    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
    "-c:a", "aac", "-b:a", "128k",
    "-movflags", "+faststart",
    output_video
]
subprocess.run(cmd, capture_output=True, text=True, timeout=120)

# 输出结果
size = os.path.getsize(output_video) / 1024 / 1024
print(f"\n🎬 完成! {output_video} ({size:.1f}MB)")
```

## Step 4: 截取封面图

```bash
# 从视频第 N 秒截取一帧作为封面（选画面最精彩的那一帧）
ffmpeg -y -i output.mp4 -ss 4 -vframes 1 cover.jpg
```

**注意**：`-vframes 1` + 非 pattern 文件名时 ffmpeg 会警告但仍然成功输出单帧。

## Step 5: 发布到飞书预览（或小红书）

### 飞书发送视频（需要封面）
```bash
cd /tmp/lark-send && lark-cli im +messages-send \
  --chat-id oc_xxx \
  --video ./xhs_demo.mp4 \
  --video-cover ./cover.jpg
# ⚠️ 没有 --video-cover 会报 validation 错误！
```

### 小红书发布视频
```bash
python scripts/cli.py fill-publish-video \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  --video "/abs/path/xhs_demo.mp4"
# 然后用户确认 → click-publish
```

## 参数调优参考

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `-crf` | 18-23 | 越小质量越高，20 是短视频最佳平衡点 |
| `-preset` | `fast` | 编码速度 vs 压缩率平衡 |
| 目标时长 | 15-30秒 | 小红书完播率最优区间 |
| 目标大小 | < 5MB | 上传速度快，移动网络友好 |
| 分辨率 | 保持原分辨率 | 手机录屏通常 540×1200 或 1080×1920，无需改 |

## 常见问题

### Q: filter_complex concat 为什么报错？
A: 音频滤波器 (`asetpts`, `atempo`) 输出的是音频流，但 `concat` 滤波器期望的输入类型是视频。用 **concat demuxer**（文件级拼接）完全绕过这个问题。

### Q: 拼接后音画不同步？
A: 确保每个分段都用相同的编码参数（同样的 `-c:v` 和 `-c:a`），且 `-avoid_negative_ts make_zero` 统一时间基准。

### Q: 封面截图是黑屏？
A: 可能截到了关键帧之间的位置。换一个 `-ss` 时间点（如 `-ss 2` 或 `-ss 6`），选画面最清晰的帧。
