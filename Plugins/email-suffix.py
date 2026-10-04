# ---
# name: 邮箱后缀补全
# icon: envelope
# summary: 打出 name@ 后，候选栏给出常见邮箱后缀，点一下补全
# version: 1.1
# author: 奥寺美紀
# ---

# 邮箱后缀补全 (Email suffixes)
#
# 国产输入法的经典小功能：在任何输入框里打出 name@，候选栏就
# 给出 gmail.com、qq.com、163.com 等后缀，点一下整段补全；
# 继续打 gm 就只剩 gmail.com。
#
# 1.1 起同时用两条路给出候选：
# - suggestions 供词：把当前词里的拼音音节空格和隔音符去掉再
#   判断，兼容中文输入时拼音被显示成 da yi fu 的情况；
# - on_key 逐键跟踪：自己记下最近敲入的邮箱字符，一遇到 @ 就
#   用 suggest() 把补全放到候选栏前排，不依赖当前词的格式。
# @人名不会触发，因为 @ 后对不上任何域名的开头。

DOMAINS = ["gmail.com", "qq.com", "163.com", "126.com", "outlook.com",
           "hotmail.com", "icloud.com", "foxmail.com", "sina.com",
           "139.com", "yahoo.com", "proton.me"]
EMAIL_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._%+-@"
SEPARATORS = ["\n", "\t", "，", "。", "！", "？", "；", "：", "、",
              ",", "!", "?", ";", ":", "(", ")", "[", "]", "{", "}",
              "<", ">", '"', "/", "|"]

def initial():
    return {"on": True, "email_only": False, "field": "default",
            "buffer": "", "showing": False, "keytrack": False}

def settings(state):
    return vstack([
        section("text.corrections", [
            toggle("邮箱后缀补全", state["on"], action="on"),
            toggle("只在邮箱输入框里启用", state["email_only"], action="email_only"),
        ], title="邮箱后缀补全"),
        text("打出 name@ 后在候选栏给出常见后缀，中英文输入都可以；只认 @ 后能对上域名开头的输入，@人名不会触发。", size=12, color="gray"),
    ])

def on_action(action, value, state):
    if action in ("on", "email_only"):
        state[action] = value
        if action == "on" and not value:
            stop_showing(state)
            state["buffer"] = ""
    return state

def on_open(state):
    state["buffer"] = ""
    state["showing"] = False
    state["keytrack"] = False
    return state

def on_field(kind, state):
    state["field"] = kind
    state["buffer"] = ""
    state["showing"] = False
    state["keytrack"] = False
    return state

def on_key(key, state):
    state["keytrack"] = True
    if not active(state):
        return state
    buf = state.get("buffer", "")
    bad = False
    for ch in key:
        if ch in EMAIL_CHARS:
            buf = (buf + ch)[-80:]
        elif ch == "'" or ch == "’":
            pass
        else:
            bad = True
    if bad:
        buf = ""
    state["buffer"] = buf
    offer(state, completions(buf))
    return state

def on_backspace(state):
    if not active(state):
        return state
    buf = state.get("buffer", "")
    if buf:
        buf = buf[:-1]
        state["buffer"] = buf
        offer(state, completions(buf))
    return state

def on_suggestion(word, state):
    state["buffer"] = ""
    state["showing"] = False
    return state

def suggestions(word, state):
    if not active(state):
        return []
    if state.get("keytrack"):
        return []
    vals = completions(normalize_word(word))
    if vals:
        return vals
    return completions(context_token())

def active(state):
    if not state.get("on", True):
        return False
    if state.get("email_only") and state.get("field") != "email":
        return False
    return True

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

def normalize_word(word):
    if not word:
        return ""
    compact = word.replace(" ", "").replace("'", "").replace("’", "")
    for sep in SEPARATORS:
        if sep in compact:
            compact = compact.split(sep)[-1]
    return compact

def context_token():
    before = context()["before"]
    if not before:
        return ""
    token = before.split(" ")[-1]
    for sep in SEPARATORS:
        if sep in token:
            token = token.split(sep)[-1]
    return token

def completions(word):
    if not word or " " in word or word.count("@") != 1:
        return []
    local, _, tail = word.partition("@")
    if not local:
        return []
    tail = tail.lower()
    out = []
    for d in DOMAINS:
        if d != tail and d.startswith(tail):
            out.append(local + "@" + d)
    return out[:5]
