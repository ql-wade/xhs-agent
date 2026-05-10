# CDP 直连 Chrome 登录小红书 Creator 平台

> 2026-05-09 实测成功。当 Bridge 扩展无法连接时，通过启动专用 Chrome 实例 + CDP WebSocket 直连完成登录和发布。

## 前置条件

- 用户授权 Hermes 系统操作权限（`--load-extension` 需要启动新 Chrome 进程）
- XHS Bridge 扩展路径：`/Users/li.qing/.hermes/skills/xiaohongshu-skills/extension/`
- Python websocket-client 已安装到 xhs venv

## 启动命令

```bash
# 一键启动（复制粘贴）
pkill -f "chrome-xhs-profile" 2>/dev/null; kill $(pgrep -f bridge_server) 2>/dev/null; sleep 2

"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --remote-allow-origins="*" \
  --user-data-dir="/Users/li.qing/.hermes/chrome-xhs-profile" \
  --load-extension="/Users/li.qing/.hermes/skills/xiaohongshu-skills/extension" \
  --no-first-run --no-default-browser-check \
  "https://creator.xiaohongshu.com/publish/publish" &>/dev/null &

sleep 4 && lsof -i :9222 | grep Google || echo "❌ Chrome failed"
```

## CDP 登录脚本（完整版）

```python
#!/usr/bin/env python3
"""CDP 直连 Chrome 完成 Creator 平台登录 + 表单填写"""
import json, time, sys, websocket, urllib.request

CDP_URL = "http://127.0.0.1:9222/json"

def connect():
    tabs = json.loads(urllib.request.urlopen(CDP_URL).read())
    if not tabs:
        print("❌ No Chrome tabs found"); sys.exit(1)
    ws = websocket.create_connection(tabs[0]["webSocketDebuggerUrl"], timeout=30)
    print(f"✅ Connected to: {tabs[0]['url'][:80]}")
    return ws, tabs[0]

_id = [0]
def cdp(ws, method, params=None):
    _id[0] += 1
    msg = {"id": _id[0], "method": method}
    if params: msg["params"] = params
    ws.send(json.dumps(msg))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == _id[0]: return resp

def js(ws, expr):
    r = cdp(ws, "Runtime.evaluate", {"expression": expr})
    res = r.get("result", {}).get("result", {})
    if "exceptionDetails" in r.get("result", {}):
        print(f"⚠️ JS Error: {r['result']['exceptionDetails'].get('text', '?')}")
        return None
    return res.get("value")

# ─── 使用示例 ───
if __name__ == "__main__":
    ws, tab = connect()

    # 1. 查找所有 input
    inputs = js(ws, "JSON.stringify(Array.from(document.querySelectorAll('input')).map((el,i)=>({i,type:el.type,ph:el.placeholder})))")
    print(f"Inputs: {inputs}")

    # 2. 填写手机号（React 受控组件）
    result = js(ws, """
    (() => {
      for (const inp of document.querySelectorAll('input')) {
        if (inp.placeholder === '手机号') {
          const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
          setter.call(inp, '15223312249');
          inp.dispatchEvent(new Event('input', {bubbles: true}));
          inp.dispatchEvent(new Event('change', {bubbles: true}));
          return 'Phone filled ✅';
        }
      }
      return 'Not found ❌';
    })()
    """)
    print(f"Fill phone: {result}")

    # 3. 点击发送验证码
    result = js(ws, """
    (() => {
      for (const el of document.querySelectorAll('*')) {
        if (el.textContent?.trim() === '发送验证码' && el.children.length === 0) {
          el.click(); return 'Clicked ✅';
        }
      }
      // 备用：模糊匹配
      for (const el of document.querySelectorAll('span,a,button,div')) {
        if (el.textContent?.includes('发送验证码') && el.offsetParent !== null) {
          el.click(); return `Clicked ${el.tagName} ✅`;
        }
      }
      return 'Not found ❌';
    })()
    """)
    print(f"Send code: {result}")

    # 4. 填写验证码（等用户提供后执行）
    # js(ws, """ ... 填入验证码到 input[2] ... """)

    # 5. 点击登录按钮
    # js(ws, """ ... 点击 .submit 或 [type=submit] ... """)

    ws.close()
```

## 关键坑点

| 问题 | 症状 | 解决 |
|------|------|------|
| 缺少 `--remote-allow-origins=*` | `websocket.BadStatusException: Handshake status 403 Forbidden` | 加上该参数重启 Chrome |
| React 受控组件不响应 `.value=` | 手机号填了但提交时为空 | 用 `nativeInputValueSetter` + dispatchEvent |
| 页面黑屏 / snapshot 空 | Browser 工具的 openclaw Chrome 不稳定 | 用 CDP 直连的专用 Chrome 更稳定 |
| 验证码倒计时 | 点发送后按钮变灰+显示秒数 | 正常现象，等用户收到短信 |

## Creator 平台登录表单 DOM 结构（2026-05-09）

```
input[0]: text, placeholder="请选择选项"   → 区号选择器（默认值 "+86"）
input[1]: text, placeholder="手机号"         → 手机号输入框
input[2]: text, placeholder="验证码"         → 验证码输入框
input[3]: text, placeholder="邮箱"           → 邮箱（备用登录方式）
input[4]: password, placeholder="密码"       → 密码（备用登录方式）
```

**「发送验证码」按钮**: 不是 `<button>`，是 `<span>` 或 `<a>`，文本精确匹配 `"发送验证码"`，`children.length === 0`。
