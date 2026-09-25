# Clink CVX Flick

Clink 插件：通过字母键上滑执行常用编辑动作。

## 手势

- **C ↑**：复制当前选区
- **V ↑**：粘贴剪贴板内容
- **X ↑**：剪切当前选区

## 要求

- 需要支持 `on_swipe(key, direction, state)` 的 Clink 版本
- 粘贴需要 Clink 的 **Full Access / 完全访问**
- 插件开启后会暂时关闭与上滑冲突的 Swipe Typing 和 Predictive Flick；关闭后恢复原设置

## 安装

在 Clink → General → Repositories 中添加：

`dayifulalala-del/-clink-cvx-flick`

然后进入 Plugins，安装 **CVX Flick**。

## 当前限制

Clink 当前插件接口没有公开 `select_all()` / `select_word()`，所以插件不会主动创建选区。复制和剪切作用于你已经选中的文字。

## 发布

修改 `Plugins/cvx-flick.py` 并推送到 `main` 后，GitHub Actions 会自动打包 `.clinkplugin` 并发布 Release。
