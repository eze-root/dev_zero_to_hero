# 第一讲：课程概览与 Shell 入门

> 官方 notes：[Course Overview + Introduction to the Shell](https://missing.csail.mit.edu/2026/course-shell/)  
> 课程主页：[The Missing Semester of Your CS Education](https://missing.csail.mit.edu/)  
> 视频：[YouTube 课程录像](https://www.youtube.com/@MissingSemester)

```{note}
本文依据 2026 年第一讲官方 notes 整理。命令、章节顺序和扩展阅读以官方页面为准；建议一边阅读，一边在自己的终端中实际运行示例。
```

## 课程为什么存在

计算机很擅长处理重复工作，但我们有时只想到让程序自动计算，却忘了也可以让计算机自动完成自己的日常操作。很多人只记住了少数可以勉强工作的命令；遇到问题时，再从网上复制一段并不真正理解的命令。

这门课希望帮助学习者更充分地使用已经知道的工具，认识可以加入工具箱的新工具，并逐渐形成主动探索、组合乃至开发工具的习惯。这正是许多计算机培养方案中缺少的“一学期”。

2026 年课程由 9 次、每次约 1 小时的课程组成。各讲大体独立，但后续课程会默认读者已经掌握前面介绍的概念。课程节奏较快，因此每一讲都配有官方 notes、录像和练习。

## 什么是 Shell

今天的计算机提供图形界面、语音、AR/VR 和 LLM 等多种交互方式。它们适合许多场景，但能做什么通常受界面中已有按钮或预先实现的能力限制。要更完整地调用计算机提供的工具，仍然需要文本接口——**Shell**。

几乎所有平台都提供一种或多种 Shell。不同 Shell 的细节有所区别，但核心能力相近：

- 运行程序；
- 向程序提供输入；
- 读取并组合程序的输出；
- 把重复操作写成可以再次执行的程序。

**Terminal（终端）**是用来显示并操作 Shell 的图形界面；**Shell**则是解释命令并启动程序的环境。二者相关，但并不是同一个东西。

### 打开终端

- Linux：通常可以按 `Ctrl + Alt + T`，或在应用菜单中搜索 Terminal。
- macOS：按 `Cmd + Space`，搜索 Terminal；也可以在“应用程序 → 实用工具”中打开。
- Windows：课程使用 Unix 风格的 Shell。建议安装 [Windows Subsystem for Linux](https://learn.microsoft.com/windows/wsl/) 或使用 Linux 虚拟机，而不是直接使用 `cmd.exe` 或 PowerShell 完成本讲练习。

Linux 和 macOS 上常见的是 Bash。Fish、Zsh 等 Shell 在交互体验上有不少改进，但 Bash 更普遍，相关概念也能够迁移到其他 Shell，因此本讲以 Bash 为主。

## 为什么要学习 Shell

Shell 不仅通常比反复点击图形界面更快，还具有很强的组合能力。多个功能单一的程序可以通过输入、输出和管道连接起来，形成新的自动化流程。

熟悉 Shell 也有助于：

- 安装和使用开源软件；
- 编写持续集成与自动化任务；
- 管理远程服务器；
- 在图形程序失效时定位错误；
- 把一次性的操作沉淀为可重复执行的脚本。

## 在 Shell 中移动

打开终端后，会看到类似下面的提示符：

```console
missing:~$
```

这里的 `missing` 是主机名，`~` 表示当前位于用户的家目录，`$` 通常意味着当前不是 root 用户。提示符之后可以输入要执行的程序：

```console
missing:~$ date
Fri 10 Jan 2020 11:49:31 AM EST

missing:~$ echo hello
hello
```

Shell 通常按空白拆分命令：第一个词是程序，其余部分是传给程序的参数。参数中如果包含空格或特殊字符，可以使用单引号、双引号，或者使用反斜杠转义：

```console
echo "My Photos"
echo 'My Photos'
echo My\ Photos
```

### 查阅帮助

`man` 是 manual 的缩写，用于阅读系统中的命令手册：

```console
man date
```

许多程序也支持较短的 `--help` 帮助。官方 notes 还建议配合 [`tldr`](https://tldr.sh/) 查看常用示例；LLM 也适合用来解释命令，但执行前仍应理解命令会读写哪些文件、是否需要权限，以及是否具有破坏性。

### 当前目录与路径

`cd` 用于切换当前目录。它是 Shell 的内建命令，而不是一个独立程序：

```console
missing:~$ cd /bin
missing:/bin$ cd /
missing:/$ cd ~
missing:~$
```

输入路径时可以按 `Tab` 自动补全。`pwd` 或 `echo $PWD` 可以显示当前工作目录。

以 `/` 开头的是绝对路径；不以 `/` 开头的是相对于当前目录解释的相对路径。每个目录中还可以使用两个特殊路径：

- `.`：当前目录；
- `..`：父目录。

如果经常在多个深层目录之间移动，可以尝试官方 notes 推荐的 [`zoxide`](https://github.com/ajeetdsouza/zoxide)。它会记录常用路径，并通过 `z` 减少输入。

## Shell 中有哪些程序

当输入 `date` 或 `echo` 时，Shell 会在环境变量 `$PATH` 列出的目录中依次查找同名的可执行文件：

```console
missing:~$ echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

missing:~$ which echo
/bin/echo
```

也可以直接给出程序路径，例如 `/bin/echo`，从而绕过 `$PATH` 查找。

### 常用文本工具

- `cat file`：输出文件内容；官方 notes 推荐功能更丰富的 [`bat`](https://github.com/sharkdp/bat)。
- `sort file`：对文件中的行排序。
- `uniq file`：合并相邻的重复行。
- `head file`、`tail file`：查看文件开头或结尾的若干行。
- `grep pattern file`：查找匹配模式的行；[`ripgrep`](https://github.com/BurntSushi/ripgrep) 通常更快，也更适合日常递归搜索。
- `ls path`：列出目录内容；[`eza`](https://eza.rocks/) 提供了更友好的显示效果。

### `sed`：批量编辑文本

`sed` 有自己的文本处理语言。一个常见用法是在文件内进行全局替换：

```console
sed -i 's/pattern/replacement/g' file
```

其中 `-i` 表示直接修改文件，`s` 表示替换，结尾的 `g` 表示替换一行中的所有匹配，而不只是第一个。正式执行前，可以先去掉 `-i` 查看输出，避免误改文件。

### `find`：按条件查找文件

查找下载目录中超过 30 天的 ZIP 文件：

```console
find ~/Downloads -type f -name "*.zip" -mtime +30
```

查找家目录中大于 100 MB 的文件并显示详细信息：

```console
find ~ -type f -size +100M -exec ls -lh {} \;
```

查找包含 `TODO` 的 Python 文件：

```console
find . -name "*.py" -exec grep -l "TODO" {} \;
```

如果觉得 `find` 语法难记，可以尝试官方 notes 推荐的 [`fd`](https://github.com/sharkdp/fd)。

### `awk`：按字段解析文本

下面的命令打印每一行按空白分隔后的第二列：

```console
awk '{print $2}' file
```

加入 `-F,` 后可以按逗号分隔字段。除了选取列，`awk` 还能筛选记录、修改字段并计算聚合结果。

### 用管道组合程序

管道符 `|` 会把左侧程序的标准输出接到右侧程序的标准输入。官方 notes 给出了一个组合示例：从远程服务器取得 SSH 日志，筛选断开连接记录，提取用户名，再统计最常见的用户名。

```console
ssh myserver 'journalctl -u sshd -b-1 | grep "Disconnected from"' \
  | sed -E 's/.*Disconnected from .* user (.*) [^ ]+ port.*/\1/' \
  | sort | uniq -c \
  | sort -nk1,1 | tail -n10 \
  | awk '{print $2}' | paste -sd,
```

这个例子体现了 Unix 工具的重要思想：让每个程序做好一件事，再通过统一的文本流把它们组合起来。

## Shell 也是一门语言

Bash 和 Python、Ruby 一样具有变量、条件、循环和函数。终端里输入的每条命令，本质上都是交给 Shell 解释的一小段程序。

### 重定向与 `tee`

- `> file`：把标准输出写入文件，并覆盖原内容。
- `>> file`：把标准输出追加到文件末尾。
- `< file`：让程序从文件读取标准输入。
- `2> file`：把标准错误写入文件。

`tee` 可以一边把输入写入文件，一边继续输出给下一个程序：

```console
verbose_cmd | tee verbose.log | grep CRITICAL
```

### 条件判断

```bash
if command1; then
  command2
  command3
fi
```

只有当 `command1` 成功退出时，后面的命令才会执行。常见的判断工具是 `test`，也经常写成 `[`：

```bash
if [ -f "$file" ]; then
  echo "file exists"
fi
```

Bash 还提供 `[[ ... ]]`，在字符串比较和模式匹配中通常比传统的 `[` 更安全易用。

### 循环与命令替换

```bash
for i in $(seq 1 10); do
  echo "$i"
done
```

`$(...)` 会先运行括号中的命令，再把输出替换到当前位置。旧脚本中可能使用反引号实现命令替换，但 `$()` 更容易嵌套，应该优先使用。

### 编写脚本

较长的命令应写入 `.sh` 文件。脚本首行的 shebang 指定解释器：

```bash
#!/bin/bash
set -euo pipefail
```

第二行让 Bash 以更严格的方式执行脚本：

- `-e`：命令失败后尽早退出；
- `-u`：使用未定义变量时立即报错；
- `-o pipefail`：管道中任一程序失败时，使整个管道返回失败。

这些选项能减少常见错误，但不能替代测试。Shell 编程有很多边界情况，官方 notes 强烈建议用 [ShellCheck](https://www.shellcheck.net/) 检查脚本。LLM 适合辅助解释、编写和调试脚本；当脚本增长到难以维护时，也可以让它协助迁移到 Python 等更合适的语言。

## 下一步

完成本讲后，你应当能够在目录之间移动、理解绝对路径与相对路径、查阅程序帮助，并把基础命令通过管道和重定向连接起来。下一讲将继续介绍命令行环境及其自动化能力。

## Exercises

完整练习与最新链接请以[官方练习列表](https://missing.csail.mit.edu/2026/course-shell/#exercises)为准。练习的价值在于调查和推理的过程：先阅读手册、缩小问题并观察中间输出，再把问题和已经尝试过的方法交给同学、论坛或 LLM 讨论。

```{exercise} 确认 Unix Shell 环境
:label: exercise-shell-environment

本课程需要使用 Bash 或 Zsh 等 Unix Shell。Linux 和 macOS 通常无须额外配置；Windows 用户应使用 WSL 或 Linux 虚拟机，而不是 `cmd.exe` 或 PowerShell。

运行 `echo $SHELL`。如果输出类似 `/bin/bash` 或 `/usr/bin/zsh`，说明当前环境符合要求。
```

```{exercise} 阅读 ls -l 的输出
:label: exercise-ls-long-format

运行 `ls -l /` 并观察输出。每一行开头的 10 个字符分别表示什么？请结合 `man ls` 调查文件类型和权限位的含义。
```

```{exercise} 练习 glob 模式
:label: exercise-shell-globs

在 `find ~/Downloads -type f -name "*.zip" -mtime +30` 中，`*.zip` 是一个 glob。创建一个测试目录和若干文件，分别尝试 `ls *.txt`、`ls file?.txt` 和 `ls {a,b,c}.txt`，解释每个模式匹配了哪些文件。

参考：[Bash Pattern Matching](https://www.gnu.org/software/bash/manual/html_node/Pattern-Matching.html)。
```

```{exercise} 比较不同引号
:label: exercise-shell-quoting

比较 `'single quotes'`、`"double quotes"` 和 `$'ANSI quotes'` 的区别。编写一条命令，使它输出包含字面量 `$`、`!` 和换行符的字符串。

参考：[Bash Quoting](https://www.gnu.org/software/bash/manual/html_node/Quoting.html)。
```

```{exercise} 重定向标准流
:label: exercise-standard-streams

Shell 有三个标准流：stdin（0）、stdout（1）和 stderr（2）。运行 `ls /nonexistent /tmp`，把 stdout 与 stderr 分别重定向到不同文件；然后尝试把二者重定向到同一个文件。
```

```{exercise} 退出状态与条件执行
:label: exercise-exit-status

`$?` 保存上一条命令的退出状态，其中 0 表示成功。`&&` 只在前一条命令成功时执行下一条命令，`||` 只在前一条命令失败时执行下一条命令。

编写一条单行命令：仅当 `/tmp/mydir` 不存在时创建它。
```

```{exercise} 为什么 cd 是内建命令
:label: exercise-cd-builtin

解释为什么 `cd` 必须由 Shell 自身实现，而不能只是一个独立程序。思考子进程能够修改哪些状态，以及它是否能改变父进程的当前工作目录。
```

```{exercise} 判断文件是否存在
:label: exercise-file-test

编写一个 Shell 脚本，接收文件名参数 `$1`，并使用 `test -f` 或 `[ -f ... ]` 判断文件是否存在。根据判断结果输出不同信息。

参考：[Bash Conditional Expressions](https://www.gnu.org/software/bash/manual/html_node/Bash-Conditional-Expressions.html)。
```

```{exercise} 理解可执行权限
:label: exercise-executable-bit

把上一题的脚本保存为 `check.sh`，尝试运行 `./check.sh somefile`。随后执行 `chmod +x check.sh` 并再次运行。比较修改前后的 `ls -l check.sh` 输出，并解释为什么需要这一步。
```

```{exercise} 使用 set -x 调试
:label: exercise-set-x

在一个简单脚本中把 `-x` 加入 `set` 的选项，运行脚本并观察输出。解释这些额外信息如何帮助调试命令展开与执行顺序。
```

```{exercise} 创建带日期的备份
:label: exercise-dated-backup

编写一条命令，把文件复制为文件名中包含当天日期的备份。例如，把 `notes.txt` 复制为 `notes_2026-01-12.txt`。

提示：使用 `$(date +%Y-%m-%d)` 完成命令替换。
```

```{exercise} 参数化测试脚本
:label: exercise-parameterize-script

修改本讲用于复现偶发失败的测试脚本，使测试命令通过参数传入，而不是固定写成 `cargo test my_test`。调查 `$1` 与 `$@` 的差别，并选择合适的形式。
```

```{exercise} 统计常见文件扩展名
:label: exercise-common-extensions

使用管道找出家目录中最常见的 5 种文件扩展名。可以组合 `find`、`grep`、`sed` 或 `awk`、`sort`、`uniq -c` 与 `head`。
```

```{exercise} 使用 find 与 xargs
:label: exercise-find-xargs

不要使用 `find -exec`，而是组合 `find` 与 `xargs`：查找目录中的所有 `.sh` 文件，并用 `wc -l` 统计每个文件的行数。

加分项：使用 `-print0` 和 `-0` 正确处理文件名中的空格。
```

```{exercise} 用 curl 与 grep 检查课程网站
:label: exercise-curl-grep

使用 `curl` 获取 `https://missing.csail.mit.edu/` 的 HTML，再通过管道交给 `grep`，统计页面列出了多少讲课程。可以用 `curl -s` 隐藏进度输出。
```

```{exercise} 使用 jq 处理 JSON
:label: exercise-jq-json

使用 `curl` 获取 `https://microsoftedge.github.io/Demos/json-dummy-data/64KB.json`，然后用 [`jq`](https://jqlang.github.io/jq/) 只输出 `version` 大于 6 的人员姓名。

先把数据传给 `jq .` 观察结构，再尝试使用 `.[] | select(...) | .name`。
```

````{exercise} 用 awk 筛选并交换列
:label: exercise-awk-columns

编写一个 `awk` 命令：仅输出第二列大于 100 的行，同时交换第一列和第三列。使用下面的数据测试：

```console
printf 'a 50 x\nb 150 y\nc 200 z\n'
```
````

```{exercise} 拆解并重组日志管道
:label: exercise-shell-pipeline

逐步解释本讲 SSH 日志管道中每个程序的输入、输出和作用。随后参考它的组合方式，从 `~/.bash_history` 或 `~/.zsh_history` 中统计自己最常使用的命令。
```

## 参考解答

```{solution} exercise-shell-environment
:class: dropdown

`echo "$SHELL"` 显示登录 Shell；`ps -p $$ -o comm=` 显示当前正在运行的 Shell。前者可能仍是 Bash，即使你当前临时进入了 Zsh，因此最好同时检查两条命令。
```

```{solution} exercise-ls-long-format
:class: dropdown

第一位表示类型：`-` 是普通文件，`d` 是目录，`l` 是符号链接。后九位每三位一组，依次是所有者、用户组和其他用户的 `rwx` 权限。随后通常是硬链接数、所有者、用户组、大小、修改时间和名称。
```

```{solution} exercise-shell-globs
:class: dropdown

`*.txt` 匹配任意长度前缀；`file?.txt` 中的 `?` 恰好匹配一个字符；`{a,b,c}.txt` 是 Shell 的花括号展开，先生成三个参数 `a.txt b.txt c.txt`，它本身不是路径匹配。
```

````{solution} exercise-shell-quoting
:class: dropdown

单引号中的内容完全按字面处理；双引号允许变量与命令替换；ANSI-C 引号 `$'...'` 还会解释 `\n` 等转义。示例：

```bash
printf '%s\n' $'$ !\n第二行'
```
````

````{solution} exercise-standard-streams
:class: dropdown

```bash
ls /nonexistent /tmp >out.txt 2>err.txt
ls /nonexistent /tmp >all.txt 2>&1
# Bash 也可写成：ls /nonexistent /tmp &>all.txt
```

`2>&1` 必须放在 `>all.txt` 之后，含义是让 stderr 指向“此刻 stdout 指向的位置”。
````

````{solution} exercise-exit-status
:class: dropdown

```bash
[ -d /tmp/mydir ] || mkdir /tmp/mydir
```

实际脚本中通常直接使用可重复执行的 `mkdir -p /tmp/mydir`，还能避免检查与创建之间的竞态条件。
````

```{solution} exercise-cd-builtin
:class: dropdown

独立程序在子进程中运行，只能改变自己的工作目录；进程退出后父 Shell 的目录不会变化。`cd` 必须在 Shell 进程内执行，才能修改 Shell 后续命令所使用的工作目录。
```

````{solution} exercise-file-test
:class: dropdown

```bash
#!/usr/bin/env bash
set -u
if [[ $# -ne 1 ]]; then
  echo "用法：$0 FILE" >&2
  exit 2
elif [[ -f $1 ]]; then
  echo "$1 是普通文件"
else
  echo "$1 不存在或不是普通文件" >&2
  exit 1
fi
```
````

```{solution} exercise-executable-bit
:class: dropdown

`chmod +x check.sh` 为相应用户增加执行位。之后内核才允许通过 `./check.sh` 直接执行它，并依据 shebang 选择解释器。即使没有执行位，`bash check.sh` 仍可运行，因为被执行的是 `bash`，脚本只是它读取的数据文件。
```

```{solution} exercise-set-x
:class: dropdown

`set -x` 会在执行前把完成变量展开、命令替换后的命令写到 stderr，默认以 `+` 开头。它适合追踪分支与参数，但可能泄露口令、令牌等敏感值，不应在含秘密信息的日志中长期启用。
```

````{solution} exercise-dated-backup
:class: dropdown

```bash
cp -- notes.txt "notes_$(date +%F).txt"
```

`--` 阻止以连字符开头的文件名被当作选项，双引号避免命令替换结果被再次分词。
````

````{solution} exercise-parameterize-script
:class: dropdown

把固定测试命令替换成 `"$@"`：

```bash
[[ $# -gt 0 ]] || { echo "用法：$0 COMMAND [ARG ...]" >&2; exit 2; }
while "$@" >stdout.log 2>stderr.log; do
  ((runs += 1))
done
```

`$1` 只代表第一个参数；`"$@"` 会保留所有参数各自的边界，适合转发一整条命令。
````

````{solution} exercise-common-extensions
:class: dropdown

一种近似统计方法如下；没有扩展名的文件会被忽略：

```bash
find "$HOME" -type f -printf '%f\n' 2>/dev/null \
  | awk -F. 'NF>1 {print "." $NF}' \
  | sort | uniq -c | sort -nr | head -5
```

macOS 的 BSD `find` 没有 `-printf`，可改用 `find ... -print` 后再由 `awk` 去掉目录部分。
````

````{solution} exercise-find-xargs
:class: dropdown

```bash
find . -type f -name '*.sh' -print0 | xargs -0 -r wc -l
```

NUL 字符是 Unix 文件名中不能出现的字符，所以 `-print0`/`-0` 比按换行拆分更可靠。BSD `xargs` 没有 `-r`，可省略它。
````

````{solution} exercise-curl-grep
:class: dropdown

```bash
curl -fsSL https://missing.csail.mit.edu/ \
  | grep -oE '/2026/[^"/]+' | sort -u | wc -l
```

HTML 结构会变化，因此结果应与课程主页人工核对；2026 年课程目录共有 9 讲。更稳妥的抓取应使用 HTML 解析器，而不是把正则表达式当作通用 HTML 解析器。
````

````{solution} exercise-jq-json
:class: dropdown

```bash
curl -fsSL https://microsoftedge.github.io/Demos/json-dummy-data/64KB.json \
  | jq -r '.[] | select(.version > 6) | .name'
```

`-r` 输出未加 JSON 引号的原始字符串。
````

````{solution} exercise-awk-columns
:class: dropdown

```bash
printf 'a 50 x\nb 150 y\nc 200 z\n' \
  | awk '$2 > 100 {tmp=$1; $1=$3; $3=tmp; print}'
```

输出为 `y 150 b` 和 `z 200 c`。
````

````{solution} exercise-shell-pipeline
:class: dropdown

远端 `journalctl` 读取上一轮启动的 SSH 日志，`grep` 保留断开连接行；本地 `sed` 提取用户名，第一次 `sort | uniq -c` 计数，第二次 `sort` 按次数排序，`tail` 取最高的十项，`awk` 取用户名，`paste` 合并为逗号分隔的一行。

Bash 的历史统计可以写成：

```bash
history | awk '{$1=""; print substr($0,2)}' \
  | sort | uniq -c | sort -nr | head -10
```

Zsh 使用 `history 1`，且历史文件的具体格式可能受配置影响。
````

## 许可与署名

本页依据 MIT Missing Semester 2026 第一讲[官方 notes](https://missing.csail.mit.edu/2026/course-shell/)整理。原课程由 Anish Athalye、Jon Gjengset 和 Jose Javier Gonzalez Ortiz 共同讲授，材料采用 [CC BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可。
