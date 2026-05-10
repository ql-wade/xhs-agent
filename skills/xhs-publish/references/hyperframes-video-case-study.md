# HyperFrames 视频：案例场景（S5）设计模式

> 当用户说「加个案例」「后面跟一个热点」「需要真实感」时，在视频末尾追加 S5 案例场景。

## 为什么需要 S5

纯概念/技术介绍的视频容易让人觉得「空洞」「跟我没关系」。加一个**真实案例场景**后：
- **可信度** ↑ — 「真的有人用这个做出结果了」
- **代入感** ↑ — 用户想象「我也可以这样」
- **传播力** ↑ — 具体数据容易被截图转发

## S5 场景设计公式

```
┌─────────────────────────────────────┐
│  案例标签（小字）：🔥 REAL CASE     │
│  大标题（冲击力）：[谁] + [做了什么]  │
│  副标题（补充）：[时间] + [零基础]   │
│  数据卡片（3个横向排列）：            │
│    ├── [结果指标1] 最大字号金色      │
│    ├── [结果指标2]                  │
│    └── [门槛指标3] 「0基础/0成本」   │
│  Punchline（金句收尾）：             │
│    「不是未来·是现在」               │
│    或：「写代码就是生产力」           │
└─────────────────────────────────────┘
```

## 时间轴安排

| 场景 | 时长 | 内容 | 目的 |
|------|------|------|------|
| S1 钩子 | 0-5s | 震撼断言 + 视觉冲击 | 停住滑动的手指 |
| S2 是什么 | 5-10s | 解释概念 | 让人听懂 |
| S3 三大招 | 10-15s | 核心卖点 | 证明价值 |
| S4 CTA | 15-20s | 行动号召 | 引导关注 |
| **S5 案例** | **20-26s+** | **真实故事+数据** | **最终一击：信+传** |

S5 放最后是因为：
1. 前面建立了认知基础（知道是什么）
2. 中间证明了价值（知道有什么用）
3. 最后用案例**消除疑虑**（知道真的有效）

## HTML 结构模板

```html
<!-- ===== SCENE 5: CASE STUDY (20 → 26s) ===== -->
<div id="s5" class="clip scene" data-start="20" data-duration="6" data-track-index="0">
  <div class="scene-bg" style="background-image: url('assets/s5_case.jpg'); ..."></div>
  
  <div class="case-container">
    <div class="case-label">🔥 REAL CASE</div>
    <div class="case-headline">[谁] 用 [工具]</div>
    <div class="case-subheadline">[时间跨度] · [零基础描述]</div>
    
    <div class="case-stats">
      <div class="case-stat">
        <div class="case-stat-value">[数据1]</div>
        <div class="case-stat-label">[标签1]</div>
      </div>
      <div class="case-stat">
        <div class="case-stat-value">[数据2]</div>
        <div class="case-stat-label">[标签2]</div>
      </div>
      <div class="case-stat">
        <div class="case-stat-value">[数据3]</div>
        <div class="case-stat-label">[标签3]</div>
      </div>
    </div>
    
    <div class="case-punchline">[金句]</div>
  </div>
</div>
```

## CSS 关键样式

```css
.case-container {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 60px 40px;
  text-align: center;
}
.case-label {
  font-size: 14px; font-weight: 700;
  color: #00D4FF; letter-spacing: 4px;
  margin-bottom: 20px;
}
.case-headline {
  font-size: 42px; font-weight: 900;
  background: linear-gradient(135deg, #F5A623, #FFD700);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  line-height: 1.3; margin-bottom: 16px;
}
.case-subheadline {
  font-size: 18px; color: rgba(255,255,255,0.7);
  margin-bottom: 40px;
}
.case-stats { display: flex; gap: 30px; margin-bottom: 40px; }
.case-stat {
  background: rgba(255,255,255,0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 16px; padding: 24px 28px;
  min-width: 120px;
}
.case-stat-value {
  font-size: 32px; font-weight: 900;
  color: #F5A623; line-height: 1.2;
}
.case-stat-label {
  font-size: 13px; color: rgba(255,255,255,0.5);
  margin-top: 8px;
}
.case-punchline {
  font-size: 22px; font-weight: 700;
  color: rgba(255,255,255,0.9);
  letter-spacing: 2px;
}
```

## GSAP 入场动画

```javascript
// S4→S5 transition (fade out CTA)
tl.to(".cta-title", { y: -30, opacity: 0, duration: 0.4 }, 19.6);
tl.to(".cta-subtitle", { opacity: 0, duration: 0.3 }, 19.7);
tl.set("#s4", { opacity: 0 }, 20);

// S5 entrance
tl.fromTo("#s5", { opacity: 0 }, { opacity: 1, duration: 0.5 }, 20);
tl.from(".case-label", { y: 20, opacity: 0, duration: 0.5 }, 20.3);
tl.from(".case-headline", { y: 30, opacity: 0, duration: 0.6 }, 20.5);
tl.from(".case-subheadline", { y: 20, opacity: 0, duration: 0.5 }, 21.1);
tl.from(".case-stat", { 
  y: 40, opacity: 0, scale: 0.8, 
  stagger: 0.15, duration: 0.5, ease: "back.out(1.7)" 
}, 21.5);
tl.from(".case-punchline", { y: 20, opacity: 0, duration: 0.5 }, 22.8);
// Hold until end
```

## 已验证的案例库

以下案例已通过 Codex 出图 + 渲染验证：

| # | 案例 | 数据卡片 | Punchline |
|---|------|---------|-----------|
| 1 | 00后用Codex自动生成视频 | 200K粉丝 / 120+条视频 / 0剪辑经验 | 写代码就是生产力 |
| 2 | Sora开放首周批量出片 | 500+条 / 200W+播放 / 72小时 | 不是未来·是现在 |
| 3 | AI视频制作成本归零 | 5000→0元 / 1人=5人团队 / 3分钟出片 | 这一行变了 |

## Codex S5 背景图 Prompt

```
Use $image-gen. Premium vertical 9:16.
Cinematic dark background.
A glowing smartphone floating in center showing app interface.
Data dashboard with floating charts and numbers around it.
Gold and cyan accent lighting. Glassmorphism cards.
Particle dust. Apple product page style.
Cinematic dark mode. No text.
Use image_gen tool.
```
