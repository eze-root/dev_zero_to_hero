# 第七讲：智能体编程

> 官方 notes：[Agentic Coding](https://missing.csail.mit.edu/2026/agentic-coding/)  
> 视频：[YouTube](https://www.youtube.com/watch?v=sTdz6PZoAnw)

```{note}
编码智能体是在语言模型外增加文件、终端、搜索等工具的系统。它能自主完成多步工作，也因此拥有造成真实损害的能力；授权范围、验证方式和隐私边界必须先于便利性。
```

## 模型、上下文与工具循环

语言模型根据输入上下文对后续 token 的概率分布采样，输出并不是事实数据库的确定查询。上下文窗口有限；多轮对话通常会把历史再次送入模型。智能体框架把某些模型输出解释为工具调用，执行后把结果加入上下文，模型据此继续推理，直到交付结果或停止。

因此，智能体的能力不仅取决于模型，还取决于工具、权限、上下文和反馈回路。给它可直接运行的测试、类型检查或 linter，通常比只说“看起来修好”可靠得多。模型走偏时应立即中断、缩小任务或补充证据，就像管理一位速度很快但需要指导的实习生。

大多数云端工具会发送代码、提示和工具输出。使用前检查数据保留、训练选项、组织政策与第三方 MCP 权限；私有代码、个人信息和秘密不应因“只是让 AI 看一下”而越过授权边界。本地开源模型能改善部分隐私问题，但仍要考虑硬件、模型质量和插件行为。

## 适合的工作类型

- 实现有清晰验收条件的小功能，尤其是测试先行；
- 读取编译器、类型检查、lint 和测试失败，反复修改直到通过；
- 机械或跨文件重构；
- 代码审查与风险清单，但不能替代负责人审查；
- 探索陌生仓库，回答“如何运行”“某功能在哪里”；
- 把自然语言转成明确的 Shell 工具操作；
- 从零快速原型，即 vibe coding。

提示应给出目标、范围、约束、禁止事项和完成定义。例如“修复 mypy”不如“只修改 `src/`，不降低类型检查级别；运行 `uv run mypy src` 和测试，说明根因与残余风险”。让智能体先检查仓库再改，要求保留用户已有改动，并审查 diff。

## 高级用法与上下文管理

可复用 prompt 把重复流程标准化。`AGENTS.md`/`CLAUDE.md` 等文件适合始终加载的项目事实：构建命令、目录边界和必须运行的检查。skill 按需加载更长的专门流程，避免每次占用上下文；subagent 用独立上下文完成边界明确的子任务，再返回摘要。

多个智能体可以在不同 Git worktree 中处理互不重叠的任务，或对同一问题独立尝试后择优。并行会增加审查和合并成本，不能把共享文件交给多个写入者而不协调。

MCP（Model Context Protocol）把外部工具接入智能体。连接 Notion、GitHub 或数据库会扩展能力，也扩展攻击面：只安装可信服务，授予最小权限，并防范外部内容中的提示注入。

上下文过长会稀释关键信息。无关任务应开新会话；走错方向时优先回退而非继续堆叠纠正；长任务通过 compaction 保存目标、已完成工作、验证结果和下一步。`llms.txt` 可提供密度更高、面向模型的文档入口，但仍需核对来源和时效。

## 风险与责任

AI 会产生错误和安全漏洞，也可能在调试循环中不断为错误假设辩护。验证代码有时比亲自编写更难，关键路径应由能承担责任的人理解和审查。不要为了自动化而关闭确认、扩大权限或把生产秘密放进上下文；生成速度不能转移最终责任。

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
