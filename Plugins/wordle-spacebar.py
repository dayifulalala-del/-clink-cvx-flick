# ---
# name: 空格条猜词
# icon: gamecontroller
# summary: 空格条上猜成语或猜英文单词，每天一题，最多 6 次
# version: 1.1
# author: 奥寺美紀
# ---

# 空格条猜词 (Spacebar Wordle)
#
# 把空格条当游戏屏，两种玩法（在插件设置里切换，默认猜成语）：
#
# 猜成语：每天一个四字成语，最多猜 6 次。在中文输入下正常打字
# 选词即可——落字的汉字会依次攒起来，每攒满 4 个字算一猜（整词
# 选中、逐字选都行），空格条立刻用 🟩🟨⬛ 回报。
# 猜单词：每天一个 5 字母英文词，规则同旧版；请在英文输入下玩
# （中文模式里提交英文走拼音引擎，落词钩子叫不到）。
#
# 两个玩法的每日题彼此独立，都猜完后点按钮开随机练习局。
# 玩法须知：打出的字会真的进输入框，请在备忘录等空白处玩；
# 游戏开着时，落字都会被攒作猜测，去别处聊天前点按钮收起。
# 空格条同一时间只能被一个插件占用，与仪表盘、电子木鱼的
# 空格显示不要同时开。

import random
import time

IDIOMS = [
    "一心一意", "三心二意", "三言两语", "四面八方", "四通八达",
    "五光十色", "五颜六色", "六神无主", "七上八下", "七嘴八舌",
    "八面玲珑", "九牛一毛", "九死一生", "十全十美", "十拿九稳",
    "百发百中", "百花齐放", "千军万马", "千言万语", "万众一心",
    "万水千山", "心花怒放", "心想事成", "心直口快", "心不在焉",
    "龙马精神", "龙飞凤舞", "虎头蛇尾", "狐假虎威", "守株待兔",
    "掩耳盗铃", "亡羊补牢", "画蛇添足", "画龙点睛", "对牛弹琴",
    "井底之蛙", "望梅止渴", "画饼充饥", "雪中送炭", "锦上添花",
    "落井下石", "一箭双雕", "三顾茅庐", "海阔天空", "天马行空",
    "风和日丽", "山清水秀", "鸟语花香", "春暖花开", "金碧辉煌",
    "富丽堂皇", "小心翼翼", "津津有味", "恋恋不舍", "依依不舍",
    "彬彬有礼", "头头是道", "念念不忘", "栩栩如生", "摇摇欲坠",
    "大名鼎鼎", "一丝不苟", "一鸣惊人", "一举两得", "一帆风顺",
    "一败涂地", "一落千丈", "一目了然", "一往无前", "二话不说",
    "三长两短", "三番五次", "四分五裂", "四海为家", "五湖四海",
    "五体投地", "六亲不认", "七拼八凑", "七零八落", "八仙过海",
    "九霄云外", "十万火急", "百折不挠", "百战百胜", "千变万化",
    "千辛万苦", "万无一失", "万事大吉", "人山人海", "人来人往",
    "车水马龙", "门庭若市", "川流不息", "络绎不绝", "张灯结彩",
    "欢天喜地", "兴高采烈", "眉开眼笑", "笑逐颜开", "喜出望外",
    "垂头丧气", "无精打采", "愁眉苦脸", "泪流满面", "装模作样",
    "自言自语", "胡说八道", "胡思乱想", "想入非非", "异想天开",
    "天方夜谭", "痴人说梦", "白日做梦", "如梦初醒", "马到成功",
]

