# ---
# name: CVX Flick
# icon: scissors
# summary: Flick C up to copy, V up to paste, and X up to cut
# version: 1.1
# author: dayifulalala-del
# ---

def initial():
    return {
        "on": False,
        "swipe_before": False,
        "predictive_before": False
    }

def settings(state):
    return section("gestures.swipe", [
        toggle("C/V/X 上滑快捷操作", state["on"], action="toggle"),
        text("C ↑ 复制   ·   V ↑ 粘贴   ·   X ↑ 剪切", size=13, color="gray"),
        text("粘贴需要 Full Access；剪切仅在已选中文字时执行。", size=12, color="gray"),
    ], title="CVX Flick")

def on_action(action, value, state):
    if action != "toggle" or state["on"] == value:
        return state

    state["on"] = value

    if value:
        state["swipe_before"] = setting("gestures.swipe")
        state["predictive_before"] = setting("gestures.predictive_flick")

        set_setting("gestures.swipe", False)
        set_setting("gestures.predictive_flick", False)

        claim("gestures.swipe")
        claim("gestures.predictive_flick")
    else:
        release("gestures.swipe")
        release("gestures.predictive_flick")

        set_setting("gestures.swipe", state["swipe_before"])
        set_setting("gestures.predictive_flick", state["predictive_before"])

    return state

def on_swipe(key, direction, state):
    if not state["on"] or direction != "up":
        return state

    if key == "c":
        copy()
        haptic("light")

    elif key == "v":
        clip = context()["clipboard"]
        if clip:
            insert(clip)
            haptic("light")
        else:
            banner("剪贴板为空或没有剪贴板权限")
            haptic("light")

    elif key == "x":
        selected = context()["selected"]
        if selected:
            copy()
            backspace()
            haptic("light")
        else:
            banner("请先选择要剪切的文字")
            haptic("light")

    return state
