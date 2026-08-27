# 第二讲：命令行环境

> 官方 notes：[https://missing.csail.mit.edu/2026/command-line-environment/](https://missing.csail.mit.edu/2026/command-line-environment/)  
> 视频：[YouTube](https://www.youtube.com/watch?v=ccBGsPedE9Q)

```{note}
本文依照 Missing Semester 2026 官方 notes 的原文结构完整翻译；保留标题层级、命令示例、工具链接、引用与提示。练习采用 MyST exercise，并在官方题目之外补充折叠参考答案。
```


正如我们在上一讲中所介绍的，大多数 shell 不仅仅是启动其他程序的启动器，但实际上它们提供了一个完整的编程语言，其中充满了常见的模式和抽象。然而，与大多数编程语言不同，在 shell 脚本中，一切都是围绕运行程序并让它们简单有效地相互通信而设计的。

特别是，shell 脚本受到_约定_的严格约束。为了让命令行界面 (CLI) 程序在更广泛的 shell 环境中良好运行，需要遵循一些常见模式。我们现在将介绍理解命令行程序如何工作所需的许多概念以及如何使用和配置它们的普遍约定。

(command-line-environment-the-command-line-interface)=
## 命令行界面

在大多数编程语言中编写函数类似于：

```
def add(x: int, y: int) -> int:
    return x + y
```

在这里我们可以明确地看到程序的输入和输出。相比之下，shell 脚本乍一看可能看起来完全不同。

```shell
#!/usr/bin/env bash

if [[ -f $1 ]]; then
    echo "Target file already exists"
    exit 1
else
    if $DEBUG; then
        grep 'error' - | tee $1
    else
        grep 'error' - > $1
    fi
    exit 0
fi
```

为了正确理解像这样的脚本中发生的事情，我们首先需要介绍一些在 shell 程序相互通信或与 shell 环境通信时经常出现的概念：

- 参数
- 流
- 环境变量
- 返回码
- 信号

(command-line-environment-arguments)=
### 参数

Shell 程序在执行时会收到一个参数列表。参数在 shell 中是纯字符串，由程序如何解释它们。例如，当我们执行 `ls -l folder/` 时，我们正在执行带有参数 `['-l', 'folder/']` 的程序 `/bin/ls`。

在 shell 脚本中，我们通过特殊的 shell 语法访问它们。要访问第一个参数，我们访问变量 `$1`，第二个参数 `$2` 等等，直到 `$9`。要以列表的形式访问所有参数，我们使用 `$@` 并检索参数的数量 `$#`。此外，我们还可以使用 `$0` 访问程序的名称。

对于大多数程序，参数将由 _flags_ 和常规字符串混合组成。可以识别标志，因为它们前面有破折号 (`-`) 或双破折号 (`--`)。标志通常是可选的，它们的作用是修改程序的行为。例如，`ls -l` 更改了 `ls` 输出格式的方式。

您将看到具有长名称的双破折号标志（例如 `--all`）和单破折号标志（例如 `-a`），它们通常后面跟着一个字母。可能会在两种格式中指定相同的选项，`ls -a` 和 `ls --all` 是等效的。单破折号标志通常分组，因此 `ls -l -a` 和 `ls -la` 也是等效的。标志的顺序通常也不重要，`ls -la` 和 `ls -al` 产生相同的结果。有些标志非常普遍，当您更加熟悉 shell 环境时，您将直观地找到它们，例如（`--help`、`--verbose`、`--version`）。

> 标志是 shell 约定的第一个很好的例子。 shell 语言不要求我们的程序以这种特定方式使用 `-` 或 `--`。
没有什么可以阻止我们使用语法 `myprogram +myoption myfile` 编写程序，但这会导致混乱，因为我们期望使用破折号。
> 实际上，大多数编程语言都提供 CLI 标志解析库（例如，Python 中的 `argparse` 用于使用破折号语法解析参数）。

CLI 程序中的另一个常见约定是程序接受数量可变的相同类型的参数。当以这种方式给出参数时，该命令对每个参数执行相同的操作。

```shell
mkdir src
mkdir docs
# 相当于
mkdir src docs
```

这个语法糖乍一看似乎没有必要，但与 _globbing_ 结合使用时它变得非常强大。通配符或通配符是 shell 在调用程序之前将扩展的特殊模式。

假设我们想以非递归方式删除当前文件夹中的所有 .py 文件。根据我们在上一讲中学到的知识，我们可以通过运行来实现这一点

```shell
for file in $(ls | grep -P '\.py$'); do
    rm "$file"
done
```

但我们可以用 `rm *.py` 来替换它！

当我们在终端中输入 `rm *.py` 时，shell 不会使用参数 `['*.py']` 调用 `/bin/rm` 程序。相反，shell 将在当前文件夹中搜索与模式 `*.py` 匹配的文件，其中 `*` 可以匹配任何类型的零个或多个字符的任何字符串。因此，如果我们的文件夹具有 `main.py` 和 `utils.py`，则 `rm` 程序将接收参数 `['main.py', 'utils.py']`。

您会发现的最常见的通配符是通配符 `*`（零个或多个任何内容）、`?`（恰好是任何内容之一）和花括号。大括号 `{}` 将逗号分隔的模式列表扩展为多个参数。

在实践中，通过激励性示例可以最好地理解 glob。

```shell
touch folder/{a,b,c}.py
# 将扩展到
touch folder/a.py folder/b.py folder/c.py

convert image.{png,jpg}
# 将扩展到
convert image.png image.jpg

cp /path/to/project/{setup,build,deploy}.sh /newpath
# 将扩展到
cp /path/to/project/setup.sh /path/to/project/build.sh /path/to/project/deploy.sh /newpath

# 通配技术也可以组合起来
mv *{.py,.sh} folder
# 将移动所有 *.py 和 *.sh 文件
```

> 某些 shell（例如 zsh）支持更高级的通配形式，例如 `**`，它将扩展为包含递归路径。因此 `rm **/*.py` 将递归删除所有 .py 文件。


(command-line-environment-streams)=
### 流

每当我们执行像这样的程序管道时

```shell
cat myfile | grep -P '\d+' | uniq -c
```

我们看到 `grep` 程序正在与 `cat` 和 `uniq` 程序进行通信。

这里的一个重要观察是所有三个程序都同时执行。也就是说，shell 并不是先调用 cat，然后调用 grep，然后调用 uniq。相反，所有三个程序都被生成，并且 shell 将 cat 的输出连接到 grep 的输入，并将 grep 的输出连接到 uniq 的输入。使用管道运算符 `|` 时，shell 对从一个程序流向链中下一个程序的数据流进行操作。

我们可以演示这种并发性，管道中的所有命令都会立即启动：

```console
$ (sleep 15 && cat numbers.txt) | grep -P '^\d$' | sort | uniq  &
[1] 12345
$ ps | grep -P '(sleep|cat|grep|sort|uniq)'
  32930 pts/1    00:00:00 sleep
  32931 pts/1    00:00:00 grep
  32932 pts/1    00:00:00 sort
  32933 pts/1    00:00:00 uniq
  32948 pts/1    00:00:00 grep
```

我们可以看到除了 `cat` 之外的所有进程都在立即运行。 shell 会生成所有进程并在其中任何进程完成之前连接它们的流。 `cat` 仅在睡眠完成后才会启动，并且 `cat` 的输出将发送到 grep 等。

每个程序都有一个输入流，标记为 stdin（用于标准输入）。管道传输时，标准输入会自动连接。在脚本中，许多程序接受 `-` 作为文件名，表示“从 stdin 读取”：

```shell
# 当数据来自管道时，这些是等效的
echo "hello" | grep "hello"
echo "hello" | grep "hello" -
```

类似地，每个程序都有两个输出流：stdout 和 stderr。标准输出是最常遇到的输出，它用于将程序的输出传输到管道中的下一个命令。标准错误是一种替代流，旨在供程序报告警告和其他类型的问题，而不会由链中的下一个命令解析该输出。

```console
$ ls /nonexistent
ls: cannot access '/nonexistent': No such file or directory
$ ls /nonexistent | grep "pattern"
ls: cannot access '/nonexistent': No such file or directory
# 由于 stderr 未通过管道传输，错误消息仍然出现
$ ls /nonexistent 2>/dev/null
# 无输出 - stderr 被重定向到 /dev/null
```

shell 提供了用于重定向这些流的语法。以下是一些说明性示例。

```shell
# 将标准输出重定向到文件（覆盖）
echo "hello" > output.txt

# 将标准输出重定向到文件（追加）
echo "world" >> output.txt

# 将 stderr 重定向到文件
ls foobar 2> errors.txt

# 将 stdout 和 stderr 重定向到同一文件
ls foobar &> all_output.txt

# 从文件重定向 stdin
grep "pattern" < input.txt

# 通过重定向到 /dev/null 丢弃输出
cmd > /dev/null 2>&1
```

另一个体现 Unix 哲学的强大工具是 [`fzf`](https://github.com/junegunn/fzf)，一个模糊查找器。它从标准输入读取行并提供一个交互式界面来过滤和选择：

```console
$ ls | fzf
$ cat ~/.bash_history | fzf
```

`fzf` 可以与许多 shell 操作集成。当我们讨论 shell 定制时，我们会看到它的更多用途。


(command-line-environment-environment-variables)=
### 环境变量

要在 bash 中分配变量，我们使用语法 `foo=bar`，然后使用 `$foo` 语法访问变量的值。请注意，`foo = bar` 是无效语法，因为 shell 会将其解析为使用参数 `['=', 'bar']` 调用程序 `foo`。在 shell 脚本中，空格字符的作用是执行参数分割。这种行为可能会令人困惑且难以适应，因此请记住这一点。

Shell 变量没有类型，它们都是字符串。请注意，在 shell 中编写字符串表达式时，单引号和双引号不能互换。用 `'` 分隔的字符串是文字字符串，不会扩展变量、执行命令替换或处理转义序列，而 `"` 分隔的字符串则会。

```shell
foo=bar
echo "$foo"
# 打印栏
echo '$foo'
# 打印 $foo
```

为了将命令的输出捕获到变量中，我们使用_命令替换_。当我们执行
```shell
files=$(ls)
echo "$files" | grep README
echo "$files" | grep ".py"
```
ls 的输出（具体来说是标准输出）被放入变量 `$files` 中，我们稍后可以访问该变量。 `$files` 变量的内容确实包含 ls 输出中的换行符，这就是 `grep` 等程序如何知道独立操作每个项目的方式。

一个鲜为人知的类似功能是_进程替换_，`<( CMD )` 将执行 `CMD` 并将输出放入临时文件中，并用该文件名替换 `<()`。当命令期望值通过文件而不是 STDIN 传递时，这非常有用。例如，`diff <(ls src) <(ls docs)` 将显示目录 `src` 和 `docs` 中的文件之间的差异。

每当 shell 程序调用另一个程序时，它都会传递一组通常称为“环境变量”的变量。在 shell 中，我们可以通过运行 `printenv` 找到当前的环境变量。要显式传递环境变量，我们可以在命令前面加上变量赋值

> 环境变量通常以 ALL_CAPS 书写（例如 `HOME`、`PATH`、`DEBUG`）。这是一个约定，不是技术要求，但遵循它有助于区分环境变量和通常为小写的本地 shell 变量。

```shell
TZ=Asia/Tokyo date  # prints the current time in Tokyo
echo $TZ  # this will be empty, since TZ was only set for the child command
```

或者，我们可以使用 `export` 内置函数来修改当前环境，因此所有子进程都将继承该变量：

```shell
export DEBUG=1
# 从此时起，所有程序的环境中都将具有 DEBUG=1
bash -c 'echo $DEBUG'
# 打印 1
```

要删除变量，请使用 `unset` 内置命令，例如`unset DEBUG`。

> 环境变量是另一个 shell 约定。它们可用于隐式而不是显式地修改许多程序的行为。例如，shell 将 `$HOME` 环境变量设置为当前用户的主文件夹的路径。然后程序可以访问此变量来获取此信息，而不需要显式的 `--home /home/alice`。另一个常见的示例是 `$TZ`，许多程序使用它根据指定的时区来格式化日期和时间。

(command-line-environment-return-codes)=
### 返回码

正如我们之前看到的，shell 程序的主要输出是通过 stdout/stderr 流和文件系统副作用来传达的。

默认情况下，shell 脚本将返回退出代码零。惯例是零意味着一切顺利，而非零意味着遇到了一些问题。要返回非零退出代码，我们必须使用内置的 `exit NUM` shell。我们可以通过访问特殊变量 `$?` 来访问最后运行的命令的返回码。

shell 有布尔运算符 `&&` 和 `||` 分别用于执行 AND 和 OR 运算。与常规编程语言中遇到的不同，shell 中的语言对程序的返回码进行操作。这两个都是 [短路](https://en.wikipedia.org/wiki/Short-circuit_evaluation) 运算符。这意味着它们可用于根据先前命令的成功或失败有条件地运行命令，其中成功是根据返回代码是否为零来确定的。一些例子：

```shell
# echo 仅当 grep 成功时才会运行（找到匹配项）
grep -q "pattern" file.txt && echo "Pattern found"

# echo 仅在 grep 失败（不匹配）时运行
grep -q "pattern" file.txt || echo "Pattern not found"

# true 是一个总是成功的 shell 程序
true && echo "This will always print"

# false 是一个总是失败的 shell 程序
false || echo "This will always print"
```

同样的原则适用于 `if` 和 `while` 语句，它们都使用返回码来做出决定：

```shell
# if 使用条件命令的返回码（0 = true，非零 = false）
if grep -q "pattern" file.txt; then
    echo "Found"
fi

# 只要命令返回 0，while 循环就会继续
while read line; do
    echo "$line"
done < file.txt
```

(command-line-environment-signals)=
### 信号

在某些情况下，您需要在程序执行时中断程序，例如，如果命令需要很长时间才能完成。中断程序的最简单方法是按 `Ctrl-C`，命令可能会停止。但这实际上是如何运作的以及为什么它有时无法阻止该过程？

```console
$ sleep 100
^C
$
```

> 请注意，此处 `^C` 是在终端中键入时显示的 `Ctrl-C`。

在幕后，这里发生的事情如下：

1. 我们按下`Ctrl-C`
2. shell识别特殊字符组合
3. shell进程向`sleep`进程发送了SIGINT信号
4. 该信号中断了 `sleep` 进程的执行

信号是一种特殊的通信机制。当进程接收到信号时，它会停止执行，处理该信号，并可能根据信号传递的信息更改执行流程。因此，信号是_软件中断_。


在我们的例子中，当输入 `Ctrl-C` 时，这会提示 shell 向进程传递 `SIGINT` 信号。下面是一个 Python 程序的最小示例，该程序捕获 `SIGINT` 并忽略它，不再停止。要终止该程序，我们现在可以通过键入 `Ctrl-\` 来使用 `SIGQUIT` 信号。

```python
#!/usr/bin/env python
import signal, time

def handler(signum, time):
    print("\nI got a SIGINT, but I am not stopping")

signal.signal(signal.SIGINT, handler)
i = 0
while True:
    time.sleep(.1)
    print("\r{}".format(i), end="")
    i += 1
```

如果我们向该程序发送 `SIGINT` 两次，然后发送 `SIGQUIT`，则会发生以下情况。请注意，`^` 是在终端中键入时显示的 `Ctrl`。

```console
$ python sigint.py
24^C
I got a SIGINT, but I am not stopping
26^C
I got a SIGINT, but I am not stopping
30^\[1]    39913 quit       python sigint.py
```

虽然 `SIGINT` 和 `SIGQUIT` 通常都与终端相关请求相关联，但用于请求进程正常退出的更通用信号是 `SIGTERM` 信号。要发送此信号，我们可以使用 [`kill`](https://www.man7.org/linux/man-pages/man1/kill.1.html) 命令，其语法为 `kill -TERM <PID>`。

除了杀死进程之外，信号还可以做其他事情。例如，`SIGSTOP` 暂停进程。在终端中，输入 `Ctrl-Z` 将提示 shell 发送 `SIGTSTP` 信号，该信号是 Terminal Stop 的缩写（即终端版本的 `SIGSTOP`）。

然后，我们可以分别使用 [`fg`](https://www.man7.org/linux/man-pages/man1/fg.1p.html) 或 [`bg`](https://man7.org/linux/man-pages/man1/bg.1p.html) 在前台或后台继续暂停的作业。

[`jobs`](https://www.man7.org/linux/man-pages/man1/jobs.1p.html) 命令列出与当前终端会话关联的未完成作业。您可以使用这些作业的 pid 来引用它们（您可以使用 [`pgrep`](https://www.man7.org/linux/man-pages/man1/pgrep.1.html) 来查找）。更直观的是，您还可以使用百分比符号后跟其作业编号（由 `jobs` 显示）来引用进程。要引用最后一个后台作业，您可以使用 `$!` 特殊参数。

另一件需要知道的事情是，命令中的 `&` 后缀将在后台运行该命令，给您返回提示，尽管它仍然会使用 shell 的 STDOUT，这可能很烦人（在这种情况下使用 shell 重定向）。同样，要使已运行的程序后台运行，您可以执行 `Ctrl-Z`，然后执行 `bg`。


请注意，后台进程仍然是终端的子进程，如果您关闭终端，后台进程将会终止（这将发送另一个信号 `SIGHUP`）。为了防止这种情况发生，您可以使用 [`nohup`](https://www.man7.org/linux/man-pages/man1/nohup.1.html)（忽略 `SIGHUP` 的包装器）运行程序，或者如果进程已经启动，则使用 `disown`。或者，您可以使用终端多路复用器，我们将在下一节中看到。

下面是展示其中一些概念的示例会话。

```
$ sleep 1000
^Z
[1]  + 18653 suspended  sleep 1000

$ nohup sleep 2000 &
[2] 18745
appending output to nohup.out

$ jobs
[1]  + suspended  sleep 1000
[2]  - running    nohup sleep 2000

$ kill -SIGHUP %1
[1]  + 18653 hangup     sleep 1000

$ kill -SIGHUP %2   # nohup protects from SIGHUP

$ jobs
[2]  + running    nohup sleep 2000

$ kill %2
[2]  + 18745 terminated  nohup sleep 2000
```

一个特殊的信号是 `SIGKILL`，因为它不能被进程捕获，并且它总是会立即终止它。但是，它可能会产生严重的副作用，例如留下孤儿进程。

您可以了解有关这些信号和其他信号（[这里](https://en.wikipedia.org/wiki/Signal_(IPC)）的更多信息，或者输入 [`man signal`](https://www.man7.org/linux/man-pages/man7/signal.7.html) 或 `kill -l`。

在 shell 脚本中，您可以使用内置的 `trap` 在收到信号时执行命令。这对于清理操作很有用：

```shell
#!/usr/bin/env bash
cleanup() {
    echo "Cleaning up temporary files..."
    rm -f /tmp/mytemp.*
}
trap cleanup EXIT  # Run cleanup when script exits
trap cleanup SIGINT SIGTERM  # Also on Ctrl-C or kill
```

(command-line-environment-remote-machines)=
## 远程机器

程序员在日常工作中使用远程服务器已经变得越来越普遍。这里最常用的工具是 SSH（安全 Shell），它将帮助我们连接到远程服务器并提供现在熟悉的 shell 界面。我们使用如下命令连接到服务器：

```bash
ssh alice@server.mit.edu
```

在这里，我们尝试以用户 `alice` 的身份在服务器 `server.mit.edu` 中进行 ssh。

`ssh` 的一个经常被忽视的功能是能够以非交互方式运行命令。 `ssh` 正确处理发送命令的 stdin 和接收命令的 stdout，因此我们可以将其与其他命令结合起来

```shell
# 这里 ls 在远程运行，wc 在本地运行
ssh alice@server ls | wc -l

# 这里 ls 和 wc 都在服务器中运行
ssh alice@server 'ls | wc -l'

```

> 尝试安装 [Mosh](https://mosh.org/) 作为 SSH 替代品，它可以处理断开连接、进入/退出睡眠、更改网络和处理高延迟链接。

为了使 `ssh` 让我们在远程服务器中运行命令，我们需要证明我们有权这样做。我们可以通过密码或 ssh 密钥来完成此操作。基于密钥的身份验证利用公钥加密技术向服务器证明客户端拥有秘密私钥，而无需泄露密钥。基于密钥的身份验证既更方便又更安全，因此您应该更喜欢它。请注意，私钥（通常是 `~/.ssh/id_rsa`，最近是 `~/.ssh/id_ed25519`）实际上是您的密码，因此请像这样对待它，并且永远不要共享其内容。

要生成一对，您可以运行 [`ssh-keygen`](https://www.man7.org/linux/man-pages/man1/ssh-keygen.1.html)。
```bash
ssh-keygen -a 100 -t ed25519 -f ~/.ssh/id_ed25519
```

如果您曾经配置过使用 SSH 密钥推送到 GitHub，那么您可能已经完成了 [这里](https://help.github.com/articles/connecting-to-github-with-ssh/) 概述的步骤，并且已经拥有有效的密钥对。要检查您是否有密码并验证它，您可以运行 `ssh-keygen -y -f /path/to/key`。

在服务器端，`ssh` 将查看 `.ssh/authorized_keys` 以确定应该允许哪些客户端进入。要复制公钥，您可以使用：

```bash
cat .ssh/id_ed25519.pub | ssh alice@remote 'cat >> ~/.ssh/authorized_keys'

# 或者更简单（如果 ssh-copy-id 可用）

ssh-copy-id -i .ssh/id_ed25519 alice@remote
```

除了运行命令之外，ssh 建立的连接还可用于安全地与服务器传输文件。 [`scp`](https://www.man7.org/linux/man-pages/man1/scp.1.html) 是最传统的工具，语法为 `scp path/to/local_file remote_host:path/to/remote_file`。 [`rsync`](https://www.man7.org/linux/man-pages/man1/rsync.1.html) 通过检测本地和远程中的相同文件并防止再次复制它们，对 `scp` 进行了改进。它还提供对符号链接、权限的更细粒度的控制，并具有额外的功能，例如可以从先前中断的副本中恢复的 `--partial` 标志。 `rsync` 的语法与 `scp` 类似。

SSH 客户端配置位于 `~/.ssh/config`，它允许我们声明主机并为其设置默认设置。此配置文件不仅可以由 `ssh` 读取，还可以由其他程序（例如 `scp`、`rsync`、`mosh` 等）读取。

```bash
Host vm
    User alice
    HostName 172.16.174.141
    Port 2222
    IdentityFile ~/.ssh/id_ed25519

# 配置也可以使用通配符
Host *.mit.edu
    User alice
```




(command-line-environment-terminal-multiplexers)=
## 终端多路复用器

使用命令行界面时，您通常会希望一次运行多个操作。例如，您可能希望并行运行编辑器和程序。尽管这可以通过打开新的终端窗口来实现，但使用终端多路复用器是一种更通用的解决方案。

[`tmux`](https://www.man7.org/linux/man-pages/man1/tmux.1.html) 等终端多路复用器允许您使用窗格和选项卡多路复用终端窗口，以便您可以高效地与多个 shell 会话进行交互。此外，终端多路复用器允许您分离当前的终端会话并在稍后的某个时间点重新连接。因此，终端多路复用器在使用远程机器时非常方便，因为它避免了使用 `nohup` 和类似技巧的需要。

目前最流行的终端多路复用器是 [`tmux`](https://www.man7.org/linux/man-pages/man1/tmux.1.html)。 `tmux` 具有高度可配置性，通过使用关联的键绑定，您可以创建多个选项卡和窗格并快速浏览它们。

`tmux` 希望您知道其键绑定，它们都具有 `<C-b> x` 的形式，这意味着 (1) 按 `Ctrl+b`，(2) 释放 `Ctrl+b`，然后 (3) 按 `x`。 `tmux` 具有以下对象层次结构：
- **会话** - 会话是具有一个或多个窗口的独立工作区
    + `tmux` 启动新会话。
    + `tmux new -s NAME` 以该名称开头。
    + `tmux ls` 列出当前会话
    + 在 `tmux` 中输入 `<C-b> d` 会分离当前会话
    + `tmux a` 附加最后一个会话。您可以使用 `-t` 标志来指定

- **Windows** - 相当于编辑器或浏览器中的选项卡，它们在视觉上是同一会话的独立部分
    + `<C-b> c` 创建一个新窗口。要关闭它，您只需终止 shell 执行 `<C-d>`
    + `<C-b> N` 转到第 _N_ 个窗口。请注意它们已编号
    + `<C-b> p` 转到上一个窗口
    + `<C-b> n` 转到下一个窗口
    + `<C-b> ,` 重命名当前窗口
    + `<C-b> w` 列出当前窗口

- **窗格** - 与 vim 分割一样，窗格允许您在同一视觉显示中拥有多个 shell。
    + `<C-b> "` 水平分割当前窗格
    + `<C-b> %` 垂直分割当前窗格
    + `<C-b> <direction>` 移至指定方向的窗格。这里的方向指的是方向键。
    + `<C-b> z` 切换当前窗格的缩放
    + `<C-b> [` 开始回滚。然后，您可以按 `<space>` 开始选择，然后按 `<enter>` 复制该选择。
    + `<C-b> <space>` 循环浏览窗格排列。

> 要了解有关 tmux 的更多信息，请考虑阅读 [这个](https://www.hamvocke.com/blog/a-quick-and-easy-guide-to-tmux/) 快速教程和 [这个](https://linuxcommand.org/lc3_adv_termmux.php) 更详细的解释。

通过工具包中的 tmux 和 SSH，您将希望让您的环境在任何计算机上都感觉像在家一样。这就是 shell 定制的用武之地。

(command-line-environment-customizing-the-shell)=
## 定制 Shell

大量命令行程序使用称为 _dotfiles_ 的纯文本文件进行配置（因为文件名以 `.` 开头，例如 `~/.vimrc`，因此默认情况下它们隐藏在列出 `ls` 的目录中）。

> dotfiles是另一种 shell 约定。前面的点是在列出时“隐藏”它们（是的，另一个约定）。

Shell 是使用此类文件配置的程序的示例之一。启动时，您的 shell 将读取许多文件来加载其配置。根据 shell 以及您是否启动登录和/或交互式会话，整个过程可能非常复杂。 [这里](https://web.archive.org/web/20260329133158/https://blog.flowblok.id.au/2013-02/shell-startup-scripts.html) 是有关该主题的优秀资源。

对于 `bash`，编辑 `.bashrc` 或 `.bash_profile` 适用于大多数系统。可以通过dotfiles配置的其他一些工具示例包括：

- `bash` - `~/.bashrc`、`~/.bash_profile`
- `git` - `~/.gitconfig`
- `vim` - `~/.vimrc` 和 `~/.vim` 文件夹
- `ssh` - `~/.ssh/config`
- `tmux` - `~/.tmux.conf`

常见的配置更改是为 shell 添加新位置以查找程序。安装软件时你会遇到这种模式：

```shell
export PATH="$PATH:path/to/append"
```

在这里，我们告诉 shell 将 $PATH 变量的值设置为其当前值加上新路径，并让所有子进程继承这个新的 PATH 值。这将允许子进程找到位于 `path/to/append` 下的程序。


自定义 shell 通常意味着安装新的命令行工具。包管理器使这一切变得简单。他们负责下载、安装和更新软件。不同的操作系统有不同的包管理器：macOS使用[Homebrew](https://brew.sh/)，Ubuntu/Debian使用`apt`，Fedora使用`dnf`，Arch使用`pacman`。我们将在交付代码讲座中更深入地介绍包管理器。

以下是如何在 macOS 上使用 Homebrew 安装两个有用的工具：

```shell
# ripgrep：更快的 grep 和更好的默认值
brew install ripgrep

# fd：更快、用户友好的查找
brew install fd
```

安装这些后，您可以使用 `rg` 代替 `grep`，使用 `fd` 代替 `find`。

> **有关 `curl | bash` 的警告**：您经常会看到 `curl -fsSL https://example.com/install.sh | bash` 等安装说明。这种模式下载脚本并立即执行，方便但有风险；您正在运行尚未检查的代码。更安全的方法是先下载，查看，然后执行：
> ```shell
> curl -fsSL https://example.com/install.sh -o install.sh
> less install.sh  # 检查脚本
> bash install.sh
> ```
> 一些安装程序使用稍微更安全的变体：`/bin/bash -c "$(curl -fsSL https://url)"`，它至少确保 bash 解释脚本而不是当前的 shell。

当您尝试运行未安装的命令时，您的 shell 将显示 `command not found`。网站 [command-not-found.com](https://command-not-found.com) 是一个有用的资源，您可以使用它来搜索任何命令，以了解如何跨不同的包管理器和发行版安装它。

另一个有用的工具是 [`tldr`](https://tldr.sh/)，它提供了简化的、以示例为中心的手册页。您无需阅读冗长的文档，而是可以快速查看常见的使用模式：

```console
$ tldr fd
  An alternative to find.
  Aims to be faster and easier to use than find.

  Recursively find files matching a pattern in the current directory:
      fd "pattern"

  Find files that begin with "foo":
      fd "^foo"

  Find files with a specific extension:
      fd --extension txt
```

有时您不需要一个全新的程序，而只需要具有特定标志的现有命令的快捷方式。这就是别名的用武之地。

我们还可以使用内置的 `alias` shell 创建自己的命令别名。 shell 别名是另一个命令的缩写形式，shell 在计算表达式之前会自动替换该命令。例如，bash 中的别名具有以下结构：

```bash
alias alias_name="command_to_alias arg1 arg2"
```

> 请注意，等号 `=` 周围没有空格，因为 [`alias`](https://www.man7.org/linux/man-pages/man1/alias.1p.html) 是采用单个参数的 shell 命令。

别名有许多方便的功能：

```bash
# 为常用标志制作简写
alias ll="ls -lh"

# 节省大量输入常用命令的时间
alias gs="git status"
alias gc="git commit"

# 避免您输入错误
alias sl=ls

# 覆盖现有命令以获得更好的默认值
alias mv="mv -i"           # -i prompts before overwrite
alias mkdir="mkdir -p"     # -p make parent dirs as needed
alias df="df -h"           # -h prints human readable format

# 可以组成别名
alias la="ls -A"
alias lla="la -l"

# 要忽略别名，请运行它并在其前面加上 \
\ls
# 或者使用 unalias 完全禁用别名
unalias la

# 要获取别名定义，只需使用别名调用它
alias ll
# 将打印 ll='ls -lh'
```

别名有局限性：它们不能在命令中间接受参数。对于更复杂的行为，您应该使用 shell 函数。

大多数 shell 支持 `Ctrl-R` 进行反向历史搜索。输入 `Ctrl-R` 并开始输入以搜索以前的命令。之前我们介绍了 `fzf` 作为模糊查找器；配置了 fzf 的 shell 集成后，`Ctrl-R` 成为对整个历史记录的交互式模糊搜索，比默认的功能强大得多。

您应该如何组织dotfiles？它们应该位于自己的文件夹中，受版本控制，并使用脚本**符号链接**到位。这样做的好处是：

- **安装简单**：如果您登录到新机器，应用您的
定制只需要一分钟。
- **可移植性**：您的工具在任何地方都可以以相同的方式工作。
- **同步**：您可以在任何地方更新您的dotfiles并保留它们
同步。
- **更改跟踪**：您可能会维护您的dotfiles
对于你的整个编程生涯来说，版本历史对于长期项目来说是很好的。

您应该在dotfiles中放入什么？您可以通过阅读在线文档或 [手册页](https://en.wikipedia.org/wiki/Man_page) 了解工具的设置。另一个好方法是在互联网上搜索有关特定程序的博客文章，其中作者会告诉您他们喜欢的自定义设置。了解自定义的另一种方法是查看其他人的dotfiles：您可以在 GitHub 上找到大量 [dotfiles仓库](https://github.com/search?o=desc&q=dotfiles&s=stars&type=Repositories) --- 查看最流行的 [这里](https://github.com/mathiasbynens/dotfiles)（不过我们建议您不要盲目复制配置）。 [这里](https://dotfiles.github.io/) 是关于该主题的另一个很好的资源。

所有课程讲师的dotfiles均可在 GitHub 上公开访问：[Anish](https://github.com/anishathalye/dotfiles)、[Jon](https://github.com/jonhoo/configs)、[Jose](https://github.com/jjgo/dotfiles)。

**框架和插件**也可以改进您的 shell。一些流行的通用框架是 [Prezto](https://github.com/sorin-ionescu/prezto) 或 [Oh My Zsh](https://ohmyz.sh/)，以及专注于特定功能的较小插件：

- [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting) - 输入时用颜色显示有效/无效命令
- [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions) - 在您键入时建议历史命令
- [zsh-completions](https://github.com/zsh-users/zsh-completions) - 附加完成定义
- [zsh-history-substring-search](https://github.com/zsh-users/zsh-history-substring-search) - 类似鱼的历史搜索
- [powerlevel10k](https://github.com/romkatv/powerlevel10k) - 快速、可定制的提示主题

像 [fish](https://fishshell.com/) 这样的 shell 默认包含许多这样的功能。

> 您不需要像 oh-my-zsh 这样的大型框架来获得这些功能。安装单独的插件通常更快，并且给您更多的控制权。大型框架会显着减慢 shell 启动时间，因此请考虑仅安装您实际使用的框架。


(command-line-environment-ai-in-the-shell)=
## Shell 中的 AI

将 AI 工具整合到 shell 中的方法有很多。以下是不同集成级别的几个示例：

**命令生成**：[`simonw/llm`](https://github.com/simonw/llm) 等工具可以帮助从自然语言描述生成 shell 命令：

```console
$ llm cmd "find all python files modified in the last week"
find . -name "*.py" -mtime -7
```

**管道集成**：LLM 可以集成到 shell 管道中以处理和转换数据。当您需要从不一致的格式中提取信息时，它们特别有用，而正则表达式会很痛苦：

```console
$ cat users.txt
Contact: john.doe@example.com
User 'alice_smith' logged in at 3pm
Posted by: @bob_jones on Twitter
Author: Jane Doe (jdoe)
Message from mike_wilson yesterday
Submitted by user: sarah.connor
$ INSTRUCTIONS="Extract just the username from each line, one per line, nothing else"
$ llm "$INSTRUCTIONS" < users.txt
john.doe
alice_smith
bob_jones
jdoe
mike_wilson
sarah.connor
```

请注意我们如何使用 `"$INSTRUCTIONS"`（带引号），因为变量包含空格，并使用 `< users.txt` 将文件内容重定向到标准输入。

**AI shell**：像 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 这样的工具充当元 shell，接受英语命令并将其转换为 shell 操作、文件编辑和更复杂的多步骤任务。

(command-line-environment-terminal-emulators)=
## 终端模拟器

除了自定义您的 shell 之外，还值得花一些时间来确定您选择的 **终端模拟器** 及其设置。终端模拟器是一个 GUI 程序，它提供运行 shell 的基于文本的界面。有很多终端模拟器。

由于您可能会在终端上花费数百至数千小时，因此检查其设置是值得的。您可能想要在终端中修改的一些方面包括：

- 字体选择
- 配色方案
- 键盘快捷键
- 选项卡/窗格支持
- 回滚配置
- 性能（一些较新的终端，如 [Alacritty](https://github.com/alacritty/alacritty) 或 [Ghostty](https://ghostty.org/) 提供 GPU 加速）。

### Exercises

以下题目对应[官方练习](https://missing.csail.mit.edu/2026/command-line-environment/#exercises)。部分开放题的“答案”是验收标准与安全做法，而不是唯一命令。

```{exercise} 参数分隔符
:label: exercise-cli-double-dash

运行 `touch -- -myfile`，再尝试删除它。解释 `--` 为什么有用。
```

```{solution} exercise-cli-double-dash
:class: dropdown

`rm -myfile` 会把文件名误作选项；使用 `rm -- -myfile`，或明确路径 `rm ./-myfile`。`--` 告诉遵循该约定的程序停止解析选项。
```

```{exercise} 组合 ls 选项
:label: exercise-cli-ls-flags

列出全部文件，采用长格式和易读大小，按修改时间从新到旧排序，并启用颜色。
```

```{solution} exercise-cli-ls-flags
:class: dropdown

GNU/Linux 可用 `ls -lath --color=auto`；macOS 的 BSD `ls` 可用 `ls -lathG`。`-a -l -t -h` 分别对应全部、长格式、按时间、易读大小。
```

```{exercise} 比较环境与导出变量
:label: exercise-cli-printenv-export

运行 `diff <(printenv | sort) <(export | sort)`，解释差异。
```

```{solution} exercise-cli-printenv-export
:class: dropdown

`printenv` 只显示当前进程要传给子进程的环境；Bash 的 `export` 还以可重新输入的 Shell 语法显示已导出名称，格式和 quoting 不同。Shell 中未导出的局部变量不会出现在二者的环境值中。
```

```{exercise} Marco Polo
:label: exercise-cli-marco-polo

编写 Bash 函数 `marco` 保存当前目录，`polo` 从任意位置返回该目录。
```

````{solution} exercise-cli-marco-polo
:class: dropdown

```bash
marco() { MARCO_DIR=$PWD; }
polo() {
  [[ -n ${MARCO_DIR:-} ]] || { echo '请先运行 marco' >&2; return 1; }
  cd -- "$MARCO_DIR"
}
```

用 `source marco.sh` 加载，函数必须在当前 Shell 中运行，才能让 `cd` 生效。
````

```{exercise} 捕获偶发失败
:label: exercise-cli-rare-failure

反复运行官方给出的随机失败脚本，分别捕获 stdout、stderr，并在失败时输出日志与运行次数。
```

````{solution} exercise-cli-rare-failure
:class: dropdown

```bash
#!/usr/bin/env bash
count=0
while true; do
  ((count += 1))
  if ./random.sh >stdout.log 2>stderr.log; then
    continue
  fi
  status=$?
  printf '第 %d 次失败，退出码 %d\n' "$count" "$status"
  cat stdout.log stderr.log
  break
done
```

不要用未初始化的 `$?` 控制第一次循环；应直接把被测命令放进 `if`。
````

```{exercise} 作业控制
:label: exercise-cli-job-control

启动 `sleep 10000`，用 `Ctrl-Z` 暂停、`bg` 恢复，再用 `pgrep -lf` 查找并用 `pkill` 终止，全程不要手输 PID。
```

```{solution} exercise-cli-job-control
:class: dropdown

执行 `pgrep -lf 'sleep 10000'` 核对匹配范围，再运行 `pkill -f '^sleep 10000$'`。宽泛的 `pkill sleep` 可能误杀别人的任务，因此先查后杀并尽量收紧模式。
```

```{exercise} 等待任意 PID
:label: exercise-cli-pidwait

先用 `wait` 让 `ls` 等待 `sleep 60 &`。再编写 `pidwait PID`，使用 `kill -0` 等待非子进程结束，并避免忙等。
```

````{solution} exercise-cli-pidwait
:class: dropdown

```bash
sleep 60 & pid=$!
wait "$pid" && ls

pidwait() {
  while kill -0 "$1" 2>/dev/null; do sleep 1; done
}
```

`kill -0` 只检查进程是否存在/可访问。PID 可能被复用；严谨工具还应核对进程启动时间或使用 pidfd 等平台能力。
````

```{exercise} 按修改时间列出文件
:label: exercise-cli-recent-files

递归找出目录中最新修改的文件，并推广为按时间排列全部文件。
```

```{solution} exercise-cli-recent-files
:class: dropdown

GNU 工具：`find . -type f -printf '%T@ %p\0' | sort -z -nr | tr '\0' '\n'`，首行最新。若文件名可含换行，不要用最后的 `tr`；交给支持 NUL 的后续程序处理。
```

```{exercise} tmux 入门
:label: exercise-cli-tmux

完成官方链接的 tmux 教程，并至少自定义一个按键或状态栏设置。
```

```{solution} exercise-cli-tmux
:class: dropdown

验收：能创建命名会话和两个窗格，`Ctrl-b d` 脱离后用 `tmux attach -t NAME` 恢复；把自定义写入 `~/.tmux.conf`，再用 `tmux source-file ~/.tmux.conf` 重载。
```

```{exercise} 修正 dc 手误
:label: exercise-cli-alias-dc

创建别名 `dc`，使其等价于 `cd`。
```

```{solution} exercise-cli-alias-dc
:class: dropdown

在 `~/.bashrc` 或 `~/.zshrc` 中加入 `alias dc=cd`，然后重新打开 Shell 或 `source` 对应文件。
```

```{exercise} 从历史记录设计别名
:label: exercise-cli-history-alias

统计最常使用的十条命令，并为确实高频且不危险的命令设计缩写。
```

```{solution} exercise-cli-history-alias
:class: dropdown

Bash 使用官方命令；Zsh 把开头改成 `history 1`。优先缩短只读命令，例如 `alias gs='git status'`；不要为 `rm -rf` 等破坏性组合创建隐蔽别名。
```

```{exercise} 建立 dotfiles 仓库
:label: exercise-cli-dotfiles-repo

创建 dotfiles 目录并启用版本控制。
```

```{solution} exercise-cli-dotfiles-repo
:class: dropdown

`mkdir -p ~/dotfiles && git -C ~/dotfiles init`。添加 README，说明支持的平台、安装方式和备份策略；秘密、机器专属缓存与私钥必须放入 `.gitignore`。
```

```{exercise} 添加一项配置
:label: exercise-cli-dotfiles-config

把至少一个程序的可见自定义加入仓库，例如提示符或 Git 别名。
```

```{solution} exercise-cli-dotfiles-config
:class: dropdown

可把 `export PS1='\u@\h:\w\$ '` 写入仓库中的 `bashrc`。先在当前会话验证，再由安装脚本链接到 `~/.bashrc`，不要直接覆盖已有文件。
```

```{exercise} 自动安装 dotfiles
:label: exercise-cli-dotfiles-install

编写可重复运行的安装方法，用符号链接或专用工具部署配置。
```

```{solution} exercise-cli-dotfiles-install
:class: dropdown

脚本应先备份冲突文件，再用 `ln -sfn "$repo/bashrc" "$HOME/.bashrc"` 等显式映射创建链接；第二次执行不能报错或生成重复内容。可选工具有 GNU Stow、chezmoi 与 yadm。
```

```{exercise} 在干净系统测试
:label: exercise-cli-dotfiles-clean-test

在新虚拟机或容器中测试安装脚本。
```

```{solution} exercise-cli-dotfiles-clean-test
:class: dropdown

验收至少包括：首次安装成功、重复安装成功、缺少可选程序时给出清晰提示、打开新 Shell 无错误。容器无法完整模拟桌面和 systemd，最终仍应在一次干净 VM 中验证。
```

```{exercise} 迁移现有配置
:label: exercise-cli-dotfiles-migrate

把当前使用的工具配置逐步迁入仓库。
```

```{solution} exercise-cli-dotfiles-migrate
:class: dropdown

按“一个工具一个提交”迁移，每次先备份、链接并重启工具验证。将主机差异放入未跟踪的 `local.*` 文件，再由公共配置条件加载。
```

```{exercise} 发布 dotfiles
:label: exercise-cli-dotfiles-publish

把清理后的 dotfiles 发布到 GitHub。
```

```{solution} exercise-cli-dotfiles-publish
:class: dropdown

发布前运行秘密扫描并人工检查历史，尤其是 `.ssh`、云凭据、Cookie、访问令牌与公司内网地址。秘密一旦进入 Git 历史，仅在最新提交删除并不足够，还必须撤销并轮换凭据。
```

```{exercise} 生成 SSH 密钥
:label: exercise-cli-ssh-key

检查 `~/.ssh/`；若没有密钥，运行 `ssh-keygen -a 100 -t ed25519`，设置口令并使用 `ssh-agent`。
```

```{solution} exercise-cli-ssh-key
:class: dropdown

私钥通常为 `~/.ssh/id_ed25519`，权限应为 600，绝不能复制到服务器或提交仓库；`.pub` 公钥可分发。`ssh-add ~/.ssh/id_ed25519` 把解密后的使用权交给当前 agent 会话。
```

```{exercise} 编写 SSH 配置
:label: exercise-cli-ssh-config

在 `~/.ssh/config` 中配置别名 `vm`、用户名、地址、密钥，并把本机 9999 转发到远端 8888。
```

````{solution} exercise-cli-ssh-config
:class: dropdown

```text
Host vm
    User username_goes_here
    HostName ip_goes_here
    IdentityFile ~/.ssh/id_ed25519
    LocalForward 9999 localhost:8888
```

运行 `ssh -G vm` 可查看合并后的最终配置；`chmod 600 ~/.ssh/config`。
````

```{exercise} 安装公钥
:label: exercise-cli-ssh-copy-id

使用 `ssh-copy-id vm` 把公钥加入服务器。
```

```{solution} exercise-cli-ssh-copy-id
:class: dropdown

先保留一个已登录的备用会话，再开新终端运行 `ssh vm` 验证公钥认证。确认成功前不要关闭密码登录，否则可能把自己锁在服务器外。
```

```{exercise} 测试本地端口转发
:label: exercise-cli-ssh-forward

在 VM 执行 `python -m http.server 8888`，从本机访问 `http://localhost:9999`。
```

```{solution} exercise-cli-ssh-forward
:class: dropdown

保持 SSH 会话运行，并在本机执行 `curl -I http://localhost:9999`。请求经加密隧道到达远端视角的 `localhost:8888`，无需把 8888 暴露给外网。
```

```{exercise} 加固 SSH 服务
:label: exercise-cli-ssh-hardening

确认密钥登录可用后，禁用密码认证与 root 登录，重启服务并再次连接。
```

```{solution} exercise-cli-ssh-hardening
:class: dropdown

先运行 `sudo sshd -t` 校验配置，再 reload/restart。设置通常是 `PasswordAuthentication no` 与 `PermitRootLogin no`；不同发行版服务名可能是 `ssh` 或 `sshd`。始终保留备用会话以便回滚。
```

```{exercise} 体验 mosh
:label: exercise-cli-mosh

安装 mosh，连接 VM 后短暂断网，观察网络恢复后的会话。
```

```{solution} exercise-cli-mosh
:class: dropdown

mosh 会在客户端本地回显并在网络恢复后同步状态，通常能从漫游或断网中恢复；它需要服务器安装 mosh，并允许相应 UDP 端口，且不替代 SSH 的认证与初始连接。
```

```{exercise} 后台端口转发
:label: exercise-cli-ssh-background-forward

调查 SSH 的 `-N` 与 `-f`，建立后台本地端口转发。
```

```{solution} exercise-cli-ssh-background-forward
:class: dropdown

`ssh -fN -L 9999:localhost:8888 vm`：`-N` 不执行远程命令，`-f` 在认证后进入后台。调试时先去掉 `-f` 并加 `-v`；长期隧道可配 `ExitOnForwardFailure yes` 并交给服务管理器监督。
```

### 许可与署名

本页依据 MIT Missing Semester 2026 第二讲[官方 notes](https://missing.csail.mit.edu/2026/command-line-environment/)整理，原材料采用 [CC BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可。