ANSWERS = [
    "about", "above", "actor", "acute", "admit", "adopt", "adult", "after",
    "again", "agent", "agree", "ahead", "alarm", "album", "alert", "alike",
    "alive", "allow", "alone", "along", "alpha", "alter", "among", "anger",
    "angle", "angry", "ankle", "apart", "apple", "apply", "arena", "argue",
    "arise", "armor", "array", "arrow", "aside", "asset", "audio", "audit",
    "avoid", "awake", "award", "aware", "bacon", "badge", "bagel", "baker",
    "banjo", "barge", "basic", "basil", "basin", "basis", "batch", "bathe",
    "beach", "beard", "beast", "beech", "beefy", "befit", "began",
    "begin", "begun", "being", "belly", "below", "bench", "berry", "berth", "beset",
    "betel", "bevel", "bible", "bicep", "bigot", "bilge", "billy", "binge",
    "bingo", "biome", "birch", "birth", "bison", "biter", "black",
    "blade", "blame", "bland", "blank", "blare", "blast", "blaze", "bleak",
    "bleat", "bleed", "bleep", "blend", "bless", "blimp", "blind", "blink",
    "bliss", "blitz", "bloat", "block", "bloke", "blond", "blood", "bloom",
    "blown", "blues", "bluff", "blunt", "blurt", "blush", "board", "boast",
    "bonus", "boost", "booth", "booty", "booze", "borax", "borne", "bosom",
    "bossy", "botch", "bough", "boule", "bound", "bowel", "boxer", "brace",
    "bract", "braid", "brain", "brake", "brand", "brash", "brass",
    "brave", "bravo", "brawl", "brawn", "bread", "break", "breed", "briar",
    "bribe", "brick", "bride", "brief", "brine", "bring", "brink", "brisk",
    "broad", "broil", "broke", "brood", "brook", "broom", "broth", "brown",
]

# 猜测不查词表：成语任意 4 个汉字、单词任意 5 个字母都算数，
# 不会因为「不在表里」被卡住。

def day_index():
    return int((time.time() + 28800) / 86400)

def daily_answer(kind):
    if kind == "idiom":
        return IDIOMS[day_index() % len(IDIOMS)]
    return ANSWERS[day_index() % len(ANSWERS)]

def initial():
    return {"pref": "idiom", "active": "off", "practice": False,
            "answer": "", "guesses": [], "done": False, "buffer": "",
            "last": "", "last_commit": "", "last_commit_at": 0.0,
            "fin_idiom": 0, "fin_word": 0, "day": 0,
            "plays": 0, "wins": 0}

def settings(state):
    roll_day(state)
    d = day_index()
    si = "已完成" if state.get("fin_idiom") == d else "未完成"
    sw = "已完成" if state.get("fin_word") == d else "未完成"
    return vstack([
        toggle("猜成语（关掉则猜英文单词）", state.get("pref", "idiom") == "idiom", action="pref"),
        text("顶栏点「猜词」开始。猜成语：中文输入下打字选词，落字攒满 4 个算一猜；猜单词：英文输入下打 5 字母词按空格提交。空格条用 🟩🟨⬛ 回报，每题 6 次。", size=13),
        text("今日成语 " + si + " · 今日单词 " + sw + " · 战绩：共 " + str(state.get("plays", 0)) + " 局，赢 " + str(state.get("wins", 0)) + " 局。打出的字会真的进输入框，请在备忘录里玩，聊正事前点按钮收起。", size=12, color="gray"),
    ])

def bar_items(state):
    return [bar_button("toggle", "猜词", icon="gamecontroller")]

def on_action(action, value, state):
    if action == "toggle":
        if state.get("active") == "off":
            start(state)
        else:
            stop(state)
            banner("猜词已收起")
    elif action == "pref":
        state["pref"] = "idiom" if value else "word"
    return state

def on_open(state):
    roll_day(state)
    if state.get("active") != "off":
        claim("spacebar.text")
        show(state)
    return state

def on_word(word, state):
    if state.get("active") == "word":
        roll_day(state)
        if state.get("active") != "word" or state.get("done"):
            return state
        guess = letters_only(word)
        if len(guess) != 5 or guess == state.get("last"):
            return state
        state["last"] = guess
        judge(state, guess)
    elif state.get("active") == "idiom":
        commit(state, word)
    return state

def on_suggestion(word, state):
    if state.get("active") == "idiom":
        commit(state, word)
    return state

