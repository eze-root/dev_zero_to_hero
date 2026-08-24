# 第三讲：开发环境与工具

> 官方 notes：[https://missing.csail.mit.edu/2026/development-environment/](https://missing.csail.mit.edu/2026/development-environment/)  
> 视频：[YouTube](https://www.youtube.com/watch?v=QnM1nVzrkx8)

```{note}
本文依照 Missing Semester 2026 官方 notes 的原文结构完整翻译；保留标题层级、命令示例、工具链接、引用与提示。练习采用 MyST exercise，并在官方题目之外补充折叠参考答案。
```


_开发环境_是一组用于开发软件的工具。开发环境的核心是文本编辑功能，以及语法突出显示、类型检查、代码格式化和自动补全等附带功能。 [VS Code][vs-code] 等集成开发环境 (IDE) 将所有这些功能汇集到一个应用程序中。基于终端的开发工作流程结合了 [tmux](https://github.com/tmux/tmux)（终端多路复用器）、[Vim](https://www.vim.org/)（文本编辑器）、[Zsh](https://www.zsh.org/)（shell）等工具和特定于语言的命令行工具，如 [Ruff](https://docs.astral.sh/ruff/)（Python linter 和代码格式化程序）和 [Mypy](https://mypy-lang.org/)（Python 类型检查器）。

IDE 和基于终端的工作流程各有其优点和缺点。例如，图形 IDE 可以更容易学习，并且当今的 IDE 通常具有更好的开箱即用的 AI 集成，例如 AI 自动补全；另一方面，基于终端的工作流程是轻量级的，在没有 GUI 或无法安装软件的环境中，它们可能是您唯一的选择。我们建议您对两者都有基本的熟悉，并至少掌握其中一种。如果您还没有首选 IDE，我们建议您从 [VS Code][vs-code] 开始。

在本次讲座中，我们将介绍：

- {ref}`文本编辑和 Vim <development-environment-text-editing-and-vim>`
- {ref}`代码智能和语言服务器 <development-environment-code-intelligence-and-language-servers>`
- {ref}`人工智能驱动的开发 <development-environment-ai-powered-development>`
- {ref}`扩展和其他 IDE 功能 <development-environment-extensions-and-other-ide-functionality>`

[vs-code]: https://code.visualstudio.com/

(development-environment-text-editing-and-vim)=
# 文本编辑和 Vim

编程时，您大部分时间都花在浏览代码、阅读代码片段以及编辑代码上，而不是编写长流或从上到下读取文件。 [Vim] 是一个针对这种任务分配进行了优化的文本编辑器。

**Vim 的哲学。** Vim 有一个美好的想法作为其基础：它的界面本身就是一种编程语言，专为导航和编辑文本而设计。击键（带有助记名称）是命令，并且这些命令是可组合的。 Vim 避免使用鼠标，因为它太慢； Vim 甚至避免使用方向键，因为它需要太多的移动。结果是：一个编辑器感觉就像一个脑机接口，并且与您的思考速度相匹配。

**其他软件中的 Vim 支持。** 您不必使用 [Vim] 本身即可从其核心思想中受益。许多涉及任何类型文本编辑的程序都支持“Vim 模式”，无论是作为内置功能还是作为插件。例如，VS Code 有 [VSCodeVim](https://marketplace.visualstudio.com/items?itemName=vscodevim.vim) 插件，Zsh 有用于 Vim 模拟的 [内置支持](https://zsh.sourceforge.io/Guide/zshguide04.html)，甚至 Claude Code 有用于 Vim 编辑器模式的 [内置支持](https://code.claude.com/docs/en/interactive-mode#vim-editor-mode)。您使用的任何涉及文本编辑的工具很可能都以某种方式支持 Vim 模式。

(development-environment-modal-editing)=
## 模态编辑

Vim 是一个_模态编辑器_：它针对不同类别的任务有不同的操作模式。

- **普通**：用于移动文件并进行编辑
- **插入**：用于插入文本
- **替换**：用于替换文本
- **视觉**（纯文本、行或块）：用于选择文本块
- **命令行**：用于运行命令

按键在不同的操作模式下具有不同的含义。例如，字母 `x` 在插入模式下只会插入一个文字字符“x”，但在普通模式下，它将删除光标下的字符，在可视模式下，它将删除所选内容。

在默认配置中，Vim 在左下角显示当前模式。初始/默认模式为正常模式。您通常会在正常模式和插入模式之间度过大部分时间。

您可以通过按 `<ESC>`（退出键）来更改模式，从任何模式切换回正常模式。在正常模式下，使用 `i` 进入插入模式，使用 `R` 进入替换模式，使用 `v` 进入可视模式，使用 `V` 进入可视行模式，使用 `<C-v>` 进入可视块模式（Ctrl-V，有时也写作 `^V`），以及使用 `:` 进入命令行模式。

使用 Vim 时经常使用 `<ESC>` 键：考虑将 Caps Lock 重新映射为 Escape ([macOS 说明](https://vim.fandom.com/wiki/Map_caps_lock_to_escape_in_macOS)) 或使用简单的按键序列为 `<ESC>` 创建 [替代映射](https://vim.fandom.com/wiki/Avoid_the_escape_key#Mappings)。

(development-environment-basics-inserting-text)=
## 基础知识：插入文本

在正常模式下，按 `i` 进入插入模式。现在，Vim 的行为就像任何其他文本编辑器一样，直到您按 `<ESC>` 返回正常模式。这与上面解释的基础知识一起，就是开始使用 Vim 编辑文件所需的全部内容（如果您将所有时间都花在插入模式下编辑，则效率不是特别高）。

(development-environment-vims-interface-is-a-programming-language)=
## Vim 的界面是一种编程语言

Vim 的界面是一种编程语言。击键（带有助记名称）是命令，这些命令_compose_。这可以实现高效的移动和编辑，尤其是当命令成为肌肉记忆时，就像一旦您学会了键盘布局，打字就会变得超级高效一样。

(development-environment-movement)=
### 移动

您应该将大部分时间花在正常模式下，使用移动命令来导航文件。 Vim 中的动作也称为“名词”，因为它们指的是文本块。

- 基本动作：`hjkl`（左、下、上、右）
- 字：`w`（下一个字）、`b`（字开头）、`e`（字结尾）
- 行：`0`（行开头）、`^`（第一个非空白字符）、`$`（行结尾）
- 屏幕：`H`（屏幕顶部）、`M`（屏幕中间）、`L`（屏幕底部）
- 滚动：`Ctrl-u`（向上）、`Ctrl-d`（向下）
- 文件：`gg`（文件开头）、`G`（文件结尾）
- 行号：`:{number}<CR>` 或 `{number}G`（行 {number}）
    - `<CR>` 指回车/回车键
- 其他：`%`（匹配项，如括号或大括号）
- 查找：`f{character}`、`t{character}`、`F{character}`、`T{character}`
    - 在当前行查找/前进/后退{字符}
    - `,` / `;` 用于导航比赛
- 搜索：`/{regex}`、`n` / `N` 用于导航匹配

(development-environment-selection)=
### 选择

视觉模式：

- 视觉：`v`
- 视线：`V`
- 视觉块：`Ctrl-v`

可以使用移动键进行选择。

(development-environment-edits)=
### 编辑

您过去使用鼠标执行的所有操作现在都可以使用键盘使用与移动命令组合的编辑命令来执行。从这里开始，Vim 的界面开始看起来像一种编程语言。 Vim 的编辑命令也称为“动词”，因为动词作用于名词。

- `i` 进入插入模式
    - 但是为了操作/删除文本，想要使用退格键以外的东西
- `o` / `O` 在下方/上方插入行
- `d{motion}` 删除{动作}
    - 例如`dw` 是删除字，`d$` 是删除到行尾，`d0` 是删除到行首
- `c{motion}` 更改{动作}
    - 例如`cw` 是更改字
    - 例如 `d{motion}` 后跟 `i`
- `x` 删除字符（相当于 `dl`）
- `s` 替换字符（相当于 `cl`）
- 视觉模式+操控
    - 选择文本，`d` 删除它或 `c` 更改它
- `u` 撤消，`<C-r>` 重做
- `y` 复制/“猛拉”（其他一些命令，如 `d` 也复制）
- `p` 粘贴
- 还有更多需要学习的内容：例如，`~` 翻转字符的大小写，`J` 将行连接在一起

(development-environment-counts)=
### 计数

您可以将名词和动词与计数结合起来，这将执行给定的操作多次。

- `3w` 向前移动 3 个字
- `5j` 向下移动 5 行
- `7dw` 删除7个字

(development-environment-modifiers)=
### 修饰符

您可以使用修饰语来更改名词的含义。一些修饰符是 `i`，意思是“内部”或“内部”，以及 `a`，意思是“周围”。

- `ci(` 更改当前括号内的内容
- `ci[` 更改当前方括号内的内容
- `da'` 删除单引号字符串，包括周围的单引号

(development-environment-putting-it-all-together)=
## 组合使用

这是一个损坏的 [Fizz Buzz](https://en.wikipedia.org/wiki/Fizz_buzz) 实现：

```python
def fizz_buzz(limit):
    for i in range(limit):
        if i % 3 == 0:
            print("fizz", end="")
        if i % 5 == 0:
            print("fizz", end="")
        if i % 3 and i % 5:
            print(i, end="")
        print()

def main():
    fizz_buzz(20)
```

我们使用以下命令序列来修复问题，从正常模式开始：

- Main 从未被调用
    - `G` 跳转到文件末尾
    - `o` **在下面新建一行
    - 输入 `if __name__ == "__main__": main()`
        - 如果您的编辑器支持 Python 语言，它可能会在插入模式下为您执行一些自动缩进
    - `<ESC>` 返回正常模式
- 从 0 而不是 1 开始
    - `/` 后跟 `range` 和 `<CR>` 搜索“范围”
    - `ww` 向前移动两个 **字**字（您也可以使用 `2w`，但实际上，对于少量计数，通常会重复按键而不是使用计数功能）
    - `i` 切换到**i**插入模式，并添加 `1,`
    - `<ESC>` 返回正常模式
    - `e` 跳转到下一个单词的**e**nd
    - `a` 开始**附加文本，并添加 `+ 1`
    - `<ESC>` 返回正常模式
- 打印 5 的倍数“fizz”
    - `:6<CR>` 转到第 6 行
    - `ci"` 至 **c**hange **i**nside '**"**'，更改为 `"buzz"`
    - `<ESC>` 返回正常模式

(development-environment-learning-vim)=
## 学习 Vim

学习 Vim 的最佳方法是学习基础知识（到目前为止我们已经介绍过），然后在所有软件中启用 Vim 模式并开始在实践中使用它。避免使用鼠标或箭头键的诱惑；在某些编辑器中，您可以解除方向键的绑定，以强迫自己养成良好的习惯。

(development-environment-additional-resources)=
### 其他资源

- 此类的上一次迭代中的 [Vim讲座](https://missing.csail.mit.edu/2020/editors/) --- 我们在那里更深入地介绍了 Vim
- `vimtutor` 是随 Vim 一起安装的教程 --- 如果安装了 Vim，您应该能够从 shell 运行 `vimtutor`
- [Vim Adventures](https://vim-adventures.com/) 是一个学习 Vim 的游戏
- [Vim Tips Wiki](https://vim.fandom.com/wiki/Vim_Tips_Wiki)
- [Vim Advent Calendar](https://vimways.org/2019/) 有各种 Vim 技巧
- [VimGolf](https://www.vimgolf.com/) 是 [代码高尔夫](https://en.wikipedia.org/wiki/Code_golf)，但编程语言是 Vim 的 UI
- [Vi/Vim Stack Exchange](https://vi.stackexchange.com/)
- [Vim Screencasts](http://vimcasts.org/)
- [Practical Vim](https://pragprog.com/titles/dnvim2/)（书籍）

[Vim]: https://www.vim.org/

(development-environment-code-intelligence-and-language-servers)=
# 代码智能和语言服务器

IDE 通常提供特定于语言的支持，需要通过连接到实现 [语言服务器协议](https://microsoft.github.io/language-server-protocol/) 的_语言服务器_的 IDE 扩展来理解代码的语义。例如，[VS Code 的 Python 扩展](https://marketplace.visualstudio.com/items?itemName=ms-python.python) 依赖于 [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)，[VS Code 的 Go 扩展](https://marketplace.visualstudio.com/items?itemName=golang.go) 依赖于第一方 [gopls](https://go.dev/gopls/)。通过安装适用于您使用的语言的扩展和语言服务器，您可以在 IDE 中启用许多特定于语言的功能，例如：

- **代码补全。** 更好的自动补全和自动建议，例如在键入 `object.` 后能够查看对象的字段和方法。
- **内联文档。** 查看有关悬停和自动建议的文档。
- **跳转到定义。** 从使用站点跳转到定义，例如能够从字段引用 `object.field` 跳转到字段的定义。
- **查找引用。** 与上述相反，查找引用特定项目（例如字段或类型）的所有站点。
- **帮助导入。** 组织导入、删除未使用的导入、标记丢失的导入。
- **代码质量。** 这些工具可以独立使用，但此功能通常也由语言服务器提供。代码格式化自动缩进和自动格式化代码以及类型检查器和 linter 会在您键入时查找代码中的错误。我们将在 [代码质量讲座](code-quality.md) 中更深入地介绍此类功能。

(development-environment-configuring-language-servers)=
## 配置语言服务器

对于某些语言，您所需要做的就是安装扩展程序和语言服务器，然后一切就完成了。对于其他人来说，为了从语言服务器中获得最大的好处，您需要告诉 IDE 您的环境。例如，将 VS Code 指向 [Python环境](https://code.visualstudio.com/docs/python/environments) 将使语言服务器能够查看您安装的软件包。我们的 [打包与交付代码讲座](shipping-code.md) 更深入地介绍了环境。

根据语言的不同，您可能可以为语言服务器配置一些设置。例如，使用 VS Code 中的 Python 支持，您可以对不使用 Python 可选类型注释的项目禁用静态类型检查。

(development-environment-ai-powered-development)=
# AI 辅助开发

自 2021 年中期使用 OpenAI 的 [Codex 模型](https://openai.com/index/openai-codex/) 推出 [GitHub Copilot][github-copilot] 以来，[LLM](https://en.wikipedia.org/wiki/Large_language_model) 已在软件工程中广泛采用。目前正在使用三种主要的形式：自动补全、行内对话和编码智能体。

[github-copilot]: https://github.com/features/copilot/ai-code-editor

(development-environment-autocomplete)=
## 自动补全

AI 支持的自动补全功能与 IDE 中的传统自动补全功能具有相同的交互形式，可在您键入时建议在光标位置进行完成。有时，它被用作“正常工作”的被动功能。除此之外，AI 自动补全通常是使用代码注释的 [提示](https://en.wikipedia.org/wiki/Prompt_engineering)。

例如，让我们编写一个脚本来下载这些讲义的内容并提取所有链接。我们可以从以下开始：

```python
import requests

def download_contents(url: str) -> str:
```

该模型将自动补全函数的主体：

```python
    response = requests.get(url)
    return response.text
```

我们可以使用注释进一步指导完成。例如，如果我们开始编写一个函数来提取所有 Markdown 链接，但它没有一个特别描述性的名称：

```python
def extract(contents: str) -> list[str]:
```

该模型将自动补全如下内容：

```python
    lines = contents.splitlines()
    return [line for line in lines if line.strip()]
```

我们可以通过代码注释来指导完成：

```python
def extract(content: str) -> list[str]:
    # 从内容中提取所有 Markdown 链接
```

这次，模型给出了更好的完成：

```python
    import re
    pattern = r'\[.*?\]\((.*?)\)'
    return re.findall(pattern, content)
```

在这里，我们看到了这个人工智能编码工具的一个缺点：它只能在光标处提供补全。在这种情况下，最好将 `import re` 放在模块级别，而不是放在函数内部。

上面的示例使用了一个命名不当的函数来演示如何使用注释来引导代码补全；在实践中，您想要编写具有更具描述性命名的函数的代码，例如 `extract_links`，并且您想要编写文档字符串（基于此，模型应该生成类似于上面的完成）。

为了演示目的，我们可以完成脚本：

```python
print(extract(download_contents("https://raw.githubusercontent.com/missing-semester/missing-semester/refs/heads/master/_2026/development-environment.md")))
```

(development-environment-inline-chat)=
## 行内对话

行内对话可让您选择一行或一个代码块，然后直接提示 AI 模型提出编辑建议。在这种交互模式下，模型可以对现有代码进行更改（这与自动补全不同，自动补全仅完成光标之外的代码）。

继续上面的示例，假设我们决定不使用第三方 `requests` 库。我们可以选择相关的三行代码，调用行内对话，然后说：

```
use built-in libraries instead
```

该模型提出：

```python
from urllib.request import urlopen

def download_contents(url: str) -> str:
    with urlopen(url) as response:
        return response.read().decode('utf-8')
```

(development-environment-coding-agents)=
## 编码智能体

[智能体编程](agentic-coding.md) 讲座中深入介绍了编码智能体。

(development-environment-recommended-software)=
## 推荐软件

一些流行的 AI IDE 包括带有 [GitHub Copilot][github-copilot] 扩展和 [光标](https://cursor.com/) 的 [VS Code][vs-code]。 GitHub Copilot 目前可供 [学生免费](https://github.com/education/students)、流行开源项目的教师和维护者使用。这是一个快速发展的空间。许多领先产品具有大致相同的功能。

(development-environment-extensions-and-other-ide-functionality)=
# 扩展和其他 IDE 功能

IDE 是强大的工具，_扩展_使其变得更加强大。我们无法在一次讲座中涵盖所有这些功能，但在这里我们提供了一些流行扩展的指导。我们鼓励您自己探索这个空间；网上有许多流行的 IDE 扩展列表，例如 Vim 插件的 [Vim Awesome](https://vimawesome.com/) 和 [VS Code 扩展按受欢迎程度排序](https://marketplace.visualstudio.com/search?target=VSCode&category=All%20categories&sortBy=Installs)。

- [开发容器](https://containers.dev/)：受流行的 IDE（例如 [VS 代码支持](https://code.visualstudio.com/docs/devcontainers/containers)）支持，开发容器允许您使用容器来运行开发工具。这对于可移植性或隔离很有帮助。 [打包与交付代码讲座](shipping-code.md) 更深入地涵盖了容器。
- 远程开发：使用 SSH 在远程计算机上进行开发（例如，使用 [VS Code 的远程 SSH 插件](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh)）。例如，如果您想在云中强大的 GPU 机器上开发和运行代码，这会很方便。
- 协作编辑：以 Google Docs 风格编辑同一文件（例如，使用 [VS Code 的 Live Share 插件](https://marketplace.visualstudio.com/items?itemName=MS-vsliveshare.vsliveshare)）。

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
