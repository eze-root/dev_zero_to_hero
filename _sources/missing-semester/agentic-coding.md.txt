# 第七讲：智能体编程

> 官方 notes：[https://missing.csail.mit.edu/2026/agentic-coding/](https://missing.csail.mit.edu/2026/agentic-coding/)  
> 视频：[YouTube](https://www.youtube.com/watch?v=sTdz6PZoAnw)

```{note}
本文依照 Missing Semester 2026 官方 notes 的原文结构完整翻译；保留标题层级、命令示例、工具链接、引用与提示。练习采用 MyST exercise，并在官方题目之外补充折叠参考答案。
```


编码智能体是对话式人工智能模型，可以访问读/写文件、网络搜索和调用 shell 命令等工具。它们要么存在于 IDE 中，要么存在于独立的命令行或 GUI 工具中。编码智能体是高度自主且功能强大的工具，可实现多种用例。

本讲座以 [开发环境和工具](development-environment.md) 讲座中的人工智能驱动的开发材料为基础。作为一个快速演示，我们继续使用 {ref}`人工智能驱动的开发 <development-environment-ai-powered-development>` 部分中的示例：

```python
from urllib.request import urlopen

def download_contents(url: str) -> str:
    with urlopen(url) as response:
        return response.read().decode('utf-8')

def extract(content: str) -> list[str]:
    import re
    pattern = r'\[.*?\]\((.*?)\)'
    return re.findall(pattern, content)

print(extract(download_contents("https://raw.githubusercontent.com/missing-semester/missing-semester/refs/heads/master/_2026/development-environment.md")))
```

我们可以尝试提示编码智能体执行以下任务：

```
Turn this into a proper command-line program, with argparse for argument parsing. Add type annotations, and make sure the program passes type checking.
```

智能体将读取文件以理解它，然后进行一些编辑，最后调用类型检查器以确保类型注释正确。如果它犯了一个错误，导致类型检查失败，它可能会迭代，尽管这是一个简单的任务，因此不太可能发生。由于编码智能体可以访问可能有害的工具，因此默认情况下，智能体工具会提示用户确认工具调用。

> 如果编码智能体犯了错误 --- 例如，如果您在 `$PATH` 上直接提供了 `mypy` 二进制文件，但智能体尝试调用 `python -m mypy` --- 您可以向其提供文本反馈以帮助其纠正。

编码智能体支持多轮交互，因此您可以通过与智能体的来回对话来迭代工作。如果智能体走错了路，您甚至可以打断它。一个有用的思维模型可能是把自己看作管理实习生的负责人：实习生会做具体的工作，但需要指导，并且偶尔会做错事并需要纠正。

> 要获得更具说明性的演示，请尝试要求智能体作为后续操作来运行生成的脚本。观察输出，并尝试要求它进行更改（例如，要求它仅包含绝对 URL）。

(agentic-coding-how-ai-models-and-agents-work)=
# AI 模型与智能体如何工作

全面解释现代 [大语言模型 (LLM)](https://en.wikipedia.org/wiki/Large_language_model) 的内部工作原理和智能体框架等基础设施超出了本课程的范围。然而，对一些关键思想有一个高层次的理解有助于有效地使用这种前沿技术并理解其局限性。

LLM 可以被视为对给定提示字符串（输入）的完成字符串（输出）的概率分布进行建模。 LLM 推理（例如，当您向对话式聊天应用程序提供查询时会发生什么）从该概率分布中进行_采样_。 LLM 有一个固定的_上下文窗口_，即输入和输出字符串的最大长度。


对话式聊天和编码智能体等人工智能工具建立在这个原语之上。对于多回合交互，聊天应用程序和智能体使用回合标记，并在每次出现新用户提示时提供整个对话历史记录作为提示字符串，每个用户提示调用一次 LLM 推理。对于工具调用智能体，智能体框架将某些 LLM 输出解释为调用工具的请求，并且智能体框架将工具调用的结果作为提示字符串的一部分提供给模型（因此每次有工具调用/响应时，LLM 推理都会再次运行）。工具调用智能体的核心概念可以是[用 200 行代码实现](https://www.mihaileric.com/The-Emperor-Has-No-Clothes/)。

(agentic-coding-privacy)=
## 隐私

大多数标准配置的人工智能编码工具都会将大量数据发送到云端。有时，智能体框架在本地运行，而 LLM 推理在云中运行，有时更多的软件在云中运行（例如，服务提供商可能会有效地获得整个仓库的副本以及您与 AI 工具的所有交互）。

有一些开源 AI 编码工具和开源 LLM 相当不错（尽管不如专有模型），但目前对于大多数用户来说，由于硬件限制，在本地运行前沿的开放 LLM 是不可行的。

(agentic-coding-use-cases)=
# 使用场景

编码智能体可以帮助完成各种任务。一些例子：

- **实现新功能。** 如上例所示，您可以要求编码智能体实现某个功能。在这一点上，给出一个好的规范更多的是一门艺术，而不是一门科学。您希望智能体的输入具有足够的描述性，以便智能体执行您希望它执行的操作（至少朝着正确的方向前进，以便您可以迭代），但不要过度描述，以免您自己做太多工作。测试驱动开发可能特别有效：编写测试（或使用编码智能体帮助您编写测试），审核它们以确保它们捕获您想要的内容，然后要求编码智能体实现该功能。模型在不断改进，因此您必须保持对模型功能的最新直觉。
    > 我们使用 Claude Code 来 [实现](https://github.com/missing-semester/missing-semester/pull/345) 这些 Tufte 风格的旁注。
- **修复错误。** 如果您的编译器、linter、类型检查器或测试出现错误，您可以要求智能体更正它们，例如使用“使用 mypy 修复问题”之类的提示。当您可以将模型纳入反馈循环时，编码模型特别有效，因此请尝试进行设置，以便模型可以直接运行失败检查，这将使其能够自主迭代。如果这不切实际，您可以手动向模型提供反馈。
    > 在提交缺失学期仓库的 [f552b55](https://github.com/missing-semester/missing-semester/commit/f552b5523462b22b8893a8404d2110c4e59613dd) 时，我们提示 Claude Code“检查智能体编程讲座中的拼写错误和语法问题”，并随后要求其修复发现的问题，这些问题是在 [f1e1c41](https://github.com/missing-semester/missing-semester/commit/f1e1c417adba6b4149f7eef91ff5624de40dc637) 中提交的。
- **重构。** 您可以使用编码智能体以各种方式重构代码，从简单的任务（例如重命名方法）（{ref}`代码智能 <development-environment-code-intelligence-and-language-servers>` 也支持这种重构）到更复杂的任务（例如将功能分解为单独的模块）。
    > 我们使用 Claude Code 将 [拆分](https://github.com/missing-semester/missing-semester/pull/344) 智能体编程转化为自己的讲座。
- **代码审查。** 您可以要求编码智能体审查代码。您可以为他们提供基本指导，例如“查看我尚未提交的最新更改”。如果您想查看拉取请求并且您的编码智能体支持网络获取，或者您安装了 [GitHub CLI](https://cli.github.com/) 等命令行工具，您甚至可以要求编码智能体“查看拉取请求 {link}”，它会从那里处理它。
- **代码理解。** 您可以向编码智能体询问有关代码库的问题，这对于入门特别有帮助。
- **作为 shell。** 您可以要求编码智能体使用特定工具来解决任务，因此您可以使用自然语言调用 shell 命令，例如“使用 find 命令查找所有超过 30 天的文件”或“使用 mogrify 将所有 jpg 大小调整为原始大小的 50%”。
- **Vibe 编码。** 智能体足够强大，您无需自己编写一行代码即可实现某些应用程序。
    > [这是一个例子](https://github.com/cleanlab/office-presence-dashboard) 是一位讲师vibe coding的真实世界项目。

(agentic-coding-advanced-agents)=
# 高级智能体

在这里，我们简要概述了编码智能体的一些更高级的使用模式和功能。

- **可重复使用的提示。** 创建可重复使用的提示或模板。例如，您可以编写详细的提示以特定方式进行代码审查，并将其保存为可重用的提示。
    > 智能体工具发展迅速。在某些工具中，可复用提示已不再作为独立功能。例如，Codex 将[自定义提示](https://developers.openai.com/codex/custom-prompts)纳入技能体系，Claude Code 也使用[技能](https://code.claude.com/docs/en/skills)来组织这类能力。
- **并行智能体。** 编码智能体可能会很慢：您可以向智能体发出提示，它可能会在问题上工作数十分钟。您可以同时运行多个智能体实例，要么处理同一任务（LLM 是随机的，因此多次运行同一件事并采取最佳解决方案会很有帮助），也可以处理不同的任务（例如，同时实现两个不重叠的功能）。为了防止不同智能体的更改相互干扰，您可以使用 [git worktree](https://git-scm.com/docs/git-worktree)，我们在 [版本控制](version-control.md) 的讲座中对此进行了介绍。
- **MCP。** MCP 代表_模型上下文协议_，是一种开放协议，可用于将编码智能体与工具连接起来。例如，这个 [Notion MCP 服务器](https://github.com/makenotion/notion-mcp-server) 可以让您的智能体读取/写入 Notion 文档，从而启用诸如“读取 {Notion doc} 中链接的规范，起草实施计划作为 Notion 中的新页面，然后实施原型”之类的用例。要发现 MCP，您可以使用 [Pulse](https://www.pulsemcp.com/servers) 和 [Glama](https://glama.ai/mcp/servers) 等目录。
- **上下文管理。** 正如我们在 {ref}`上面 <agentic-coding-how-ai-models-and-agents-work>` 中指出的，编码智能体底层的 LLM 具有有限的_上下文窗口_。编码智能体的有效使用需要充分利用上下文。您希望确保智能体能够访问其所需的信息，但要避免不必要的上下文，以避免溢出上下文窗口或降低模型的性能（这种情况往往会随着上下文大小的增长而发生，即使它不会溢出上下文窗口）。智能体框架会自动提供并在某种程度上管理上下文，但很多控制权留给了用户。
    - **清除上下文窗口。** 最基本的控制，编码智能体支持清除上下文窗口（开始新的对话），您应该为不相关的查询执行此操作。
    - **倒回对话。** 某些编码智能体支持撤消对话历史记录中的步骤。在“撤消”更有意义的情况下，这不是给出引导智能体朝不同方向前进的后续消息，而是更有效地管理上下文。
    - **压缩。** 为了实现无限长度的对话，编码智能体支持上下文_压缩_：如果对话历史记录变得太长，它们将自动调用 LLM来总结对话的前缀，并用摘要替换对话历史记录。一些智能体允许用户在需要时调用压缩。
    - **llms.txt.** `/llms.txt` 文件是建议的 [标准](https://llmstxt.org/) 位置，用于供 LLM 在推理时使用的文档。产品（例如 [cursor.com/llms.txt](https://cursor.com/llms.txt)）、软件库（例如 [ai.pydantic.dev/llms.txt](https://ai.pydantic.dev/llms.txt)）和 API（例如 [apify.com/llms.txt](https://apify.com/llms.txt)）可能具有便于开发的 `llms.txt` 文件。此类文档的每个标记的信息密度更高，因此它们比要求编码智能体获取和读取 HTML 页面更具上下文效率。当编码智能体没有关于您尝试使用的依赖项的内置知识时（例如，因为它是在 LLM 知识截止后发布的），外部文档会很方便。
    - **AGENTS.md.** 大多数编码智能体支持 [AGENTS.md](https://agents.md/) 或类似的（例如，Claude Code 查找 `CLAUDE.md`）作为编码智能体的说明文件。当智能体启动时，它会使用 `AGENTS.md` 的全部内容预先填充上下文。您可以使用它向智能体提供跨会话常见的建议（例如，指示它在进行代码更改后始终运行类型检查器，解释如何运行单元测试，或提供智能体可以浏览的第三方文档的链接）。某些编码智能体可以自动生成此文件（例如，Claude Code 中的 `/init` 命令）。有关 `AGENTS.md` 的真实示例，请参阅 [这里](https://github.com/pydantic/pydantic-ai/blob/main/CLAUDE.md)。
    - **技能。** `AGENTS.md` 中的内容始终会完整加载到智能体的上下文窗口中。 _技能_添加一级间接以避免上下文膨胀：您可以向智能体提供技能列表以及描述，并且智能体可以根据需要“打开”技能（将其加载到其上下文窗口中）。
    - **子智能体。** 某些编码智能体允许您定义子智能体，它们是特定于任务的工作流程的智能体。顶级编码智能体可以调用子智能体来完成特定任务，这使得顶层智能体和子智能体能够更有效地管理上下文。顶层智能体的上下文不会因为子智能体看到的所有内容而变得臃肿，并且子智能体可以仅获取其任务所需的上下文。举一个例子，一些编码智能体将网络研究实现为子智能体：顶层智能体将向子智能体提出查询，子智能体将运行网络搜索、检索各个网页、分析它们，并向顶层智能体提供查询的答案。这样，顶层智能体的上下文就不会因为所有检索到的网页的完整内容而变得臃肿，并且子智能体的上下文中也不会包含顶层智能体的其余对话历史记录。

对于许多需要编写提示的高级功能（例如技能或子智能体），您可以使用 LLM 来帮助您入门。一些编码智能体甚至内置了对此的支持。例如，Claude Code 可以通过简短的提示生成子智能体（调用 `/agents` 并创建新智能体）。尝试使用以下提示创建子智能体：

```
A Python code checking agent that uses `mypy` and `ruff` to type-check, lint, and format *check* any files that have been modified from the last git commit.
```

然后，您可以使用顶层智能体通过诸如“使用代码检查器子智能体”之类的消息显式调用子智能体。您还可以让顶层智能体在适当的时候自动调用子智能体，例如，在修改任何 Python 文件后。

(agentic-coding-what-to-watch-out-for)=
# 需要注意什么

人工智能工具可能会犯错误。它们建立在 LLM 的基础上，而 LLM 只是概率式的下一 token 预测模型。它们并不像人类那样“聪明”。检查 AI 输出的正确性和安全漏洞。有时验证代码可能比自己编写代码更困难；对于关键代码，请考虑手动编写。智能体可能钻进无效的兔子洞，甚至坚持错误结论；要警惕调试螺旋。不要把人工智能当作拐杖，警惕过度依赖或理解浅薄。人工智能仍然无法完成大量的编程任务。计算思维仍然有价值。

(agentic-coding-recommended-software)=
# 推荐软件

许多 IDE / AI 编码扩展都包含编码智能体（请参阅 [开发环境讲座](development-environment.md) 的建议）。其他流行的编码智能体包括 Anthropic 的 [Claude Code](https://www.claude.com/product/claude-code)、OpenAI 的 [Codex](https://openai.com/codex/) 以及 [opencode](https://github.com/anomalyco/opencode) 等开源智能体。

## Exercises

```{exercise} 比较四种编程方式
:label: exercise-agent-four-modes

对同一个小任务分别手写、使用 AI 补全、行内对话和编码智能体，比较体验与结果。
```

```{solution} exercise-agent-four-modes
:class: dropdown

固定相同需求与测试，记录完成时间、人工输入、修改轮次、测试通过率、代码复杂度、安全问题和自己对实现的理解。不要只比较“第一次产出速度”；把审查与返工计入成本。结果应说明哪种方式适合什么规模和风险等级。
```

```{exercise} 探索陌生代码库
:label: exercise-agent-unfamiliar-repo

让智能体在你关心的陌生仓库中定位一个 bug 或功能；也可调查 opencode 的安全相关机制。
```

```{solution} exercise-agent-unfamiliar-repo
:class: dropdown

先要求只读调查：入口、关键模块、数据流、测试和安全边界，并为每个结论给出文件路径/符号。然后手工抽查并运行相关测试。一个合格答案应区分源码事实与推断，指出仍未确认的问题，而不是只给架构概述。
```

```{exercise} 完全 vibe code 一个小应用
:label: exercise-agent-vibe-app

从空目录开始，不手写一行代码，由智能体完成一个小应用。
```

```{solution} exercise-agent-vibe-app
:class: dropdown

仍要由你定义范围、用户故事和验收测试。要求智能体初始化版本库、分小提交、运行检查、写 README；最后在干净环境按 README 重建并进行安全/依赖审查。若你无法解释关键数据流或回滚失败修改，说明原型尚不适合真实用户。
```

```{exercise} 对比 AGENTS.md、skill 与 subagent
:label: exercise-agent-instructions

在支持的智能体中创建并测试项目说明文件、一个 skill 和一个 subagent，比较使用时机。
```

```{solution} exercise-agent-instructions
:class: dropdown

`AGENTS.md` 放每次都必须知道的短规则；skill 放描述明确、按需读取的专业流程和资料；subagent 放可独立交付、需要隔离上下文或工具探索的任务。设计同一小改动做 A/B 测试，检查触发是否正确、上下文是否减少、结果能否复现。工具不支持的能力可跳过，不应伪装实现。
```

```{exercise} 强制智能体使用命令行变换
:label: exercise-agent-regex-tool

完成代码质量讲中的 Markdown 列表标记替换。先观察智能体是否逐文件直接编辑，再提示它使用第一讲的命令行工具完成可复用变换。
```

```{solution} exercise-agent-regex-tool
:class: dropdown

直接编辑能完成单个文件，却难以审计、复用和扩展到大量文件。可提示：“不要直接调用文件编辑工具；先用 `rg` 定位仅位于行首、允许缩进的 `- ` 列表项，再用 `sed`/`perl` 生成变换，先输出 diff，确认后应用。”最终用 `git diff --check` 和 Markdown 构建验证，确保没有替换分隔符或正文连字符。
```

```{exercise} 在隔离环境测试自主模式
:label: exercise-agent-sandbox

把智能体放进 VM 或容器后测试跳过逐次权限确认的自主模式。
```

```{solution} exercise-agent-sandbox
:class: dropdown

安全基线：一次性 VM/容器、非特权用户、只挂载测试副本、无宿主 Docker socket、无 SSH/云凭据、默认断网或域名白名单、限制 CPU/内存/时间，执行后销毁环境并只导出审查过的 patch。容器共享宿主内核，处理真正不可信代码时 VM 边界更强。“隔离”不是运行危险模式的免责理由。
```

## 许可与署名

本页依据 MIT Missing Semester 2026 第七讲[官方 notes](https://missing.csail.mit.edu/2026/agentic-coding/)整理，原材料采用 [CC BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可。
