# 第五讲：版本控制与 Git

> 官方 notes：[Version Control and Git](https://missing.csail.mit.edu/2026/version-control/)  
> 视频：[YouTube](https://www.youtube.com/watch?v=9K8lB61dl3Y)

```{note}
Git 的命令行界面并不总是直观。与其背“咒语”，不如先理解对象、提交图、引用和暂存区；命令只是对这些结构的操作。
```

## 为什么使用版本控制

版本控制系统记录目录的一系列快照和作者、时间、说明等元数据。即使独自开发，也能回答“某行是谁、何时、为什么修改的”“哪个提交引入了回归”，并支持并行试验与可靠回退；多人开发时，它还是交换修改和解决冲突的基础。

```{important}
Git 是版本控制软件；GitHub 是 Git 仓库托管与协作平台。GitLab、Gitee、Bitbucket 等也能托管 Git 仓库，二者不要混为一谈。
```

## Git 的数据模型

文件内容是 blob，目录是“名称到 blob/tree”的 tree；一个提交包含顶层 tree、父提交、作者和说明。提交之间形成有向无环图（DAG）：普通提交通常有一个父，合并提交可有多个父。提交对象不可变；所谓“改历史”其实是创建新对象，再移动引用。

Git 对对象内容计算哈希并以哈希寻址。相同内容对应相同对象；tree 保存子对象哈希，commit 保存 tree 与父 commit 哈希。可用 `git cat-file -p HASH` 观察底层对象。

40 位哈希不便记忆，因此分支、标签等 reference 提供可移动的人类名称；`HEAD` 表示当前所在位置，通常符号指向当前分支。粗略地说，仓库就是对象数据库加引用集合。

## 工作区、暂存区与提交

Git 没有强制把工作目录的全部状态一次提交。`git add` 把选中的版本写入暂存区（index），`git commit` 再从暂存区生成快照。因此同一工作区的两项修改可以用 `git add -p` 拆成两个清晰提交，调试打印也不必混入修复。

```bash
git status
git diff                 # 工作区与暂存区
git diff --cached        # 暂存区与 HEAD
git add -p
git commit
git log --all --graph --decorate --oneline
```

## 分支、远端与撤销

分支只是指向提交的可移动引用，创建成本很低。`git switch -c feature` 创建并切换，`git merge` 把另一条历史并入当前分支；`git rebase` 在新基底上重放提交，会生成新提交，不应随意重写他人已经基于其工作的共享历史。

远端是另一组对象和引用。`fetch` 只取回数据并更新远端跟踪引用；`pull` 通常相当于 fetch 后 merge/rebase；`push` 发送对象并请求移动远端引用。

撤销前先问“改动在哪一层、是否已经共享”：

- 工作区误改：`git restore PATH`；
- 误暂存：`git restore --staged PATH`；
- 本地最近提交：`git commit --amend`；
- 已共享提交：优先 `git revert COMMIT` 创建反向提交；
- 临时收起工作区：`git stash`；
- 查回归：`git bisect`；
- 同时检出多个分支：`git worktree`。

`reset --hard`、历史过滤和强制推送会丢失或改写可达历史，执行前必须明确目标、备份引用并协调协作者。

## Exercises

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

## 许可与署名

本页依据 MIT Missing Semester 2026 第五讲[官方 notes](https://missing.csail.mit.edu/2026/version-control/)整理，原材料采用 [CC BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可。
