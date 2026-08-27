# 第五讲：版本控制与 Git

> 官方 notes：[https://missing.csail.mit.edu/2026/version-control/](https://missing.csail.mit.edu/2026/version-control/)  
> 视频：[YouTube](https://www.youtube.com/watch?v=9K8lB61dl3Y)

```{note}
本文依照 Missing Semester 2026 官方 notes 的原文结构完整翻译；保留标题层级、命令示例、工具链接、引用与提示。练习采用 MyST exercise，并在官方题目之外补充折叠参考答案。
```


版本控制系统 (VCS) 是用于跟踪源代码（或其他文件和文件夹集合）更改的工具。顾名思义，这些工具有助于维护变更历史记录；此外，它们还促进协作。从逻辑上讲，VCS 在一系列_快照_中跟踪文件夹及其内容的更改，其中每个快照都封装了顶级目录中文件/文件夹的整个状态。 VCS 还维护元数据，例如每个快照的创建者、与每个快照关联的消息等等。

为什么版本控制有用？即使您独自工作，它也可以让您查看项目的旧快照、记录进行某些更改的原因、处理并行开发分支等等。当与他人合作时，它是一个非常宝贵的工具，可以查看其他人所做的更改，以及解决并发开发中的冲突。

现代 VCS 还可以让您轻松（通常是自动）回答以下问题：

- 谁写了这个模块？
- 该特定文件的该特定行何时被编辑？由谁来？为什么
被编辑了吗？
- 在过去 1000 次修订中，特定单元测试何时/为何停止
工作？

虽然存在其他 VCS，但 **Git** 是版本控制的事实标准。这个 [XKCD漫画](https://xkcd.com/1597/) 赢得了 Git 的声誉：

![xkcd 1597](https://imgs.xkcd.com/comics/git.png)

因为 Git 的界面是一个有漏洞的抽象，所以自上而下地学习 Git（从它的界面/命令行界面开始）可能会导致很多混乱。可以记住一些命令并将它们视为魔法咒语，并在出现问题时按照上面漫画中的方法进行操作。

虽然 Git 的界面确实很丑，但它的底层设计和想法却很漂亮。虽然丑陋的界面必须_记住_，但漂亮的设计却可以_理解_。因此，我们对 Git 进行了自下而上的解释，从它的数据模型开始，然后介绍命令行界面。一旦理解了数据模型，就可以更好地理解命令如何操作底层数据模型。

(version-control-gits-data-model)=
## Git 的数据模型

Git 的独创性在于其经过深思熟虑的数据模型，它支持版本控制的所有出色功能，例如维护历史记录、支持分支和实现协作。

(version-control-snapshots)=
### 快照

Git 将某些顶级目录中的文件和文件夹集合的历史记录建模为一系列快照。在 Git 术语中，文件称为“blob”，它只是一堆字节。目录称为“树”，它将名称映射到 blob 或树（因此目录可以包含其他目录）。快照是正在跟踪的顶级树。例如，我们可能有一棵树，如下所示：

```
<root> (tree)
|
+- foo (tree)
|  |
|  + bar.txt (blob, contents = "hello world")
|
+- baz.txt (blob, contents = "git is wonderful")
```

顶级树包含两个元素，一棵树“foo”（它本身包含一个元素，一个 blob“bar.txt”）和一个 blob“baz.txt”。

(version-control-modeling-history-relating-snapshots)=
### 建模历史：相关快照

版本控制系统应如何关联快照？一个简单的模型是具有线性历史。历史记录是按时间顺序排列的快照列表。由于多种原因，Git 不使用这样的简单模型。

在 Git 中，历史记录是快照的有向无环图 (DAG)。这听起来像是一个花哨的数学词，但不要被吓倒。所有这一切意味着 Git 中的每个快照都引用一组“父级”，即它之前的快照。它是一组父项而不是单个父项（如线性历史中的情况），因为快照可能源自多个父项，例如，由于组合（合并）两个并行的发展分支。

Git 将这些快照称为“提交”。可视化提交历史可能看起来像这样：

```
o <-- o <-- o <-- o
            ^
             \
              --- o <-- o
```

在上面的 ASCII 艺术中，`o` 对应于单独的提交（快照）。箭头指向每个提交的父级（这是“先于”关系，而不是“后于”关系）。第三次提交后，历史记录分支成两个单独的分支。例如，这可能对应于并行开发的两个独立的功能，彼此独立。将来，这些分支可能会被合并以创建一个包含这两个功能的新快照，生成如下所示的新历史记录，新创建的合并提交以粗体显示：

<pre class="highlight">
<code>
o <-- o <-- o <-- o <---- <strong>o</strong>
            ^            /
             \          v
              --- o <-- o
</code>
</pre>

Git 中的提交是不可变的。然而，这并不意味着错误无法纠正；只是对提交历史记录的“编辑”实际上创建了全新的提交，并且引用（见下文）被更新以指向新的提交。

(version-control-data-model-as-pseudocode)=
### 数据模型，作为伪代码

看看用伪代码写下的 Git 数据模型可能会很有启发：

```
// a file is a bunch of bytes
type blob = array<byte>

// a directory contains named files and directories
type tree = map<string, tree | blob>

// a commit has parents, metadata, and the top-level tree
type commit = struct {
    parents: array<commit>
    author: string
    message: string
    snapshot: tree
}
```

这是一个干净、简单的历史模型。

(version-control-objects-and-content-addressing)=
### 对象和内容寻址

“对象”是一个 blob、树或提交：

```
type object = blob | tree | commit
```

在 Git 的数据存储中，所有对象均通过其 [SHA-1 哈希](https://en.wikipedia.org/wiki/SHA-1) 进行内容寻址。

```
objects = map<string, object>

def store(object):
    id = sha1(object)
    objects[id] = object

def load(id):
    return objects[id]
```

Blob、树和提交以这种方式统一：它们都是对象。当它们引用其他对象时，它们实际上并不_包含_它们在磁盘上的表示形式，而是通过它们的散列来引用它们。

例如，示例目录结构 {ref}`上面 <version-control-snapshots>` 的树（使用 `git cat-file -p 698281bc680d1995c5f4caaf3359721a5a58d48d` 进行可视化）如下所示：

```
100644 blob 4448adbf7ecd394f42ae135bbeed9676e894af85    baz.txt
040000 tree c68d233a33c5c06e0340e4c224f0afca87c8ce87    foo
```

树本身包含指向其内容的指针：`baz.txt`（一个 blob）和 `foo`（一棵树）。如果我们用 `git cat-file -p 4448adbf7ecd394f42ae135bbeed9676e894af85` 查看 baz.txt 对应的哈希所寻址的内容，我们会得到以下结果：

```
git is wonderful
```

(version-control-references)=
### 引用

现在，所有快照都可以通过其 SHA-1 哈希值来识别。这很不方便，因为人类不擅长记住 40 个十六进制字符的字符串。

Git 解决这个问题的方法是为 SHA-1 哈希值提供人类可读的名称，称为“引用”。引用是指向提交的指针。与不可变的对象不同，引用是可变的（可以更新以指向新的提交）。例如，`master` 引用通常指向开发主分支中的最新提交。

```
references = map<string, string>

def update_reference(name, id):
    references[name] = id

def read_reference(name):
    return references[name]

def load_reference(name_or_id):
    if name_or_id in references:
        return load(references[name_or_id])
    else:
        return load(name_or_id)
```

这样，Git 就可以使用人类可读的名称（例如“master”）来引用历史记录中的特定快照，而不是使用长的十六进制字符串。

一个细节是，我们经常需要历史记录中“我们当前所在位置”的概念，以便当我们拍摄新快照时，我们知道它相对于什么（我们如何设置提交的 `parents` 字段）。在 Git 中，“我们当前所在的位置”是一个称为“HEAD”的特殊引用。

(version-control-repositories)=
### 仓库

最后，我们可以（粗略地）定义什么是 Git 仓库：它是数据 `objects` 和 `references`。

在磁盘上，所有 Git 存储都是对象和引用：这就是 Git 数据模型的全部内容。所有 `git` 命令通过添加对象和添加/更新引用来映射到提交 DAG 的某些操作。

每当您输入任何命令时，请考虑该命令对底层图形数据结构进行的操作。相反，如果您尝试对提交 DAG 进行特定类型的更改，例如“放弃未提交的更改并使‘主’引用指向提交 `5d83f9e`”，可能有一个命令可以执行此操作（例如，在本例中为 `git checkout master; git reset --hard 5d83f9e`）。

(version-control-staging-area)=
## 暂存区

这是与数据模型正交的另一个概念，但它是创建提交的界面的一部分。

您可能想象实现如上所述的快照的一种方法是使用“创建快照”命令，该命令根据工作目录的_当前状态_创建新快照。有些版本控制工具是这样工作的，但 Git 不是。我们想要干净的快照，并且从当前状态创建快照可能并不总是理想的。例如，想象一个场景，您已经实现了两个单独的功能，并且想要创建两个单独的提交，其中第一个提交引入第一个功能，下一个提交引入第二个功能。或者想象一个场景，您在整个代码中添加了调试打印语句以及错误修复；您想要提交错误修复，同时丢弃所有打印语句。

Git 允许您通过称为“暂存区域”的机制指定下一个快照中应包含哪些修改，从而适应这种情况。

(version-control-git-command-line-interface)=
## Git 命令行界面

为了避免重复信息，我们不会在这些讲义中详细解释以下命令。请参阅强烈推荐的 [Pro Git](https://git-scm.com/book/en/v2) 了解更多信息，或观看讲座视频。

(version-control-basics)=
### 基础知识

- `git help <command>`：获取 git 命令的帮助
- `git init`：创建一个新的 git 仓库，数据存储在 `.git` 目录中
- `git status`：告诉您发生了什么事
- `git add <filename>`：将文件添加到暂存区
- `git commit`：创建一个新提交
    - 写入 [良好的提交消息](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)！
    - 写 [良好的提交消息](https://chris.beams.io/posts/git-commit/) 的更多理由！
- `git log`：显示历史记录的扁平化日志
- `git log --all --graph --decorate`：将历史可视化为 DAG
- `git diff <filename>`：显示您相对于暂存区域所做的更改
- `git diff <revision> <filename>`：显示快照之间文件的差异
- `git checkout <revision>`：更新 HEAD（如果检出分支则更新当前分支）

(version-control-branching-and-merging)=
### 分支和合并

- `git branch`：显示分支
- `git branch <name>`：创建分支
- `git switch <name>`：切换到分支
- `git checkout -b <name>`：创建分支并切换到该分支
    - 与 `git branch <name>; git switch <name>` 相同
- `git merge <revision>`：合并到当前分支
- `git mergetool`：使用精美的工具来帮助解决合并冲突
- `git rebase`：将补丁集重新设置到新的基础上

(version-control-remotes)=
### 远端

- `git remote`：列出远端
- `git remote add <name> <url>`：添加远程
- `git push <remote> <local branch>:<remote branch>`：发送对象到远程，并更新远程引用
- `git branch --set-upstream-to=<remote>/<remote branch>`：建立本地和远程分支之间的对应关系
- `git fetch`：从远程检索对象/引用
- `git pull`：与 `git fetch; git merge` 相同
- `git clone`：从远程下载仓库

(version-control-undo)=
### 撤消

- `git commit --amend`：编辑提交的内容/消息
- `git reset <file>`：取消暂存文件
- `git restore`：放弃更改

(version-control-advanced-git)=
## 高级 Git

- `git config`：Git 是 [高度可定制](https://git-scm.com/docs/git-config)
- `git clone --depth=1`：浅克隆，没有完整的版本历史记录
- `git add -p`：交互式暂存
- `git rebase -i`：交互式变基
- `git blame`：显示谁最后编辑了哪一行
- `git stash`：暂时删除对工作目录的修改
- `git bisect`：二分搜索历史记录（例如回归）
- `git revert`：创建一个新的提交来逆转早期提交的效果
- `git worktree`：同时检查多个分支
- `.gitignore`：[指定](https://git-scm.com/docs/gitignore) 有意忽略未跟踪的文件

(version-control-miscellaneous)=
## 杂项

- **GUI**：有很多 [图形用户界面客户端](https://git-scm.com/downloads/guis)
Git 就在那里。我们个人不使用它们，而是使用命令行界面。
- **Shell 集成**：将 Git 状态作为您的一部分非常方便
shell 提示符（[zsh](https://github.com/olivierverdier/zsh-git-prompt)、[bash](https://github.com/magicmonty/bash-git-prompt)）。通常包含在 [Oh My Zsh](https://github.com/ohmyzsh/ohmyzsh) 等框架中。
- **编辑器集成**：与上面类似，与许多
特点。 [fugitive.vim](https://github.com/tpope/vim-fugitive) 是 Vim 的标准版本。
- **工作流程**：我们教您数据模型，以及一些基本命令；我们
没有告诉您在处理大型项目时要遵循哪些实践（并且有 [许多](https://nvie.com/posts/a-successful-git-branching-model/) [不同的](https://www.endoflineblog.com/gitflow-considered-harmful) [方法](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)）。
- **GitHub**：Git 不是 GitHub。 GitHub 有特定的贡献代码方式
到其他项目，称为 [拉取请求](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests)。
- **其他 Git 提供商**：GitHub 并不具有特殊地位：有很多 Git 仓库
主机，例如 [GitLab](https://about.gitlab.com/) 和 [Bitbucket](https://bitbucket.org/)。

(version-control-resources)=
## 资源

- [Pro Git](https://git-scm.com/book/en/v2) **强烈推荐阅读**。
现在您已经了解了数据模型，通过第 1--5 章应该可以教会您熟练使用 Git 所需的大部分内容。后面的章节有一些有趣的高级材料。
- [Oh Shit, Git!?!](https://ohshitgit.com/) 是有关如何恢复的简短指南
一些常见的 Git 错误。
- [计算机版 Git
科学家](https://eagain.net/articles/git-for-computer-scientists/) 是对 Git 数据模型的简短解释，与这些讲义相比，伪代码更少，图表更精美。
- [Git from the Bottom Up](https://jwiegley.github.io/git-from-the-bottom-up/)
对于好奇的人来说，除了数据模型之外，还详细解释了 Git 的实现细节。
- 【如何简单解释git
字](https://smusamashah.github.io/blog/2017/10/14/explain-git-in-simple-words)
- [学习 Git 分支](https://learngitbranching.js.org/) 是一个基于浏览器的
教你 Git 的游戏。

### Exercises

```{exercise} 用数据模型学习基础 Git
:label: exercise-git-model-tutorial

阅读 Pro Git 前几章或完成 Learn Git Branching；对每条命令说明它创建了什么对象、移动了什么引用。
```

```{solution} exercise-git-model-tutorial
:class: dropdown

最低验收：能解释 `add` 更新 index，`commit` 创建 tree/commit 并移动当前分支，`branch` 创建引用，`switch` 改变 HEAD/工作区，`merge` 可能快进或创建双亲提交。用 `git log --graph` 对照自己的解释。
```

```{exercise} 调查课程仓库历史
:label: exercise-git-investigate

克隆课程仓库，画出历史图；找出最后修改 `README.md` 的人，以及 `_config.yml` 中 `collections:` 行最后一次修改对应的提交说明。
```

````{solution} exercise-git-investigate
:class: dropdown

```bash
git clone https://github.com/missing-semester/missing-semester.git
cd missing-semester
git log --all --graph --decorate --oneline
git log -1 --format='%an <%ae>' -- README.md
git blame -L '/collections:/,+1' _config.yml
git show --no-patch --format='%H%n%s' COMMIT
```

仓库会继续变化，所以答案应以运行时输出为准，而不是写死姓名与提交。
````

```{exercise} 从历史中删除大文件或秘密
:label: exercise-git-rewrite-secret

在测试仓库提交一个文件若干次，再把它从整个历史中删除，而不仅是最新快照。
```

```{solution} exercise-git-rewrite-secret
:class: dropdown

在隔离测试仓库使用 `git filter-repo --path secret.bin --invert-paths`，检查 `git log --all -- secret.bin` 与仓库大小，再决定是否强推。真实秘密还必须立即撤销/轮换；改写历史无法让已克隆的副本失效，并会要求所有协作者重新同步。
```

```{exercise} 使用 stash
:label: exercise-git-stash

修改已跟踪文件，运行 `git stash`、`git log --all --oneline` 与 `git stash pop`，解释适用场景。
```

```{solution} exercise-git-stash
:class: dropdown

`stash` 把工作区/暂存区状态保存为特殊引用可达的提交，并恢复干净工作区；`--all` 的图中可看到相关对象。`pop` 应用后成功则删除 stash，冲突时保留。它适合短暂切换上下文，不应代替有说明的长期分支提交。
```

```{exercise} 创建 git graph 别名
:label: exercise-git-graph-alias

配置 `git graph` 输出 `git log --all --graph --decorate --oneline`。
```

````{solution} exercise-git-graph-alias
:class: dropdown

```bash
git config --global alias.graph 'log --all --graph --decorate --oneline'
git graph
```

可用 `git config --global --get alias.graph` 检查；别名值不应再带开头的 `git`。
````

```{exercise} 全局忽略文件
:label: exercise-git-global-ignore

配置 `~/.gitignore_global`，忽略 `.DS_Store` 等操作系统或编辑器临时文件。
```

````{solution} exercise-git-global-ignore
:class: dropdown

```bash
git config --global core.excludesFile ~/.gitignore_global
printf '.DS_Store\n*~\n' >>~/.gitignore_global
git check-ignore -v .DS_Store
```

只把跨项目、只属于个人环境的噪声放到全局文件；项目共同产生的构建产物应写入仓库的 `.gitignore`。
````

```{exercise} 提交一个有价值的 PR
:label: exercise-git-pr

若确实找到课程仓库中的错字或改进，fork 后提交 pull request；找不到就跳过，不要制造无意义修改。
```

```{solution} exercise-git-pr
:class: dropdown

流程：先搜索已有 issue/PR；建小分支；只做一项可验证改动；运行本地检查；写清问题、修改与验证；遵循贡献指南。维护者不欠合并，反馈应及时响应。练习目标是协作质量，不是“获得一个 PR 计数”。
```

```{exercise} 制造并解决合并冲突
:label: exercise-git-conflict

按官方步骤创建 `recipe.txt`，让 `salty` 和 `sweet` 修改同一行，依次合并并解决冲突，最后画出提交图。
```

```{solution} exercise-git-conflict
:class: dropdown

第一次合并通常快进；第二次在同一行出现 `<<<<<<< HEAD`、`=======`、`>>>>>>> sweet`，分别界定当前版本、分隔线和传入版本。编辑成最终内容并删除标记，运行 `git add recipe.txt && git merge --continue`，再用 `git log --graph --oneline --all` 验证合并提交有两条父边。
```

### 许可与署名

本页依据 MIT Missing Semester 2026 第五讲[官方 notes](https://missing.csail.mit.edu/2026/version-control/)整理，原材料采用 [CC BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可。
