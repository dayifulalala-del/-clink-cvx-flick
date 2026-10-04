# ---
# name: 数字大写
# icon: banknote
# summary: 输入数字时在候选栏给出中文读法与财务大写金额
# version: 1.1
# author: 奥寺美紀
# ---

# 数字大写 (Number words)
#
# 打一串数字（至少两位），候选栏给出三种写法，点一下插入：
#   财务大写  123456 -> 壹拾贰万叁仟肆佰伍拾陆元整
#   中文读法  123456 -> 十二万三千四百五十六
#   千分位    123456 -> 123,456（默认关，在设置里开）
# 小数最多读到分（财务）或四位（读法）。带前导零的编号类数字
# （如 007）不触发，免得跟证件号、验证码过不去。
#
# 1.1 起两条路供词：on_key 逐键记下刚敲的数字串，用 suggest()
# 主动把写法放到候选栏前排——中文输入下 suggestions 钩子拿不
# 到数字串时靠这条；suggestions 供词保留给滑行输入等场景。

DIGITS_PLAIN = "零一二三四五六七八九"
DIGITS_FIN = "零壹贰叁肆伍陆柒捌玖"
SMALL_PLAIN = ["", "十", "百", "千"]
SMALL_FIN = ["", "拾", "佰", "仟"]
BIG = ["", "万", "亿", "兆"]

def initial():
    return {"on": True, "money": True, "plain": True, "grouped": False,
            "buffer": "", "showing": False, "keytrack": False}

def settings(state):
    return vstack([
        section("text.corrections", [
            toggle("数字大写", state["on"], action="on"),
            toggle("财务大写（壹贰叁…）", state["money"], action="money"),
            toggle("中文读法（一二三…）", state["plain"], action="plain"),
            toggle("千分位（123,456）", state["grouped"], action="grouped"),
        ], title="数字大写"),
        text("输入至少两位数字时在候选栏给出写法，点一下插入。前导零的数字不触发。", size=12, color="gray"),
    ])

def on_action(action, value, state):
    if action in ("on", "money", "plain", "grouped"):
        state[action] = value
        if action == "on" and not value:
            stop_showing(state)
            state["buffer"] = ""
    return state

def on_open(state):
    reset_track(state)
    return state

def on_field(kind, state):
    reset_track(state)
    return state

def on_key(key, state):
    state["keytrack"] = True
    if not state.get("on", True):
        return state
    buf = state.get("buffer", "")
    for ch in key:
        if ch.isdigit() or ch == ".":
            buf = (buf + ch)[-20:]
        else:
            buf = ""
    state["buffer"] = buf
    offer(state, offers(buf, state))
    return state

def on_backspace(state):
    if not state.get("on", True):
        return state
    buf = state.get("buffer", "")
    if buf:
        buf = buf[:-1]
        state["buffer"] = buf
        offer(state, offers(buf, state))
    return state

def on_suggestion(word, state):
    state["buffer"] = ""
    state["showing"] = False
    return state

def suggestions(word, state):
    if not state.get("on", True):
        return []
    if state.get("keytrack"):
        return []
    return offers(word, state)

def reset_track(state):
    state["buffer"] = ""
    state["showing"] = False
    state["keytrack"] = False

def offer(state, vals):
    if vals:
        suggest(vals)
        state["showing"] = True
    elif state.get("showing"):
        stop_showing(state)

def stop_showing(state):
    if state.get("showing"):
        suggest([])
        state["showing"] = False

def offers(word, state):
    parts = parse_number(word)
    if parts is None:
        return []
    int_part, frac = parts
    out = []
    if state.get("money", True) and (not frac or len(frac) <= 2):
        out.append(money_text(int_part, frac))
    if state.get("plain", True):
        out.append(plain_text(int_part, frac))
    if state.get("grouped") and len(int_part) >= 4:
        out.append(grouped_text(int_part, frac))
    return out[:3]

def parse_number(word):
    # 返回 (整数部分, 小数部分)，不像个要转换的数字时返回 None。
    if not word or word.count(".") > 1:
        return None
    int_part, _, frac = word.partition(".")
    if not int_part.isdigit() or len(int_part) > 13:
        return None
    if len(int_part) > 1 and int_part[0] == "0":
        return None
    if not frac and len(int_part) < 2:
        return None
    if frac and (not frac.isdigit() or len(frac) > 4):
        return None
    return (int_part, frac)

def group_read(g, digits, small):
    # 0..9999 的四位一节读法，0 返回空串。
    if g == 0:
        return ""
    out = ""
    started = False
    zero = False
    for d, p in ((g // 1000, 3), ((g // 100) % 10, 2), ((g // 10) % 10, 1), (g % 10, 0)):
        if d == 0:
            if started:
                zero = True
        else:
            if zero:
                out += digits[0]
                zero = False
            out += digits[d] + small[p]
            started = True
    return out

def int_read(s, digits, small):
    if s == "0":
        return digits[0]
    groups = []
    t = s
    while t:
        groups.append(int(t[-4:]))
        t = t[:-4]
    out = ""
    pending_zero = False
    top = len(groups) - 1
    for i in range(top, -1, -1):
        g = groups[i]
        if g == 0:
            if out:
                pending_zero = True
            continue
        if pending_zero or (out and g < 1000 and i != top):
            out += digits[0]
        pending_zero = False
        out += group_read(g, digits, small) + BIG[i]
    return out

def plain_text(int_part, frac):
    out = int_read(int_part, DIGITS_PLAIN, SMALL_PLAIN)
    if out.startswith("一十"):
        out = out[1:]
    if frac:
        out += "点" + "".join(DIGITS_PLAIN[int(c)] for c in frac)
    return out

def money_text(int_part, frac):
    out = int_read(int_part, DIGITS_FIN, SMALL_FIN) + "元"
    if not frac or frac.strip("0") == "":
        return out + "整"
    jiao = frac[0]
    fen = frac[1] if len(frac) > 1 else "0"
    if jiao != "0":
        out += DIGITS_FIN[int(jiao)] + "角"
    elif fen != "0":
        out += "零"
    if fen != "0":
        out += DIGITS_FIN[int(fen)] + "分"
    else:
        out += "整"
    return out

def grouped_text(int_part, frac):
    chunks = []
    t = int_part
    while t:
        chunks.append(t[-3:])
        t = t[:-3]
    out = ",".join(reversed(chunks))
    if frac:
        out += "." + frac
    return out
