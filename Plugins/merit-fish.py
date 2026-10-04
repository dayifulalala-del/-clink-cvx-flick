# ---
# name: 电子木鱼
# icon: hand.tap
# summary: 顶栏点一下功德+1，今日敲满 108 下还有圆满提示
# version: 1.0
# author: 奥寺美紀
# ---

# 电子木鱼 (Merit fish)
#
# 顶栏放一个木鱼按钮，点一下功德 +1，横幅冒一句佛系文案；
# 今日敲满 108 下（一串佛珠）有圆满提示，偶尔还会「佛祖显灵」
# 额外 +9。计数按天自动清零今日、累计不清零，都只存在本机。
# 开了空格条显示时，空格上常驻「🪵 今日 X · 累计 Y」。
#
# 注意：空格条同一时间只能被一个插件占用——与空格条仪表盘、
# 空格条猜词不要同时开显示。

import random
import time

LINES = [
    "功德+1",
    "心诚则灵",
    "施主，放下手机……算了继续敲",
    "烦恼-1",
    "佛祖说：这个可以有",
    "敲的不是木鱼，是寂寞",
    "今日宜敲木鱼",
    "心平气和，再来一下",
    "功德无量，头发浓密",
    "一敲解千愁",
]

def day_index():
    # 按北京时间算「今天」，与仪表盘的自然日对齐。
    return int((time.time() + 28800) / 86400)

def initial():
    return {"total": 0, "today": 0, "day": 0, "show": True}

def settings(state):
    roll(state)
    return vstack([
        text("在顶栏（Layout > Top bar）把「电子木鱼」按钮加上，点一下功德 +1。今日敲满 108 下有圆满提示，偶有佛祖显灵额外 +9。", size=13),
        text("今日 " + str(state.get("today", 0)) + " 下 · 累计功德 " + str(state.get("total", 0)) + "，只存在这台设备上。", size=12, color="gray"),
        toggle("空格条显示功德", state.get("show", True), action="show"),
        text("空格条同一时间只能给一个插件：与空格条仪表盘、空格条猜词不要同时开。", size=12, color="gray"),
        button("功德清零", "reset", style="destructive"),
    ])

def bar_items(state):
    return [bar_button("knock", "木鱼", icon="hand.tap")]

def on_action(action, value, state):
    if action == "knock":
        knock(state)
    elif action == "show":
        state["show"] = value
        if value:
            claim("spacebar.text")
            show(state)
        else:
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
    if state.get("show", True):
        claim("spacebar.text")
        show(state)
    return state

def roll(state):
    d = day_index()
    if state.get("day", 0) != d:
        state["day"] = d
        state["today"] = 0

def knock(state):
    roll(state)
    bonus = 0
    if random.random() < 0.02:
        bonus = 9
    gain = 1 + bonus
    state["today"] = state.get("today", 0) + gain
    state["total"] = state.get("total", 0) + gain
    today = state["today"]
    if today % 108 == 0:
        banner("📿 一串佛珠圆满！今日已敲 " + str(today) + " 下，功德无量")
    elif bonus:
        banner("✨ 佛祖显灵！功德+10（今日 " + str(today) + "）")
    else:
        line = LINES[state["total"] % len(LINES)]
        banner(line + " · 今日 " + str(today))
    show(state)

def show(state):
    if not state.get("show", True):
        return
    space_text("🪵 今日 " + str(state.get("today", 0)) + " · 累计 " + str(state.get("total", 0)))
