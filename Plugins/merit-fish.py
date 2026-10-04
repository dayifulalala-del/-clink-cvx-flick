# ---
# name: 电子木鱼
# icon: hand.tap
# summary: 开启后按空格敲木鱼攒功德，空格条实时显示计数
# version: 1.1
# author: 奥寺美紀
# ---

# 电子木鱼 (Merit fish)
#
# v1.1：不再点按钮——在设置里开启后，打字时每按一次空格
# 就算敲一下木鱼（中文模式下选词落字也算），功德实时涨，
# 空格条上常驻显示。今日敲满 108 的整数倍（一串佛珠）有
# 圆满提示，偶尔还会「佛祖显灵」额外 +9。
#
# 计数防重复：一次落字可能同时触发空格键与候选落字两个
# 钩子，0.3 秒内的重复触发只算一次。
#
# 注意：空格条同一时间只能被一个插件占用——与空格条仪表盘、
# 空格条猜词不要同时开显示。

import random
import time

def day_index():
    # 按北京时间算「今天」，与仪表盘的自然日对齐。
    return int((time.time() + 28800) / 86400)

def initial():
    return {"on": True, "show": True, "total": 0, "today": 0,
            "day": 0, "last": 0.0}

def settings(state):
    roll(state)
    return vstack([
        toggle("敲木鱼（按空格计数）", state.get("on", True), action="on"),
        toggle("空格条显示功德", state.get("show", True), action="show"),
        text("开启后，每按一次空格算敲一下（中文模式下点候选、空格落字都算），今日 " + str(state.get("today", 0)) + " 下 · 累计功德 " + str(state.get("total", 0)) + "，只存在这台设备上。敲满 108 的整数倍有圆满提示，偶有佛祖显灵额外 +9。", size=12, color="gray"),
        text("空格条同一时间只能给一个插件：与空格条仪表盘、空格条猜词不要同时开。", size=12, color="gray"),
        button("功德清零", "reset", style="destructive"),
    ])

def on_action(action, value, state):
    if action == "on":
        state["on"] = value
        if value:
            if state.get("show", True):
                claim("spacebar.text")
                show(state)
        else:
            release("spacebar.text")
            space_text(None)
    elif action == "show":
        state["show"] = value
        if value and state.get("on", True):
            claim("spacebar.text")
            show(state)
        elif not value:
            release("spacebar.text")
            space_text(None)
    elif action == "reset":
        state["total"] = 0
        state["today"] = 0
        state["day"] = day_index()
        show(state)
        banner("功德清零，一切从头 🙏")
    return state

def on_open(state):
    roll(state)
    if state.get("on", True) and state.get("show", True):
        claim("spacebar.text")
        show(state)
    return state

def on_key(key, state):
    if key == " ":
        knock(state)
    return state

def on_suggestion(word, state):
    knock(state)
    return state

def roll(state):
    d = day_index()
    if state.get("day", 0) != d:
        state["day"] = d
        state["today"] = 0

def knock(state):
    if not state.get("on", True):
        return
    now = time.time()
    if now - state.get("last", 0.0) < 0.3:
        return
    state["last"] = now
    roll(state)
    bonus = 0
    if random.random() < 0.02:
        bonus = 9
    gain = 1 + bonus
    before = state.get("today", 0)
    state["today"] = before + gain
    state["total"] = state.get("total", 0) + gain
    if state["today"] // 108 > before // 108:
        banner("📿 佛珠圆满！今日已敲 " + str(state["today"]) + " 下，功德无量")
    elif bonus:
        banner("✨ 佛祖显灵！功德+10（今日 " + str(state["today"]) + "）")
    show(state)

def show(state):
    if not state.get("on", True) or not state.get("show", True):
        return
    space_text("🪵 今日 " + str(state.get("today", 0)) + " · 累计 " + str(state.get("total", 0)))
