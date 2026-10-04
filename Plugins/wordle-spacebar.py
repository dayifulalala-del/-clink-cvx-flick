# ---
# name: 空格条猜词
# icon: gamecontroller
# summary: 在空格条上玩 Wordle：每天一词，猜中为止最多 6 次
# version: 1.0
# author: 奥寺美紀
# ---

# 空格条猜词 (Spacebar Wordle)
#
# 把空格条当游戏屏：顶栏点「猜词」开始，每天一个 5 字母英文词，
# 最多猜 6 次。在任意输入框里像平时一样打词（空格落字即提交），
# 空格条立刻用 🟩🟨⬛ 回报这一猜。今日词猜完后，再点按钮是
# 随机练习局，不限次数。
#
# 玩法须知：你打的词会真的进输入框，所以请在备忘录之类的空白
# 地方玩；游戏开着时，所有 5 字母词都会被当作一次猜测，去别处
# 聊天前记得点按钮收起。空格条同一时间只能被一个插件占用，
# 与空格条仪表盘、电子木鱼的空格显示不要同时开。

import random
import time

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
    "bract", "braid", "brain", "brake", "brand", "brane", "brash", "brass",
    "brave", "bravo", "brawl", "brawn", "bread", "break", "breed", "briar",
    "bribe", "brick", "bride", "brief", "brine", "bring", "brink", "brisk",
    "broad", "broil", "broke", "brood", "brook", "broom", "broth", "brown",
]

# 说明：词表特意只放最常见的词当答案；猜测不查词表，
# 任意 5 个字母都算数，不会因为「词不存在」被卡住。

def day_index():
    return int((time.time() + 28800) / 86400)

def daily_answer():
    return ANSWERS[day_index() % len(ANSWERS)]

def initial():
    return {"mode": "off", "day": 0, "answer": "", "guesses": [],
            "done": False, "last": "", "plays": 0, "wins": 0}

def settings(state):
    roll_day(state)
    status = "今日还没开始"
    if state.get("done"):
        status = "今日已完成（" + str(len(state.get("guesses", []))) + "/6）"
    elif state.get("mode") == "daily":
        status = "今日进行中（已猜 " + str(len(state.get("guesses", []))) + "/6）"
    return vstack([
        text("顶栏点「猜词」开始：每天一个 5 字母词，最多 6 次。在备忘录等空白处打词、按空格提交，空格条用 🟩🟨⬛ 回报。今日猜完后点按钮可开随机练习局。", size=13),
        text(status + " · 战绩：共 " + str(state.get("plays", 0)) + " 局，赢 " + str(state.get("wins", 0)) + " 局。打出的词会真的进输入框，别在聊天里开着玩。", size=12, color="gray"),
    ])

def bar_items(state):
    return [bar_button("toggle", "猜词", icon="gamecontroller")]

def on_action(action, value, state):
    if action == "toggle":
        if state.get("mode") == "off":
            start(state)
        else:
            stop(state)
            banner("猜词已收起")
    return state

def on_open(state):
    roll_day(state)
    if state.get("mode") != "off":
        claim("spacebar.text")
        show(state)
    return state

def on_word(word, state):
    if state.get("mode") == "off" or state.get("done"):
        return state
    roll_day(state)
    if state.get("mode") == "off" or state.get("done"):
        return state
    guess = letters_only(word)
    if len(guess) != 5:
        return state
    if guess == state.get("last"):
        return state
    state["last"] = guess
    guesses = state.get("guesses", [])
    guesses.append(guess)
    state["guesses"] = guesses
    answer = state["answer"]
    if guess == answer:
        state["done"] = True
        state["wins"] = state.get("wins", 0) + 1
        banner("🎉 猜中了！ " + answer.upper() + " · " + str(len(guesses)) + "/6")
    elif len(guesses) >= 6:
        state["done"] = True
        banner("就差一点 — 答案是 " + answer.upper() + "，明天再来")
    show(state)
    return state

def start(state):
    roll_day(state)
    if state.get("mode") == "daily" and not state.get("done"):
        return
    if not state.get("done"):
        state["mode"] = "daily"
        state["answer"] = daily_answer()
    else:
        state["mode"] = "practice"
        state["answer"] = ANSWERS[int(random.random() * len(ANSWERS))]
    state["done"] = False
    state["guesses"] = []
    state["last"] = ""
    state["plays"] = state.get("plays", 0) + 1
    claim("spacebar.text")
    show(state)
    if state["mode"] == "daily":
        banner("今日猜词开始 · 5 个字母，6 次机会")
    else:
        banner("练习局 · 随机词，猜到为止也可随时收起")

def stop(state):
    state["mode"] = "off"
    release("spacebar.text")
    space_text(None)

def roll_day(state):
    d = day_index()
    if state.get("day", 0) != d:
        state["day"] = d
        mode = state.get("mode", "off")
        if mode == "daily":
            state["mode"] = "off"
            release("spacebar.text")
            space_text(None)
            state["guesses"] = []
            state["done"] = False
            state["last"] = ""
        elif mode == "off":
            state["guesses"] = []
            state["done"] = False
            state["last"] = ""

def letters_only(word):
    out = ""
    w = word.lower()
    for ch in w:
        if "a" <= ch <= "z":
            out = out + ch
    return out

def marks(guess, answer):
    res = []
    used = []
    i = 0
    while i < 5:
        res.append("⬛")
        used.append(False)
        i += 1
    i = 0
    while i < 5:
        if guess[i] == answer[i]:
            res[i] = "🟩"
            used[i] = True
        i += 1
    i = 0
    while i < 5:
        if res[i] == "🟩":
            i += 1
            continue
        j = 0
        while j < 5:
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
    mode = state.get("mode", "off")
    if mode == "off":
        return
    guesses = state.get("guesses", [])
    tag = "今日" if mode == "daily" else "练习"
    if state.get("done"):
        if guesses and guesses[-1] == state.get("answer", ""):
            space_text("✅ " + state["answer"].upper() + " · " + str(len(guesses)) + "/6 · " + tag)
        else:
            space_text("❌ 答案 " + state.get("answer", "").upper() + " · " + tag)
        return
    if not guesses:
        space_text("🟩 " + tag + "猜词 · 打 5 字母词 · 0/6")
        return
    last = guesses[-1]
    space_text(last.upper() + " " + marks(last, state["answer"]) + " · " + str(len(guesses)) + "/6")
