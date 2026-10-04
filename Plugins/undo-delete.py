# ---
# name: 删词后悔药
# icon: arrow.uturn.backward
# summary: 记住刚删掉的词，顶栏点一下就恢复回来
# version: 1.1
# author: 奥寺美紀
# ---

# 删词后悔药 (Undo delete)
#
# 手机键盘没有撤销键：删错一个词只能重打。这个插件在旁边看着
# 输入框，光标前的文字一旦变短，就把消失的那一段记下来（最多
# 最近 20 段、每段不超过 200 字）。顶栏会出现一个恢复按钮
# （只有图标、不带文字），点一下就把最近删掉的那段插回光标处。
#
# 实现要点：删除没有专门的事件可用，所以在几个钩子里对比
# context() 的 before 快照做差分。只有「光标前文字是上次的
# 前缀、且变短了」才记，等于只认末尾删除；把光标移到文中编辑
# 时自动重新同步，不会记错。密码框里不看也不记。

KEEP = 20
MAXCH = 200
TAIL = 1000

def initial():
    return {"stack": [], "last": "", "field": "default"}

def settings(state):
    return vstack([
        text("删掉的词会暂存在这里。在顶栏（Layout > Top bar）把「Undo delete」按钮加上（只占一个图标的位置），删错时点它就能把最近删掉的一段插回来。", size=13),
        text("当前暂存 " + str(len(state.get("stack", []))) + " 段，只存在这台设备上，密码框里的内容不会被记录。", size=12, color="gray"),
        button("清空记录", "clear", style="destructive"),
    ])

def bar_items(state):
    if state.get("stack"):
        return [bar_button("undo", "Undo delete", icon="arrow.uturn.backward")]
    return []

def on_action(action, value, state):
    if action == "undo":
        sample(state)
        stack = state.get("stack", [])
        if stack:
            chunk = stack.pop()
            state["stack"] = stack
            insert(chunk)
            banner("已恢复：" + chunk[:12])
    elif action == "clear":
        state["stack"] = []
    return state

def on_open(state):
    sync(state)
    return state

def on_field(kind, state):
    state["field"] = kind
    if kind == "password":
        state["last"] = ""
    else:
        sync(state)
    return state

def on_backspace(state):
    sample(state)
    return state

def on_word(word, state):
    sample(state)
    return state

def on_suggestion(word, state):
    sample(state)
    return state

def sync(state):
    # 换了输入框：只重新对齐，不把差异当作删除。
    if state.get("field") == "password":
        state["last"] = ""
    else:
        state["last"] = context()["before"][-TAIL:]

def sample(state):
    if state.get("field") == "password":
        state["last"] = ""
        return
    cur = context()["before"][-TAIL:]
    old = state.get("last", "")
    if old and cur != old and old.startswith(cur):
        removed = old[len(cur):]
        if 1 <= len(removed) <= MAXCH and removed.strip() and removed != old and "\n" not in removed:
            stack = state.get("stack", [])
            if not stack or stack[-1] != removed:
                stack.append(removed)
                state["stack"] = stack[-KEEP:]
    state["last"] = cur
