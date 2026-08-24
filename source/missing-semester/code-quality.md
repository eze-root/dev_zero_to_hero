# 第九讲：代码质量

> 官方 notes：[https://missing.csail.mit.edu/2026/code-quality/](https://missing.csail.mit.edu/2026/code-quality/)  
> 视频：[YouTube](https://www.youtube.com/watch?v=XBiLUNx84CQ)

```{note}
本文依照 Missing Semester 2026 官方 notes 的原文结构完整翻译；保留标题层级、命令示例、工具链接、引用与提示。练习采用 MyST exercise，并在官方题目之外补充折叠参考答案。
```


有多种工具和技术可以支持开发人员编写高质量的代码。在本次讲座中，我们将介绍：

- {ref}`格式化 <code-quality-formatting>`
- {ref}`Lint <code-quality-linting>`
- {ref}`测试 <code-quality-testing>`
- {ref}`预提交钩子 <code-quality-pre-commit-hooks>`
- {ref}`持续集成 <code-quality-continuous-integration>`
- {ref}`命令运行器 <code-quality-command-runners>`

作为额外主题，我们还将介绍 {ref}`正则表达式 <code-quality-regular-expressions>`，这是一个跨领域主题，它在代码质量（例如，用于运行与模式匹配的测试子集）以及 IDE 等其他领域（例如，用于搜索和替换）中具有应用程序。

其中许多工具都是特定于语言的（例如，Python 的 [Ruff](https://docs.astral.sh/ruff/) linter/formatter）。在某些情况下，工具将支持多种语言（例如，[Prettier](https://prettier.io/) 代码格式化程序）。然而，这些概念几乎是通用的——您可以找到适用于任何编程语言的代码格式化程序、linter、测试库等。

(code-quality-formatting)=
# 格式化

代码自动格式化程序会自动美化表面语法。这样，您可以专注于更深入和更具挑战性的问题，而自动格式化工具可以处理日常细节，例如 `'` 与 `"` 字符串语法的一致性、二元运算符周围有空格（`x + y` 而不是 `x+y`）、按排序顺序排列 `import` 语句以及避免超长行。代码格式化程序的一大好处是它们可以标准化所有开发代码库的开发人员的代码风格。

有些工具如Prettier是[高度可配置](https://prettier.io/docs/configuration)；您应该将项目的配置文件签入 [版本控制](version-control.md) 中。其他工具（例如 [Black](https://github.com/psf/black) 和 [gofmt](https://pkg.go.dev/cmd/gofmt)）的可配置性有限或没有可配置性，无法减少 [无意义的风格争论](https://en.wikipedia.org/wiki/Law_of_triviality)。

您可以使用代码格式化程序设置 {ref}`IDE集成 <development-environment-code-intelligence-and-language-servers>`，以便在您键入或保存文件时自动格式化您的代码。您还可以将 [编辑器配置](https://editorconfig.org/) 文件添加到您的项目中，该文件向您的 IDE 传达某些项目级设置，例如每种文件类型的缩进大小。

(code-quality-linting)=
# Lint

Linters 运行静态分析（分析您的代码而不运行它）以查找代码中的反模式和潜在问题。这些工具比自动格式化程序更深入，超越了表面语法。分析的深度因工具而异。

Linters 配备了_规则_列表，以及可以在项目级别配置的预设。某些 linter 规则会产生误报，因此您可以针对每个文件或每行禁用它们。

好的 linter 将有内置的帮助或文档来解释每个 linter 规则——规则正在寻找什么，为什么它不好，以及什么是代码模式的更好替代方案。例如，请参阅 [Ruff](https://docs.astral.sh/ruff/) 中 [SIM102](https://docs.astral.sh/ruff/rules/collapsible-if/) 规则的文档，该规则捕获 Python 代码中不必要的嵌套 `if` 语句。

有些 linter 不仅可以标记问题，还可以自动为您修复某些问题。

除了特定于语言的 linter 之外，另一个可能派上用场的工具是 [semgrep](https://github.com/semgrep/semgrep)，这是一种“语义 grep”工具，可在 AST 级别（而不是字符级别，如 grep）工作并支持多种语言。您可以使用 semgrep 轻松为您的项目编写自定义 linter 规则。例如，如果您想防止 Python 中危险的 `subprocess.Popen(..., shell=True)`，您可以使用以下命令找到该代码模式：

```bash
semgrep -l python -e "subprocess.Popen(..., shell=True, ...)"
```

(code-quality-testing)=
# 测试

软件测试是一种标准技术，可以增强您对代码正确性的信心。您编写代码，然后编写代码来执行您编写的代码，并在代码未按预期工作时引发错误。

您可以为不同粒度级别的代码块编写测试：针对单个功能的_单元测试_、针对模块或服务之间交互的_集成测试_以及针对端到端场景的_功能测试_。您可以进行_测试驱动开发_，即在编写任何实现代码之前编写测试。当您在代码中发现错误时，您可以编写_回归测试_，这样您就可以发现功能将来是否出现故障。您可以编写_基于属性的测试_，这是 Haskell 中 [QuickCheck](https://hackage.haskell.org/package/QuickCheck) 中首创的，并在许多库中实现，例如用于 Python 的 [Hypothesis](https://hypothesis.readthedocs.io/)。哪种测试方法正确取决于您的项目；很可能，您会采用某种组合。

如果您的程序具有数据库或 Web API 等外部依赖项，那么在测试中_模拟_这些依赖项可能会有所帮助，而不是让您的代码在测试时与第三方依赖项进行交互。

(code-quality-code-coverage)=
## 代码覆盖率

代码覆盖率是一个衡量测试好坏的指标。代码覆盖率会查看运行测试时执行的代码行，因此您可以确保覆盖所有代码路径。代码覆盖率工具可以向您显示逐行覆盖率，以指导您编写测试。 [Codecov](https://app.codecov.io) 等服务提供了 Web 界面，用于跟踪和查看项目历史记录中的代码覆盖率。

与任何指标一样，代码覆盖率并不完美；不要过度索引覆盖范围，专注于编写高质量的测试。

(code-quality-pre-commit-hooks)=
# 预提交钩子

Git 预提交 [钩子](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks) 通过 [pre-commit](https://pre-commit.com/) 框架变得更容易，在每次 Git 提交之前自动运行用户指定的代码。项目通常使用预提交钩子来运行格式化程序和 linter，有时还会在每次提交之前自动进行测试，以确保提交的代码与项目代码风格匹配并且不存在某些问题。

(code-quality-continuous-integration)=
# 持续集成

[GitHub Actions](https://github.com/features/actions) 等持续集成 (CI) 服务可以在您每次推送代码时（或在每个拉取请求或按计划）运行脚本。开发人员通常使用 CI 服务来运行代码质量工具，包括格式化程序、linter 和测试。对于编译型语言，可以确保代码可以编译；对于静态类型语言，您可以确保它进行类型检查。每次推送新提交时运行 CI 可以捕获代码主版本中引入的错误；在拉取请求上运行可以捕获贡献者提交的问题；按计划运行可以捕获外部依赖项的问题（例如，开发人员意外地将重大更改发布为 {ref}`语义兼容 <shipping-code-releases--versioning>`）。

由于 CI 脚本与开发人员计算机分开运行，因此您可以轻松地在那里运行长时间运行的作业。例如，可以利用这一点跨不同操作系统和编程语言版本运行测试矩阵，以确保软件在所有操作系统和编程语言版本上都能正常工作。

一般来说，在 CI 中运行的脚本不会直接对代码进行更改：它将以“仅检查”模式而不是“修复”模式运行工具，因此，例如，当代码不符合格式时，自动格式化程序将引发错误。

仓库的 README 中通常包含 [状态徽章](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge)，显示 CI 状态和其他信息（例如代码覆盖率）。例如，下面是 Missing Semester 的当前构建状态。

[![构建状态](https://github.com/missing-semester/missing-semester/actions/workflows/build.yml/badge.svg)](https://github.com/missing-semester/missing-semester/actions/workflows/build.yml) [![链接状态](https://github.com/missing-semester/missing-semester/actions/workflows/links.yml/badge.svg)](https://github.com/missing-semester/missing-semester/actions/workflows/links.yml)

> 我们使用 [proof-html](https://github.com/anishathalye/proof-html) GitHub Action 的 [链接检查器](https://github.com/missing-semester/missing-semester/blob/master/.github/workflows/links.yml) 经常失败，通常是由于第三方网站的问题。尽管如此，它仍然帮助我们捕获并修复了许多损坏的链接（有时是由于拼写错误，大多数时候是由于网站在没有添加重定向的情况下移动内容或网站消失）。

了解 CI 服务、格式化程序、linter 和测试库细节的一个好方法是通过示例。在 GitHub 上查找高质量的开源项目——在编程语言、领域、规模和范围等方面与您的项目越相似越好——并研究他们的 `pyproject.toml`、`.github/workflows/`、`DEVELOPMENT.md` 和其他相关文件。

(code-quality-continuous-deployment)=
## 持续部署

持续部署利用 CI 基础设施来实际_部署_更改。例如，Missing Semester 仓库使用持续部署到 GitHub Pages，以便每当我们 `git push` 更新讲义时，都会自动构建和部署该网站。您可以在 CI 中构建其他类型的 [产物](shipping-code.md)，例如应用程序的二进制文件或服务的 Docker 镜像。

(code-quality-command-runners)=
# 命令运行器

[just](https://github.com/casey/just) 等命令运行程序简化了在项目上下文中运行命令的任务。当您为项目构建代码质量基础架构时，您不希望让开发人员记住 `uv run ruff check --fix` 等命令。使用命令运行程序，这可以变成 `just lint`，并且您可以对开发人员可能想要为您的项目运行的所有不同工具进行类似的调用，例如 `just format`、`just typecheck` 等。

某些特定于语言的项目或包管理器内置了对此类功能的支持，这意味着您不需要使用 `just` 等与语言无关的工具。例如，[npm](https://nodejs.org/en/learn/getting-started/an-introduction-to-the-npm-package-manager) (Node.js) 的 `package.json` 的 `scripts` 部分和 [Hatch](https://hatch.pypa.io/) (Python) 的 `pyproject.toml` 的 `tool.hatch.envs.*.scripts` 部分支持此功能。

(code-quality-regular-expressions)=
# 正则表达式

_正则表达式_，通常缩写为“regex”，是一种用于表示字符串集的语言。正则表达式模式通常用于各种上下文（例如命令行工具和 IDE）中的模式匹配。例如，[ag](https://github.com/ggreer/the_silver_searcher) 支持用于代码库范围搜索的正则表达式模式（例如，`ag "import .* as .*"` 将查找 Python 中的所有重命名导入），而 [go test](https://pkg.go.dev/cmd/go#hdr-Test_packages) 支持用于选择测试子集的 `-run [regexp]` 选项。此外，编程语言具有用于正则表达式匹配的内置支持或第三方库，因此您可以使用正则表达式来实现模式匹配、验证和解析等功能。

为了帮助建立直觉，下面是一些正则表达式模式的示例。在本讲座中，我们使用 [Python 正则表达式语法](https://docs.python.org/3/library/re.html)。正则表达式有很多种风格，它们之间略有差异，特别是在更复杂的功能方面。您可以使用 [regex101](https://regex101.com/) 等在线正则表达式测试器来开发和调试正则表达式。

- `abc` --- 匹配文字“abc”。
- `missing|semester` --- 匹配字符串“missing”或字符串“semester”。
- `\d{4}-\d{2}-\d{2}` --- 匹配 YYYY-MM-DD 格式的日期，例如“2026-01-14”。除了确保字符串由四位数字、一个破折号、两位数字、一个破折号和两位数字组成之外，这不会验证日期，因此“2026-01-99”也与此正则表达式模式匹配。
- `.+@.+` --- 匹配电子邮件地址、包含一些文本的字符串，然后是“@”，然后是更多文本。这仅执行最基本的验证并匹配诸如“nonsense@@@email”之类的字符串。匹配电子邮件地址且没有误报或否定 [存在](https://pdw.ex-parrot.com/Mail-RFC822-Address.html) 的正则表达式，但不切实际。

(code-quality-regex-syntax)=
## 正则表达式语法

您可以在 [本文档](https://docs.python.org/3/library/re.html#regular-expression-syntax)（或在线提供的许多其他资源之一）中找到正则表达式语法的综合指南。以下是一些基本构建块：

- 当字符没有特殊含义时（在本例中为“abc”），`abc` 匹配文字字符串
- `.` 匹配任何单个字符
- `[abc]` 匹配括号中包含的单个字符（在此示例中为“a”、“b”或“c”）
- `[^abc]` 匹配除括号中包含的字符（例如“d”）之外的单个字符
- `[a-f]` 匹配括号中指示的范围内包含的单个字符（例如，“c”，但不是“q”）
- `a|b` 匹配任一模式（例如“a”或“b”）
- `\d` 匹配任何数字字符（例如“3”）
- `\w` 匹配任何单词字符（例如“x”）
- `\b` 匹配任何单词_边界_（例如，在字符串“Missing Semester”中，匹配“m”之前、“g”之后、“s”之前和“r”之后）
- `(...)` 匹配模式组
- `...?` 匹配零个或一个模式，例如 `words?` 匹配“word”或“words”
- `...*` 匹配任意数量的模式，例如 `.*` 匹配任意数量的任意字符
- `...+` 匹配一个或多个模式，例如 `\d+` 匹配一个或多个数字
- `...{N}` 与模式中的 N 个完全匹配，例如 `\d{4}` 表示 4 位数字
- `\.` 匹配文字“.”
- `\\` 匹配文字“\\”
- `^` 匹配行的开头
- `$` 匹配行尾

(code-quality-capture-groups-and-references)=
## 捕获组和引用

如果您使用正则表达式组 `(...)`，则可以引用匹配的子部分以进行提取或搜索和替换。例如，要从 YYYY-MM-DD 样式日期中仅提取月份，可以使用以下 Python 代码：

```python
>>> import re
>>> re.match(r"\d{4}-(\d{2})-\d{2}", "2026-01-14").group(1)
'01'
```

在文本编辑器中，您可以在替换模式中使用引用捕获组。不同 IDE 的语法可能有所不同。例如，在 VS Code 中，您可以使用 `$1`、`$2` 等变量，而在 Vim 中，您可以使用 `\1`、`\2` 等来引用组。

(code-quality-limitations)=
## 局限性

[正则语言](https://en.wikipedia.org/wiki/Regular_language)功能强大但有限；有些字符串无法表示为标准正则表达式（例如，编写一个与字符串集 {a^n b^n \| n ≥ 0} 匹配的正则表达式是 [不可能](https://en.wikipedia.org/wiki/Pumping_lemma_for_regular_languages)，该正则表达式是由多个“a”后跟相同数量的“b”组成的字符串集；更实际的是，像 HTML 这样的语言不是正则语言）。在实践中，现代正则表达式引擎支持诸如前瞻和反向引用之类的功能，这些功能将支持扩展到正则语言之外，并且它们实际上非常有用，但重要的是要知道它们的表达能力仍然有限。对于更复杂的语言，您可能需要使用一种功能更强大的解析器（例如，请参阅 [pyparsing](https://github.com/pyparsing/pyparsing)、[PEG](https://en.wikipedia.org/wiki/Parsing_expression_grammar) 解析器）。

(code-quality-learning-regex)=
## 学习正则表达式

我们建议学习基础知识（我们在本讲座中介绍的内容），然后根据需要查看正则表达式参考，而不是记住整个语言。

对话式人工智能工具可以有效地帮助您生成正则表达式模式。例如，尝试使用以下查询提示您最喜欢的 LLM：

```
Write a Python-style regex pattern that matches the requested path from log lines from Nginx. Here is an example log line:

169.254.1.1 - - [09/Jan/2026:21:28:51 +0000] "GET /feed.xml HTTP/2.0" 200 2995 "-" "python-requests/2.32.3"
```

## Exercises

```{exercise} 配置格式、lint 与 pre-commit
:label: exercise-quality-tooling

为真实项目配置 formatter、linter 和 pre-commit；可让智能体协助修复 lint，但必须让它运行检查并审查结果。
```

```{solution} exercise-quality-tooling
:class: dropdown

Python 示例可用 Ruff：在 `pyproject.toml` 配置规则，运行 `uv run ruff format .`、`uv run ruff check --fix .`，再把 `ruff-format`/`ruff` hook 固定到明确 revision。验收：全仓 check 通过、第二次运行无 diff、现有测试通过；规则抑制有理由，智能体没有为“清零”而降低规则级别。
```

```{exercise} 测试与覆盖率
:label: exercise-quality-coverage

为项目写单元测试并生成 HTML 覆盖率报告；人工和智能体分别补充测试，评价测试质量。
```

```{solution} exercise-quality-coverage
:class: dropdown

Python 可运行 `uv run pytest --cov=PACKAGE --cov-branch --cov-report=html`，打开 `htmlcov/index.html`。优先补边界与失败路径，而不是逐行制造无断言测试。对 AI 测试做 mutation 思考：如果故意破坏实现，它会失败吗？是否只复述当前实现、过度 mock 或依赖执行顺序？
```

```{exercise} 建立 CI 并验证失败路径
:label: exercise-quality-ci

让 CI 在每次 push 运行格式检查、lint 和测试；故意引入 lint 问题，确认它能阻止通过。
```

```{solution} exercise-quality-ci
:class: dropdown

工作流应 checkout、按锁文件安装、运行与本地相同的 `format-check/lint/test` 命令，并启用缓存但不缓存秘密。先在分支提交故意违规，观察 job 非零退出和清晰日志，再修复。把该 job 设为受保护分支必需检查，才能真正阻止合并。
```

```{exercise} grep 与 Semgrep 对比
:label: exercise-quality-semgrep

用 grep regex 查找 `subprocess.Popen(..., shell=True)`，设计代码使 regex 漏报，再看 Semgrep 是否仍能匹配。
```

```{solution} exercise-quality-semgrep
:class: dropdown

字符模式很容易被换行、额外参数、空格、关键字顺序或别名破坏，例如 `subprocess.Popen(cmd,\n shell = True)`。Semgrep 模式 `subprocess.Popen(..., shell=True, ...)` 基于语法树，通常仍能识别格式变化；导入别名和间接变量也可能需要更完整的数据流规则。安全扫描不能只依赖单一模式。
```

```{exercise} 精确替换 Markdown 列表标记
:label: exercise-quality-markdown-bullets

在官方 notes 源文件中，把 `-` 无序列表标记替换为 `*`，但不要替换普通连字符。
```

```{solution} exercise-quality-markdown-bullets
:class: dropdown

在支持多行的编辑器中搜索 `^(\s*)-\s+`，替换为 `$1* `（具体捕获引用随工具变化）。命令行可先预览：`sed -E 's/^([[:space:]]*)-([[:space:]]+)/\1*\2/' file`。检查 diff，尤其是 fenced code block 中看似列表的内容；通用 Markdown 变换更适合 AST parser。
```

```{exercise} 从 JSON 文本提取 name
:label: exercise-quality-json-name

先写 regex 从 `{"name": "Alyssa P. Hacker", "college": "MIT"}` 捕获姓名；再支持姓名中的转义双引号；最后改用 JSON parser 从 stdin 读取并向 stdout 输出姓名。
```

````{solution} exercise-quality-json-name
:class: dropdown

限制在题目字段顺序和 JSON 字符串转义下，可用 Python regex：

```python
r'"name"\s*:\s*"((?:\\.|[^"\\])*)"'
```

`(?:\\.|[^"\\])*` 匹配转义序列或非引号/反斜杠字符。但正确方案是解析 JSON：

```bash
python -c 'import json,sys; print(json.load(sys.stdin)["name"])'
```

parser 会正确处理空白、字段顺序、Unicode 和转义；regex 适合受控局部模式，不适合重建 JSON 语法。
````

## 许可与署名

本页依据 MIT Missing Semester 2026 第九讲[官方 notes](https://missing.csail.mit.edu/2026/code-quality/)整理，原材料采用 [CC BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可。
