# ---
# name: 空格条仪表盘
# icon: chart.bar
# summary: 空格上轮播打字速度、本次词数与连续打字天数
# version: 1.0
# author: 奥寺美紀
# ---

# 空格条仪表盘 (Spacebar stats)
#
# 官方的 WPM Spacebar 只报速度。这个把空格当成一块小仪表盘，
# 每 3 秒轮换一项：实时速度、本次打开键盘以来打的词数、
# 累计总词数、连续打字天数。显示哪几项在设置里勾。
#
# 注意：它和官方 WPM Spacebar 抢同一块空格，别同时开两个。

def initial():
    return {"on": False, "session": 0, "slot": 0, "ticks": 0,
            "show_wpm": True, "show_session": True,
            "show_total": False, "show_streak": True}

def settings(state):
    return vstack([
        section("keys.spacebar", [
            toggle("空格条仪表盘", state["on"], action="on"),
            toggle("打字速度", state["show_wpm"], action="show_wpm"),
            toggle("本次词数", state["show_session"], action="show_session"),
            toggle("累计词数", state["show_total"], action="show_total"),
            toggle("连续天数", state["show_streak"], action="show_streak"),
        ], title="空格条仪表盘"),
        text("空格上每 3 秒轮换一项统计。与官方 WPM Spacebar 不要同时开。", size=12, color="gray"),
    ])

def on_action(action, value, state):
    if action == "on":
        state["on"] = value
        if value:
            claim("spacebar.text")
            show(state)
        else:
            release("spacebar.text")
            space_text(None)
    elif action in ("show_wpm", "show_session", "show_total", "show_streak"):
        state[action] = value
        show(state)
    return state

def on_open(state):
    state["session"] = 0
    state["ticks"] = 0
    show(state)
    return state

def on_word(word, state):
    state["session"] = state.get("session", 0) + 1
    show(state)
    return state

def on_tick(state):
    if state.get("on"):
        state["ticks"] = state.get("ticks", 0) + 1
        if state["ticks"] >= 3:
            state["ticks"] = 0
            state["slot"] = state.get("slot", 0) + 1
    show(state)
    return state

def items(state):
    s = stats()
    out = []
    if state.get("show_wpm", True):
        out.append(str(s["wpm"]) + " wpm")
    if state.get("show_session", True):
        out.append("本次 " + str(state.get("session", 0)) + " 词")
    if state.get("show_total"):
        out.append("累计 " + str(s["words"]) + " 词")
    if state.get("show_streak", True):
        out.append("连打 " + str(s["streak"]) + " 天")
    return out

def show(state):
    if not state.get("on"):
        return
    out = items(state)
    if not out:
        space_text(None)
        return
    slot = state.get("slot", 0) % len(out)
    space_text(out[slot])
