# ---
# name: 盘古之白
# icon: textformat.abc
# summary: 中英文混输时，自动在汉字与字母、数字之间补一个空格
# version: 1.2
# author: 奥寺美紀
# ---

# 盘古之白 (Pangu spacing)
#
# 中文排版讲究汉字与西文之间留一点空白：写出来是「在 Clink 里打字」，
# 而不是「在Clink里打字」。国产输入法大多有这个习惯，Clink 没有，
# 这个插件把它补上。
#
# 做法（v1.1 改）：不猜刚落的词是什么，直接看光标前的文字结尾——
# 最后一个「段」（连续同类字符：汉字段、字母段或数字段）与它前面
# 那个字之间若是汉字↔字母/数字的交界，就用 replace 在交界处补空格。
# 补完后交界处就是空格，重复检查也不会补第二次。
#
# v1.2：英文模式下 v1.1 已可用，但中文输入法里提交英文走的是拼音
# 引擎的路，空格落字和词落字两个触发点都可能叫不到。于是再加两个
# 触发点：on_suggestion（点候选条落字时）和 on_tick（每秒巡查一次
# 兜底，只在当前没有正在拼的词时动手，免得打扰拼音组合）。
# 标点旁、已经有空格、邮箱和网址内部都不动手。
#
# 注意：读光标前文字需要插件的「打字数据」访问权（Access 页开启），
# 没开时 context() 的文档内容是空的，插件不会有任何动作。

NO_SPACE_AFTER = "，。！？；：、,.!?;:)]}%…"
OPENERS = "（【「『《(“‘"

def initial():
    return {"on": True, "digits": True, "field": "default"}

def settings(state):
    return vstack([
        section("text.corrections", [
            toggle("中英之间自动加空格", state["on"], action="on"),
            toggle("汉字与数字之间也加", state["digits"], action="digits"),
        ], title="盘古之白"),
        text("打完中文接着打英文、或打完英文接着打中文时，自动在交界处补一个空格。标点旁、邮箱和网址里不补。需要在本插件的 Access 页开启打字数据访问。", size=12, color="gray"),
    ])

def on_action(action, value, state):
    if action in ("on", "digits"):
        state[action] = value
    return state

def on_field(kind, state):
    state["field"] = kind
    return state

def on_key(key, state):
    if key == " ":
        apply_fix(state)
    return state

def on_word(word, state):
    apply_fix(state)
    return state

def on_suggestion(word, state):
    apply_fix(state)
    return state

def on_tick(state):
    apply_fix(state, settled=True)
    return state

def apply_fix(state, settled=False):
    if not state.get("on", True):
        return
    if state.get("field") == "password":
        return
    ctx = context()
    if settled and ctx.get("word"):
        return
    fix = junction_fix(ctx["before"], state.get("digits", True))
    if fix is not None:
        replace(fix[0], fix[1])

def char_class(ch):
    o = ord(ch)
    if 0x3400 <= o <= 0x9FFF or 0x3040 <= o <= 0x30FF or 0xAC00 <= o <= 0xD7AF:
        return "cjk"
    if ("a" <= ch <= "z") or ("A" <= ch <= "Z"):
        return "latin"
    if "0" <= ch <= "9":
        return "digit"
    return "other"

def junction_fix(before, digits_on):
    # 看光标前文字的最后一个交界。需要补空格时返回
    # (要替换掉的字符数, 替换文本)，否则返回 None。
    if not before:
        return None
    tail = ""
    b = before
    if b.endswith(" "):
        tail = " "
        b = b[:-1]
    if not b:
        return None
    lc = char_class(b[-1])
    if lc == "other":
        return None
    i = len(b)
    while i > 0 and char_class(b[i - 1]) == lc:
        i -= 1
    if i == 0:
        return None
    suffix = b[i:]
    prev = b[i - 1]
    if prev == " " or prev in NO_SPACE_AFTER or prev in OPENERS:
        return None
    pc = char_class(prev)
    need = False
    if pc == "cjk" and (lc == "latin" or (digits_on and lc == "digit")):
        need = True
    if lc == "cjk" and (pc == "latin" or (digits_on and pc == "digit")):
        need = True
    if not need:
        return None
    start = b.rfind(" ", 0, i) + 1
    token = b[start:]
    if "@" in token or "://" in token:
        return None
    return (len(suffix) + len(tail), " " + suffix + tail)