def commit(state, text):
    # 同一次落字可能经 on_word 与 on_suggestion 各报一遍，
    # 0.5 秒内同文只认一次。
    now = time.time()
    if text == state.get("last_commit") and now - state.get("last_commit_at", 0.0) < 0.5:
        return
    state["last_commit"] = text
    state["last_commit_at"] = now
    roll_day(state)
    if state.get("active") != "idiom" or state.get("done"):
        return
    buf = state.get("buffer", "") + cjk_only(text)
    while len(buf) >= 4:
        guess = buf[:4]
        buf = buf[4:]
        state["buffer"] = buf
        judge(state, guess)
        if state.get("done"):
            state["buffer"] = ""
            return
    state["buffer"] = buf

def judge(state, guess):
    guesses = state.get("guesses", [])
    guesses.append(guess)
    state["guesses"] = guesses
    answer = state["answer"]
    if guess == answer:
        state["done"] = True
        state["wins"] = state.get("wins", 0) + 1
        mark_done(state)
        banner("🎉 猜中了！ " + answer + " · " + str(len(guesses)) + "/6")
    elif len(guesses) >= 6:
        state["done"] = True
        mark_done(state)
        banner("就差一点 — 答案是 " + answer + "，明天再来")
    show(state)

def mark_done(state):
    if state.get("practice"):
        return
    if state.get("active") == "idiom":
        state["fin_idiom"] = day_index()
    elif state.get("active") == "word":
        state["fin_word"] = day_index()

def start(state):
    roll_day(state)
    kind = state.get("pref", "idiom")
    fin = state.get("fin_idiom") if kind == "idiom" else state.get("fin_word")
    state["active"] = kind
    state["practice"] = (fin == day_index())
    if state["practice"]:
        pool = IDIOMS if kind == "idiom" else ANSWERS
        state["answer"] = pool[int(random.random() * len(pool))]
    else:
        state["answer"] = daily_answer(kind)
    state["guesses"] = []
    state["done"] = False
    state["buffer"] = ""
    state["last"] = ""
    state["plays"] = state.get("plays", 0) + 1
    claim("spacebar.text")
    show(state)
    if state["practice"]:
        banner("练习局 · 随机题，猜到为止也可随时收起")
    elif kind == "idiom":
        banner("今日猜成语开始 · 四字，6 次机会")
    else:
        banner("今日猜单词开始 · 5 个字母，6 次机会")

def stop(state):
    state["active"] = "off"
    state["buffer"] = ""
    release("spacebar.text")
    space_text(None)

def roll_day(state):
    d = day_index()
    if state.get("day", 0) != d:
        state["day"] = d
        if state.get("active") != "off" and not state.get("practice"):
            stop(state)

def letters_only(word):
    out = ""
    for ch in word.lower():
        if "a" <= ch <= "z":
            out = out + ch
    return out

def cjk_only(text):
    out = ""
    for ch in text:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF:
            out = out + ch
    return out

def marks(guess, answer):
    n = len(answer)
    res = []
    used = []
    i = 0
    while i < n:
        res.append("⬛")
        used.append(False)
        i += 1
    i = 0
    while i < n:
        if guess[i] == answer[i]:
            res[i] = "🟩"
            used[i] = True
        i += 1
    i = 0
    while i < n:
        if res[i] == "🟩":
            i += 1
            continue
        j = 0
        while j < n:
            if not used[j] and answer[j] == guess[i]:
                used[j] = True
                res[i] = "🟨"
                break
            j += 1
        i += 1
    out = ""
    for m in res:
        out = out + m
    return out

def show(state):
    kind = state.get("active", "off")
    if kind == "off":
        return
    guesses = state.get("guesses", [])
    tag = "练习" if state.get("practice") else "今日"
    name = "成语" if kind == "idiom" else "单词"
    if state.get("done"):
        if guesses and guesses[-1] == state.get("answer", ""):
            space_text("✅ " + state["answer"] + " · " + str(len(guesses)) + "/6 · " + tag + name)
        else:
            space_text("❌ 答案 " + state.get("answer", "") + " · " + tag + name)
        return
    if not guesses:
        hint = "打四字词" if kind == "idiom" else "打 5 字母词"
        space_text("🟩 " + tag + name + " · " + hint + " · 0/6")
        return
    last = guesses[-1]
    disp = last.upper() if kind == "word" else last
    space_text(disp + " " + marks(last, state["answer"]) + " · " + str(len(guesses)) + "/6")
