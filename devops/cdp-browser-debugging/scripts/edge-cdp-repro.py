# -*- coding: utf-8 -*-
"""CDP 直连真实浏览器：复现"点了没反应"并抓网络/JS 证据。

用法（用系统 Python，Hermes venv 无 pip）：
  C:\\Users\\HMSJ\\AppData\\Local\\Programs\\Python\\Python312\\python.exe edge-cdp-repro.py \
      --url https://login.tailscale.com/ --button "Sign in with Google" --port 9222

先决条件：目标浏览器已用 --remote-debugging-port=<port> --remote-allow-origins=* 启动（真实 profile）。
判定：点击后 location 未变 + 无新增请求 + 无 JS 异常 = 事件层被吞；有请求但 loadingFailed = 网络层失败。
"""
import argparse, json, sys, time, urllib.request, urllib.parse
from websocket import create_connection

def new_tab(base, url):
    req = urllib.request.Request(base + "/json/new?" + urllib.parse.quote(url, safe=""), method="PUT")
    return json.loads(urllib.request.urlopen(req, timeout=10).read())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="初始页面（第三方登录页）")
    ap.add_argument("--button", default="Google", help="按钮文字包含的片段")
    ap.add_argument("--port", default="9222")
    ap.add_argument("--click-x", type=int, help="可选：跳过找按钮，直接点此坐标")
    ap.add_argument("--click-y", type=int)
    args = ap.parse_args()
    base = f"http://127.0.0.1:{args.port}"

    tab = new_tab(base, args.url)
    ws = create_connection(tab["webSocketDebuggerUrl"], timeout=30)
    mid = 0
    def nid():
        global mid
        mid += 1
        return mid
    def send(method, params=None):
        ws.send(json.dumps({"id": nid(), "method": method, "params": params or {}}))
    def ev(expr):
        send("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
        while True:
            m = json.loads(ws.recv())
            if m.get("id") == mid:
                return m.get("result", {}).get("result", {}).get("value")
    def drain(timeout, buf):
        ws.settimeout(timeout)
        try:
            while True:
                buf.append(json.loads(ws.recv()))
        except Exception:
            pass

    send("Runtime.enable"); send("Network.enable"); send("Page.enable")
    time.sleep(6)
    evts = []
    drain(1.0, evts)
    print("PAGE:", ev("document.title"), "|", ev("location.href")[:100])

    if args.click_x is not None:
        x, y = args.click_x, args.click_y
    else:
        loc = ev(f"""(() => {{
          const b = [...document.querySelectorAll('button')].find(x => x.textContent.includes({json.dumps(args.button)}));
          if (!b) return null;
          const r = b.getBoundingClientRect();
          return JSON.stringify({{x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)}});
        }})()""")
        if not loc:
            print("!! 没找到按钮，页面可能不是目标页"); sys.exit(1)
        x, y = json.loads(loc)["x"], json.loads(loc)["y"]

    print(f"CLICK @ {x},{y}")
    send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y})
    send("Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y, "button": "left", "buttons": 1, "clickCount": 1})
    send("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y, "button": "left", "buttons": 0, "clickCount": 1})
    time.sleep(6)
    evts2 = []
    drain(2.0, evts2)
    all_ev = evts + evts2

    print("\n===== 点击后 =====")
    print("当前URL:", ev("location.href")[:110])
    reqs = [e for e in evts2 if e.get("method") == "Network.requestWillBeSent"]
    fails = [e for e in evts2 if e.get("method") == "Network.loadingFailed"]
    excs = [e for e in all_ev if e.get("method") == "Runtime.exceptionThrown"]
    print(f"新增请求: {len(reqs)}")
    for e in reqs[:15]:
        rq = e["params"]["request"]
        print("  REQ:", rq.get("method"), rq["url"][:110])
    print(f"失败请求: {len(fails)}")
    for e in fails[:10]:
        print("  FAIL:", e["params"].get("errorText"))
    print(f"JS异常: {len(excs)}")
    for e in excs[:5]:
        d = e["params"]["exceptionDetails"]
        print("  EXC:", d.get("text"), "|", (d.get("exception") or {}).get("description", "")[:150])
    ws.close()

if __name__ == "__main__":
    main()
