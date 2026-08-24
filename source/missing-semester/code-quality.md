# 第九讲：代码质量

> 官方 notes：[Code Quality](https://missing.csail.mit.edu/2026/code-quality/)  
> 视频：[YouTube](https://www.youtube.com/watch?v=XBiLUNx84CQ)

```{note}
高质量不是靠一次人工检查“注入”的，而是把格式化、静态分析、测试和 CI 变成随每次修改重复运行的反馈系统。
```

## 格式化与 lint

formatter 处理表层语法一致性，例如引号、空格、导入顺序和行宽，让团队停止在无关风格上争论。项目应提交工具配置和 `.editorconfig`；IDE 保存时可自动格式化，CI 则使用 check 模式验证，不直接修改贡献者代码。

linter 在不运行程序的情况下寻找反模式与潜在错误。规则应有可查的原因和修复建议；误报可局部抑制，但抑制应说明理由。部分问题能自动修复，仍需检查 diff。Semgrep 直接匹配抽象语法树，比字符级 grep 更能识别跨换行、参数重排等代码结构，例如查找 Python 中的 `subprocess.Popen(..., shell=True, ...)`。

## 测试与覆盖率

单元测试验证小函数，集成测试验证模块/服务协作，功能测试覆盖端到端行为。TDD 先写失败测试再实现；回归测试把已修 bug 固化；property-based testing 生成大量输入验证不变量。外部数据库/API 可 mock，但过度 mock 会测试自己的假实现而非真实集成。

覆盖率告诉你哪些行/分支执行过，不证明结果正确。它适合发现完全没有触达的路径，而不应成为逼迫团队写低价值测试的唯一目标。优先覆盖风险、边界条件和失败行为。

## 本地钩子、CI 与部署

pre-commit hook 在提交前快速运行格式化、lint 等，缩短反馈；但本地钩子能被跳过，最终规则必须由 CI 强制执行。CI 在 push、PR 或定时触发，可运行格式、lint、类型检查、测试和多 OS/语言版本矩阵。定时构建还能发现外部依赖变化。

持续部署在 CI 通过后构建并发布 artifact 或站点。部署需要环境保护、最小权限、可追踪版本、健康检查和回滚，不能把“测试通过”误认为“上线一定安全”。

`just`、Make、npm scripts 等 command runner 把长命令统一为 `just lint`、`just test`，让开发者和 CI 调用同一入口，避免两套流程漂移。

## 正则表达式

regex 描述字符串集合，常用于搜索、替换、筛选测试和简单验证。基础构件包括：`.` 任意字符，`[]` 字符类，`|` 选择，`?/*/+/{N}` 数量，`^/$` 行边界，`()` 捕获组，反斜杠转义。`\d{4}-\d{2}-\d{2}` 只验证日期形状，并不会拒绝 99 月。

量词默认贪婪，`.*?` 等形式尽量少取。捕获组可在代码中提取，也可在编辑器替换中用 `$1` 或 `\1` 引用。不同引擎语法不同，应针对实际工具测试。

regex 很有用但不是通用 parser。HTML、嵌套语言和完整 JSON 应交给对应解析器；即使现代引擎提供回溯引用等扩展，也会面临可维护性和性能风险。学会基础后按需查文档，比背完所有语法更有效。

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
