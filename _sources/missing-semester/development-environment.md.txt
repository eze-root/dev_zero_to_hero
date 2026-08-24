# 第三讲：开发环境与工具

> 官方 notes：[Development Environment and Tools](https://missing.csail.mit.edu/2026/development-environment/)  
> 视频：[YouTube](https://www.youtube.com/watch?v=QnM1nVzrkx8)

```{note}
开发环境不是某一个编辑器，而是编辑、理解、运行、检查代码的一组工具。应当基本熟悉图形 IDE 与终端工作流，并至少熟练掌握其中一种。
```

## 编辑器与 Vim

图形 IDE 通常易于上手、集成完整；tmux、Vim、Shell 与语言工具组成的终端工作流更轻量，也适合远程或无法安装 GUI 的环境。若尚无偏好，官方建议从 VS Code 开始。

编程时，大部分时间花在定位、阅读和局部修改，而不是连续输入长段文字。Vim 针对这种分布设计：它是模态编辑器，也把编辑接口设计成一门可组合的语言。

- Normal：移动和执行编辑动作；
- Insert：插入文本；
- Replace：覆盖文本；
- Visual / Visual Line / Visual Block：选择；
- Command-line：运行 `:` 命令。

`Esc` 返回 Normal；`i` 插入，`R` 替换，`v`/`V`/`Ctrl-v` 进入三种选择模式，`:` 进入命令行。Vim 的动作像“动词 + 名词”：`d` 删除，`c` 修改，`y` 复制；`w` 单词，`$` 行尾，`i(` 括号内部。因此 `dw` 删除单词，`d$` 删除到行尾，`ci(` 修改当前括号内部。数量也能组合：`3w`、`5j`、`7dw`。

常见移动包括 `hjkl`、`w/b/e`、`0/^/$`、`gg/G`、`%`、`f{char}` 与 `/regex`。真正的学习方法不是背完表格，而是先完成 `vimtutor`，再在日常编辑器中启用 Vim 模式；每次发现低效动作，就查找更好的组合。

## 代码智能与语言服务器

语言服务器通过 [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) 把语言语义能力与编辑器解耦。它通常提供：

- 补全与悬浮文档；
- 跳转定义和查找引用；
- 自动导入、整理导入；
- 格式化、类型检查和 lint 诊断。

“扩展已经安装”不等于“环境已经正确”。例如 Python 语言服务器必须指向项目实际使用的虚拟环境，才能识别依赖；Go 的 `gopls`、Rust 的 rust-analyzer 也需要在正确的项目根目录和工具链中运行。验收时应跳到第三方依赖定义、查找引用并观察诊断，而不只看语法高亮。

## AI 辅助开发的三种形态

AI 补全在光标处续写，适合样板代码和局部模式；注释、函数名和类型提示都会成为上下文。行内对话对选区提出修改，适合重构一小段已有代码。编码智能体则能搜索仓库、编辑多个文件并运行命令，后续课程会单独讨论。

无论哪种形态，都要审查边界条件、依赖选择、安全性和测试结果。模型生成“看起来合理”的代码很容易，但它并不知道项目真实约束，除非这些约束存在于上下文并能通过工具验证。

## IDE 扩展能力

开发容器能把工具链放入隔离、可复用的容器；Remote SSH 允许在远端机器编辑运行；协同编辑支持多人同步修改。扩展拥有读取代码、运行命令甚至访问凭据的能力，应核对发布者、权限与维护状态，保持最小安装集合。

## Exercises

```{exercise} 一个月的 Vim 模式
:label: exercise-dev-vim-month

在编辑器、Shell 等支持 Vim 模式的软件中启用它，连续使用一个月；每次发现低效动作时记录问题并查找更好的命令。
```

```{solution} exercise-dev-vim-month
:class: dropdown

这是一项习惯训练，没有唯一输出。建议维护日志：日期、原动作、学到的命令、是否形成肌肉记忆。最低验收是熟练切换模式，使用 `hjkl`、词/行移动、搜索、`d/c/y/p`、撤销重做，并能在不依赖鼠标的情况下完成一次真实改动。
```

```{exercise} 完成 VimGolf
:label: exercise-dev-vimgolf

从 [VimGolf](https://www.vimgolf.com/) 选择并完成一道挑战。
```

```{solution} exercise-dev-vimgolf
:class: dropdown

先用自己能理解的命令完成，再阅读高分解法。不要只追求最少按键；解释每个动作为什么成立，并挑出一到两个可迁移到日常工作的组合，才算完成学习闭环。
```

```{exercise} 配置语言服务器
:label: exercise-dev-lsp

为真实项目配置 IDE 扩展和语言服务器，确认包括第三方依赖在内的跳转定义、引用查找、补全与诊断都工作。
```

```{solution} exercise-dev-lsp
:class: dropdown

检查清单：编辑器识别正确项目根；选择了正确解释器/SDK；语言服务器日志无启动错误；能从调用跳到项目函数和已安装依赖；故意制造类型或语法问题时出现诊断；重命名能更新引用。只出现颜色不代表 LSP 成功。
```

```{exercise} 评估一个扩展
:label: exercise-dev-extension

浏览编辑器扩展列表，选择并安装一个真正有用的扩展。
```

```{solution} exercise-dev-extension
:class: dropdown

记录它解决的问题、发布者、所需权限、最近更新时间与替代方案；安装后完成一个具体任务，并比较安装前后的步骤。若收益不明确或索取无关权限，应卸载。扩展越少，启动速度、稳定性与供应链风险通常越容易控制。
```

## 许可与署名

本页依据 MIT Missing Semester 2026 第三讲[官方 notes](https://missing.csail.mit.edu/2026/development-environment/)整理，原材料采用 [CC BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可。
