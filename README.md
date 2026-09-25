# Clink Plugins

个人维护的 Clink 插件集合仓库。

## 安装仓库

在 Clink → General → Repositories 中添加：

`dayifulalala-del/-clink-cvx-flick`

然后进入 **Plugins** 页面安装需要的插件。

## 当前插件

| 插件 | 版本 | 功能 |
|---|---:|---|
| **CVX Flick** | 1.1 | C 上滑复制、V 上滑粘贴、X 上滑剪切当前选区 |
| **随机色彩按键** | 1.0 | 按下任意按键时，为当前按键覆盖随机颜色；松开后恢复 |

### CVX Flick

- **C ↑**：复制当前选区
- **V ↑**：粘贴剪贴板内容
- **X ↑**：剪切当前选区
- 粘贴需要 Clink 的 **Full Access / 完全访问**
- Clink 当前没有公开 `select_all()` / `select_word()`，所以复制和剪切作用于已经选中的文字

### 随机色彩按键

- 每次按下按键生成一种随机亮色
- 松开按键后恢复原键盘外观
- 使用 `key_down` / `key_up` 和 `key_art`
- 需要在 Clink 中授予对应的 Typing / 按键数据权限

## 仓库结构

- `Plugins/`：插件源码或可直接发布的 `.clinkplugin`
- `tools/build-manifest.py`：生成 Clink 仓库 manifest
- `.github/workflows/release.yml`：自动打包并发布 Release

每次修改 `Plugins/` 后推送到 `main`，GitHub Actions 会自动重新生成 Release。
