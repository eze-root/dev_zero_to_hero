# 为 GPT-6 Astra 重新思考 Skills 与 Prompts

> 原文：[Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)  
> 发布日期：2026-09-11  
> 分类：Codex  
> 作者：Eric Provencher

```{note}
本文按 OpenAI Developer Blog 原文的结构和内容翻译。翻译尽可能忠于原文，不省略原文中的正文、示例、Bad / Good 对照和引用；除本说明外，不额外补充原文没有的观点。
```

**重新审视 skill 描述、`AGENTS.md` 和任务 prompt，避免上下文过度膨胀。**

编码智能体已经走过了很长一段路，最佳实践也在快速变化。随着模型能力增强，过去需要大量手把手指导和脚手架才能完成的事情，如今已经不再需要那么多这些东西。

如果过去一年里你一直在项目中使用 Codex 这样的智能体，那么在努力引导模型取得良好结果的过程中，你很可能已经积累了大量指令。每次模型发布新版本时，都值得重新审视这些假设；而到了 GPT-6 Astra，这比以往任何时候都更加重要。

这些指令可以有很多种形式：skills、`AGENTS.md`，以及你的任务 prompt，都会影响模型如何完成工作。

## 更好的 Skills

这些指令可以采用 skills 的形式。skills 本质上是存储为 Markdown 文件的 prompt，也可以与资源文件和打包好的脚本放在一起。一般来说，它们最适合用于指导某个特定工作流，或者指导模型使用某些应用。

现在，人们往往会默认在项目中打包很多 skills；每个 skill 都有一个名称和描述，这些内容会被加载到模型的上下文中，让模型知道什么时候应该使用它们。但是，很多描述都写得太长；而当你加入太多 skills 时，Codex 会开始缩短这些描述以便把它们放进上下文。最终，模型看到的每个描述都更少，也就更难判断应该选择哪个 skill。

更糟糕的是，这些描述经常会互相矛盾，或者过度强调某个 skill 应该在什么情况下使用，从而导致模型加载一些实际上并不能帮助当前任务的指令。

创建 skills 的一个常见工作流是使用 `$skill-creator` skill。我们最近更新了它的指导，以帮助缓解很多在实践中观察到的失败模式。

首先，skill 描述应该尽可能简短，同时明确告诉模型什么时候应该使用它：

### 明确说明它适用于什么情况

::::{grid} 1 1 2 2
:gutter: 2

:::{grid-item-card} Bad
:class-card: agents-example-card agents-example-bad

**原文**

`Create and validate Postgres schema migrations. Use when working with databases, queries, models, or persistence.`

**译文**

创建并验证 Postgres schema migration。用于涉及数据库、查询、模型或持久化的工作。
:::

:::{grid-item-card} Good
:class-card: agents-example-card agents-example-good

**原文**

`Create and validate Postgres schema migrations. Use when adding or changing a migration, or reviewing its rollout.`

**译文**

创建并验证 Postgres schema migration。用于新增或修改 migration，或者审查它的 rollout 时。
:::
::::

这里，较差的 skill 描述会促使模型在碰到任何与数据库有关的内容时都使用这个 skill，而不是只在真正需要处理 migration 时才使用它。

其次，一个有用的 skill 的关键标志之一是 **progressive disclosure（渐进式披露）**。读取 skill 会占用上下文，让你更接近 compaction，同时也可能引入并不适用于当前任务的指导。对于包含多个工作流的 skill，应当让根文档成为一个最小化的 router，指向支持文档和脚本。只给模型足够的指导，让它知道应该去哪里查找，而不要强迫它阅读当前根本不需要的内容。

第三，很多 skills 被写成了非常复杂的 itinerary 或 recipe。模型现在已经更擅长理解细微差别和模糊性，因此，过去可能有帮助的过度具体指导，如今反而可能妨碍结果。

仓库中的 skills 也会指导其他贡献者的智能体，而他们可能使用不同的模型。对 Sol 或 Luna 有帮助的指导，可能会对 GPT-6 Astra 形成过度约束，因此要考虑你留下的这些指令最终会被哪些模型使用。

## 保持 `AGENTS.md` 最新

因为 `AGENTS.md` 会在模型每次进入你的仓库工作时生效，所以应该经常重新审视其中的每一条指令，并问自己：它现在是否仍然有必要。

要求模型在每次编辑之前都先阅读一整套文档或完整的仓库地图，对于修复一个拼写错误来说显然太过头了。GPT-6 Astra 能够自己判断需要阅读什么，不需要在每次修改之前都被强制要求审查整个项目。

### 阅读任务真正需要的内容

::::{grid} 1 1 2 2
:gutter: 2

:::{grid-item-card} Bad
:class-card: agents-example-card agents-example-bad

每次编辑之前，都先阅读 `architecture.md`、`database.md` 和 `deployment.md`。
:::

:::{grid-item-card} Good
:class-card: agents-example-card agents-example-good

处理服务边界时使用 `architecture.md`，处理 schema 变更时使用 `database.md`，准备部署时使用 `deployment.md`。
:::
::::

在每次编辑之前都提示模型去读文件，是一种非常有效的“烧掉上下文并拖慢工作速度”的方式。不过，指向某些文档仍然可能有帮助，只要这种指引是与上下文相关的。同时也要确保这些文档本身保持更新。

过去的模型需要被鼓励去运行测试并检查自己的工作。GPT-6 Astra 会自己做这些事情，因此同样的指令现在可能导致不必要的测试。

GPT-6 Astra 很彻底，但对于一个任务究竟应该推进到什么程度，它可能会更加谨慎。有时需要稍微推动它一下，让它继续完成工作。你可以使用 `AGENTS.md`，针对某个你确定安全的具体工作流明确给予它权限，例如本地测试套件：

> 本地测试使用一次性 fixture，并且无法访问生产环境。直接运行测试；修复由请求中的改动导致的失败，并重新运行受影响的测试，不需要在每一步都请求批准。

## 决策边界

要特别注意你如何描述边界。如果以前的模型曾经在未经许可的情况下替你执行操作，你可能已经加入了很强的措辞，要求它必须先询问。这可能有用；但 GPT-6 Astra 是我们对齐程度最高的模型，它有更好的判断力，在不知道某项操作是否安全时不会执行，因此你也应该按照这种能力水平来对待它。

如果你之前设置某些边界，是为了防止其他模型走得太远，而现在准备切换到 GPT-6 Astra，那么可以考虑更新这些措辞：Astra 可能会把它们理解得过于严格，并在你其实愿意让它继续工作的地方停下来。

## 持续性

如果你已经习惯 GPT-5.6 Sol 接到一个请求后持续工作很长时间，那么 GPT-6 Astra 对于什么时候应该停止可能会显得更加谨慎。它可能完成第一版实现之后就回来让你 review，即使其实还有工作没有完成。

这时，在开始之前定义什么叫“完成”会很有帮助。你可能需要明确推动 Astra 一直继续到任务彻底完成。如果任务包括让实现真正运行起来、检查结果，并修复失败的部分，就把这些要求写进请求里。要求它在第一版实现完成后停下来等待 review，会把模型拉向一个更早的停止点，因此要确认这是否真的是一个需要你做决定的节点。

如果你希望它在第一遍之外继续探索，就说明你希望它探索什么，以及它应该在哪里停止。

新模型发布是一次清理旧东西的好机会，但你不需要手工审查所有内容：可以让 GPT-6 Astra 根据本文讨论的内容做一次 audit，然后去构建一些你以前不会尝试去做的东西！
