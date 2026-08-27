# 第四讲：调试与性能分析

> 官方 notes：[https://missing.csail.mit.edu/2026/debugging-profiling/](https://missing.csail.mit.edu/2026/debugging-profiling/)  
> 视频：[YouTube](https://www.youtube.com/watch?v=8VYT9TcUmKs)

```{note}
本文依照 Missing Semester 2026 官方 notes 的原文结构完整翻译；保留标题层级、命令示例、工具链接、引用与提示。练习采用 MyST exercise，并在官方题目之外补充折叠参考答案。
```


编程的一条黄金法则是，代码不会做你期望它做的事情，而是做你告诉它做的事情。弥合这一差距有时可能是一项相当困难的壮举。在本次讲座中，我们将介绍处理有错误和资源匮乏的代码的有用技术：调试和分析。

(debugging-profiling-debugging)=
## 调试

(debugging-profiling-printf-debugging-and-logging)=
### Printf 调试和日志记录

> “最有效的调试工具仍然是仔细的思考，加上明智地放置打印语句”——Brian Kernighan，_Unix for Beginners_。

调试程序的第一种方法是在检测到问题的位置添加打印语句，并不断迭代，直到提取足够的信息以了解导致问题的原因。

第二种方法是在程序中使用日志记录，而不是临时打印语句。日志记录本质上是“更加小心地打印”，通常通过日志记录框架完成，该框架包括对以下内容的内置支持：

- 将日志（或日志子集）定向到其他输出位置的能力；
- 设置严重性级别（例如 INFO、DEBUG、WARN、ERROR 等）并允许您根据这些级别过滤输出；和
- 支持对与日志条目相关的数据进行结构化记录，事后可以更轻松地提取这些数据。

您通常还会在编程时主动放入日志语句，以便调试所需的数据可能已经存在！事实上，一旦您使用打印语句发现并解决了问题，通常值得在删除这些打印之前将它们转换为正确的日志语句。这样，如果将来出现类似的错误，您无需修改​​代码即可获得所需的诊断信息。

> **第三方日志**：许多程序支持 `-v` 或 `--verbose` 标志以在运行时打印更多信息。这对于发现给定命令失败的原因非常有用。有些甚至允许重复该标志以获取更多详细信息。调试服务（数据库、Web 服务器等）问题时，请检查其日志 — 通常在 Linux 上的 `/var/log/` 中。使用 `journalctl -u <service>` 查看 systemd 服务的日志。对于第三方库，检查它们是否支持通过环境变量或配置进行调试日志记录。

(debugging-profiling-debuggers)=
### 调试器

当您知道要打印什么并且可以轻松修改和重新运行代码时，打印调试效果很好。当您不确定需要什么信息时，当错误仅在难以重现的情况下出现时，或者当修改和重新启动程序成本高昂（启动时间长、重新创建的状态复杂等）时，调试器就变得很有价值。

调试器是一种程序，可让您在程序执行时与其进行交互，从而使您能够：

- 当到达某一行时停止执行。
- 一次逐步执行一项指令。
- 崩溃后检查变量的值。
- 当满足给定条件时有条件地停止执行。
- 以及许多更高级的功能。

大多数编程语言都支持（或附带）某种形式的调试器。最通用的是**通用调试器**，例如 [`gdb`](https://www.gnu.org/software/gdb/)（GNU 调试器）和 [`lldb`](https://lldb.llvm.org/)（LLVM 调试器），它们可以调试任何本机二进制文件。许多语言还具有**特定于语言的调试器**，它们与运行时集成更紧密（例如 Python 的 pdb 或 Java 的 jdb）。

`gdb` 是 C、C++、Rust 和其他编译语言事实上的标准调试器。它可以让您探测几乎任何进程并获取其当前的机器状态：寄存器、堆栈、程序计数器等等。

一些有用的 GDB 命令：

- `run` - 启动程序
- `b {function}` 或 `b {file}:{line}` - 设置断点
- `c` - 继续执行
- `step` / `next` / `finish` - 步入/跨过/走出
- `p {variable}` - 打印变量值
- `bt` - 显示回溯（调用堆栈）
- `watch {expression}` - 值更改时中断

> 考虑使用 GDB 的 TUI 模式（`gdb -tui` 或在 GDB 内按 `Ctrl-x a`）以获得在命令提示符旁边显示源代码的分屏视图。

(debugging-profiling-record-replay-debugging)=
#### 记录重放调试

一些最令人沮丧的错误是_Heisenbugs_：当您尝试观察它们时，这些错误似乎会消失或改变行为。竞争条件、与时间相关的错误以及仅在某些系统条件下出现的问题都属于这一类。传统的调试在这里通常是无用的，因为再次运行程序会产生不同的行为（例如，打印语句可能会充分减慢代码速度，从而不再发生竞争）。

**记录重放调试** 通过记录程序的执行并允许您根据需要多次确定地重放它来解决这个问题。更好的是，您可以“反向”执行，以准确找到出错的地方。

[RR](https://rr-project.org/) 是一款强大的 Linux 工具，可记录程序执行情况并允许确定性重放并具有完整的调试功能。它与 GDB 一起使用，因此您已经了解该接口。

基本用法：

```bash
# 记录程序执行情况
rr record ./my_program

# 重播录音（打开 GDB）
rr replay
```

奇迹发生在重播期间。由于执行是确定性的，因此可以使用**反向调试**命令：

- `reverse-continue` (`rc`) - 向后运行直到遇到断点
- `reverse-step` (`rs`) - 后退一行
- `reverse-next` (`rn`) - 后退一步，跳过函数调用
- `reverse-finish` - 向后运行直到进入当前函数

这对于调试来说非常强大。假设您发生了崩溃，您可以：而不是猜测错误在哪里并设置断点：

1. 跑到崩溃处
2. 检查损坏的状态
3. 在损坏的变量上设置观察点
4. `reverse-continue` 准确查找损坏的位置

**何时使用 rr:**
- 间歇性失败的片状测试
- 竞争条件和线程错误
- 难以重现的崩溃
- 任何你希望“回到过去”的错误

> 注意：rr 仅适用于 Linux，并且需要硬件性能计数器。它不适用于不公开这些计数器的虚拟机（例如大多数 AWS EC2 实例），并且不支持 GPU 访问。对于 macOS，请查看 [Warp](https://warpspeed.dev/)。

> **rr 和并发性**：因为 rr 确定性地记录执行，所以它串行化线程调度。这意味着如果某些竞争条件取决于特定的时间，则它们可能不会在 rr 下显现。 rr 对于调试竞赛仍然有用 - 一旦捕获失败的运行，您就可以可靠地重放它 - 但您可能需要多次记录尝试才能捕获间歇性错误。对于不涉及并发的错误，rr 表现最出色：您始终可以重现确切的执行情况并使用反向调试来查找损坏。

(debugging-profiling-system-call-tracing)=
### 系统调用追踪

有时您需要了解程序如何与操作系统交互。程序使 [系统调用](https://en.wikipedia.org/wiki/System_call) 向内核请求服务——打开文件、分配内存、创建进程等等。跟踪这些调用可以揭示程序挂起的原因、它试图访问哪些文件，或者它在哪里等待。

(debugging-profiling-strace-linux-and-dtruss-macos)=
#### strace (Linux) 和 dtruss (macOS)

[`strace`](https://www.man7.org/linux/man-pages/man1/strace.1.html) 可让您观察程序进行的每个系统调用：

```bash
# 跟踪所有系统调用
strace ./my_program

# 仅跟踪与文件相关的调用
strace -e trace=file ./my_program

# 跟踪子进程（对于启动其他程序的程序很重要）
strace -f ./my_program

# 跟踪正在运行的进程
strace -p <PID>

# 显示计时信息
strace -T ./my_program
```

> 在 macOS 和 BSD 上，使用 [`dtruss`](https://www.manpagez.com/man/1/dtruss/)（包装 `dtrace`）来实现类似的功能：

> 要更深入地了解 `strace`，请查看 Julia Evans 的精彩 [strace 小册子](https://jvns.ca/strace-zine-unfolded.pdf)。

(debugging-profiling-bpftrace-and-ebpf)=
#### bpftrace 和 eBPF

[eBPF](https://ebpf.io/)（扩展伯克利数据包过滤器）是一项强大的 Linux 技术，允许在内核中运行沙盒程序。 [`bpftrace`](https://github.com/iovisor/bpftrace) 提供了用于编写 eBPF 程序的高级语法。这些是在内核中运行的任意程序，因此具有巨大的表达能力（尽管也是有点笨拙的类似 awk 的语法）。它们最常见的用例是调查正在调用哪些系统调用，包括聚合（如计数或延迟统计）或内省（甚至过滤）系统调用参数。

```bash
# 跟踪文件在系统范围内打开（立即打印）
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf("%s %s\n", comm, str(args->filename)); }'

# 按名称对系统调用进行计数（按 Ctrl-C 打印摘要）
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_* { @[probe] = count(); }'
```

但是，您也可以使用 [`bcc`](https://github.com/iovisor/bcc) 等工具链直接用 C 语言编写 eBPF 程序，该工具链还附带 [许多方便的工具](https://www.brendangregg.com/blog/2015-09-22/bcc-linux-4.3-tracing.html)，例如用于打印磁盘操作延迟分布的 `biosnoop` 或用于打印所有打开文件的 `opensnoop`。

`strace` 很有用，因为它很容易“启动并运行”，而 `bpftrace` 是当您需要较低开销、想要跟踪内核函数、需要进行任何类型的聚合等时应该使用的。请注意，`bpftrace` 必须作为 `root` 运行，并且它通常监视整个内核，而不仅仅是特定进程。要定位特定程序，您可以按命令名称或 PID 进行过滤：

```bash
# 按命令名称过滤（按 Ctrl-C 打印摘要）
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_* /comm == "bash"/ { @[probe] = count(); }'

# 使用 -c (cpid = 子 PID) 从启动时跟踪特定命令
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_* /pid == cpid/ { @[probe] = count(); }' -c 'ls -la'
```

`-c` 标志运行指定的命令并将 `cpid` 设置为其 PID，这对于从程序启动的那一刻起跟踪程序很有用。当跟踪命令退出时，bpftrace 会打印聚合结果。

(debugging-profiling-network-debugging)=
#### 网络调试

对于网络问题，[`tcpdump`](https://www.man7.org/linux/man-pages/man1/tcpdump.1.html) 和 [Wireshark](https://www.wireshark.org/) 可让您捕获和分析网络数据包：

```bash
# 80端口抓包
sudo tcpdump -i any port 80

# 捕获并保存到文件以供 Wireshark 分析
sudo tcpdump -i any -w capture.pcap
```

对于 HTTPS 流量，加密会降低 tcpdump 的用处。 [mitmproxy](https://mitmproxy.org/) 等工具可以充当拦截代理来检查加密流量。浏览器开发人员工具（“网络”选项卡）通常是调试来自 Web 应用程序的 HTTPS 请求的最简单方法 - 它们显示解密的请求/响应数据、标头和计时。

(debugging-profiling-memory-debugging)=
### 内存调试

内存错误（缓冲区溢出、释放后使用、内存泄漏）是最危险且最难调试的错误。它们通常不会立即崩溃，但会以稍后导致问题的方式破坏内存。

(debugging-profiling-sanitizers)=
#### Sanitizer

查找内存错误的一种方法是使用**清理程序**，它们是编译器功能，可在运行时检测代码以检测错误。例如，广泛使用的 **AddressSanitizer (ASan)** 检测：
- 缓冲区溢出（堆栈、堆和全局）
- 释放后使用
- 归还后使用
- 内存泄漏

```bash
# 使用 AddressSanitizer 进行编译
gcc -fsanitize=address -g program.c -o program
./program
```

有多种有用的Sanitizer：

- **ThreadSanitizer (TSan)**：检测多线程代码中的数据争用 (`-fsanitize=thread`)
- **MemorySanitizer (MSan)**：检测未初始化内存的读取 (`-fsanitize=memory`)
- **UndefinedBehaviorSanitizer (UBSan)**：检测未定义的行为，例如整数溢出 (`-fsanitize=undefined`)

Sanitizers 需要重新编译，但速度足够快，可以在 CI 管道和常规开发过程中使用。

(debugging-profiling-valgrind-when-you-cant-recompile)=
#### Valgrind：当你无法重新编译时

[Valgrind](https://valgrind.org/) 相反，在类似于虚拟机的环境中运行您的程序来检测内存错误。它比Sanitizer慢，但不需要重新编译：

```bash
valgrind --leak-check=full ./my_program
```

在以下情况下使用 Valgrind：
- 你没有源代码
- 无法重新编译（第三方库）
- 您需要无法用作Sanitizer的特定工具

Valgrind 实际上是一个非常强大的受控执行环境，稍后当我们进行分析时我们会看到更多它！

(debugging-profiling-ai-for-debugging)=
### 人工智能调试

大型语言模型已成为非常有用的调试助手。他们擅长某些与传统工具相辅相成的调试任务。

**LLM的闪光点：**

- **解释神秘的错误消息**：编译器错误，尤其是来自 C++ 模板或 Rust 的借用检查器的错误，可能非常神秘。LLM可以将它们翻译成通俗语言并提出修复建议。

- **穿越语言和抽象边界**：如果您正在调试跨多种语言的问题（例如，C 库中通过 Python 绑定体现的错误），LLM 可以帮助导航不同的层。他们特别擅长理解 FFI 边界、构建系统问题和跨语言调试（例如，我的程序错误，但我相信这是因为我的依赖项之一中的错误）。

- **将症状与根本原因相关联**：“我的程序运行良好，但使用的内存比预期多 10 倍”是LLM可以帮助调查的一种模糊症状，建议可能的原因以及要查找的内容。

- **分析故障转储和堆栈跟踪**：粘贴堆栈跟踪并询问可能导致它的原因。

> **有关调试符号的注意事项**：为了获得有意义的堆栈跟踪和调试，请确保使用调试符号（`-g` 标志）编译二进制文件（以及任何链接库）。调试信息通常以 DWARF 格式存储。此外，使用帧指针 (`-fno-omit-frame-pointer`) 进行编译使堆栈跟踪更加可靠，特别是对于分析工具而言。如果没有这些，堆栈跟踪可能仅显示内存地址或不完整。这对于本机编译的程序（C++、Rust）来说比 Python 或 Java 更重要。

**要记住的限制：**
- LLM可能会产生看似合理但错误的解释
- 他们可能会建议掩盖错误而不是修复错误的修复
- 始终使用实际调试工具验证建议
- 它们最适合作为理解代码的补充，而不是替代

> 这与开发环境讲座中介绍的 {ref}`通用AI编码能力 <development-environment-ai-powered-development>` 不同。在这里，我们专门讨论使用LLM作为调试辅助工具。

(debugging-profiling-profiling)=
## 性能分析

即使您的代码在功能上表现符合您的预期，但如果它占用了进程中的所有 CPU 或内存，那么这可能还不够好。算法课程经常教授大_O_符号，但不教授如何在程序中查找热点。从 [过早的优化是万恶之源](https://wiki.c2.com/?PrematureOptimization) 开始，您应该了解分析器和监视工具。它们将帮助您了解程序的哪些部分占用了大部分时间和/或资源，以便您可以专注于优化这些部分。

(debugging-profiling-timing)=
### 计时

衡量绩效的最简单方法就是计时。在许多情况下，只需打印代码在两点之间花费的时间就足够了。

但是，挂钟时间可能会产生误导，因为您的计算机可能同时运行其他进程或等待事件发生。 `time` 命令区分_Real_、_User_ 和_Sys_ 时间：

- **真实** - 从开始到结束的挂钟时间，包括等待时间
- **用户** - CPU 运行用户代码所花费的时间
- **Sys** - CPU 运行内核代码所花费的时间

```bash
$ time curl https://missing.csail.mit.edu &> /dev/null
real	0m0.272s
user	0m0.079s
sys	    0m0.028s
```

这里的请求花费了近 300 毫秒（实时），但仅占用了 107 毫秒的 CPU 时间（用户 + 系统）。剩下的就等网络了。

(debugging-profiling-resource-monitoring)=
### 资源监控

有时，分析程序性能的第一步是了解其实际资源消耗是多少。当资源有限时，程序通常运行缓慢。

- **一般监控**：[`htop`](https://htop.dev/) 是 `top` 的改进版本，可显示当前正在运行的进程的各种统计信息。有用的按键绑定：`<F6>` 用于对进程进行排序，`t` 用于显示树层次结构，`h` 用于切换线程。还有 [`btop`](https://github.com/aristocratos/btop) 可以监控_way_更多的东西。

- **I/O 操作**：[`iotop`](https://www.man7.org/linux/man-pages/man8/iotop.8.html) 显示实时 I/O 使用信息。

- **内存使用情况**：[`free`](https://www.man7.org/linux/man-pages/man1/free.1.html) 显示可用内存和已用内存总量。

- **打开文件**：[`lsof`](https://www.man7.org/linux/man-pages/man8/lsof.8.html) 列出有关进程打开的文件的文件信息。对于检查哪个进程打开了特定文件很有用。

- **网络连接**：[`ss`](https://www.man7.org/linux/man-pages/man8/ss.8.html) 可让您监控网络连接。一个常见的用例是确定哪个进程正在使用给定端口：`ss -tlnp | grep :8080`。

- **网络使用情况**：[`nethogs`](https://github.com/raboof/nethogs) 和 [`iftop`](https://pdw.ex-parrot.com/iftop/) 是很好的交互式 CLI 工具，用于监视每个进程的网络使用情况。

(debugging-profiling-visualizing-performance-data)=
### 可视化性能数据

人类在图表中发现模式的速度比在数字表格中快得多。在分析性能时，绘制数据通常会揭示原始数据中不可见的趋势、峰值和异常情况。

**使数据可绘图**：添加打印或日志语句进行调试时，请考虑格式化输出，以便稍后可以轻松绘制图表。 CSV 格式 (`1705012345,42.5`) 的简单时间戳和值比散文句子更容易绘制。 JSON 结构的日志也可以轻松解析和绘制。换句话说，记录您的数据 [整齐地](https://vita.had.co.nz/papers/tidy-data.pdf)。

**使用 gnuplot 快速绘图**：对于简单的命令行绘图，[`gnuplot`](http://www.gnuplot.info/) 可以直接从数据文件生成图形：

```bash
# 绘制一个带有时间戳、值的简单 CSV
gnuplot -e "set datafile separator ','; plot 'latency.csv' using 1:2 with lines"
```

**使用 matplotlib 和 ggplot2 进行迭代探索**：为了进行更深入的分析，Python 的 [`matplotlib`](https://matplotlib.org/) 和 R 的 [`ggplot2`](https://ggplot2.tidyverse.org/) 支持迭代探索。与一次性绘图不同，这些工具可让您快速切片和转换数据以研究假设。 ggplot2 的分面图特别强大 - 您可以按类别将单个数据集拆分为多个子图（例如，按端点或一天中的时间分面请求延迟），以梳理出本来会隐藏的模式。

**用例示例：**
- 绘制随时间变化的请求延迟可以揭示原始百分位数所掩盖的周期性减速（垃圾收集、cron 作业、流量模式）
- 可视化不断增长的数据结构的插入时间可以暴露算法复杂性问题——当支持数组大小加倍时，向量插入图将显示特征峰值
- 按不同维度（请求类型、用户群体、服务器）划分指标通常会揭示“系统范围”的问题实际上被隔离到一个类别

(debugging-profiling-cpu-profilers)=
### CPU 分析器

大多数时候，当人们提到_分析器_时，他们指的是_CPU分析器_。主要有两种类型：

- **跟踪分析器** 记录程序进行的每个函数调用
- **采样分析器**定期探测您的程序（通常每毫秒）并记录程序的堆栈

采样分析器的开销较低，通常更适合生产使用。

(debugging-profiling-perf-the-sampling-profiler)=
#### perf：采样分析器

[`perf`](https://www.man7.org/linux/man-pages/man1/perf.1.html) 是标准 Linux 分析器。它可以分析任何程序而无需重新编译：

`perf stat` 让您快速了解时间花在哪里：

```bash
$ perf stat ./slow_program

 Performance counter stats for './slow_program':

         3,210.45 msec task-clock                #    0.998 CPUs utilized
               12      context-switches          #    3.738 /sec
                0      cpu-migrations            #    0.000 /sec
              156      page-faults               #   48.587 /sec
   12,345,678,901      cycles                    #    3.845 GHz
    9,876,543,210      instructions              #    0.80  insn per cycle
    1,234,567,890      branches                  #  384.532 M/sec
       12,345,678      branch-misses             #    1.00% of all branches
```

现实世界程序的探查器输出将包含大量信息。人类是视觉动物，不擅长阅读大量数字。 [火焰图](https://www.brendangregg.com/flamegraphs.html) 是一种可视化工具，可以使分析数据更容易理解。

火焰图显示 Y 轴上的函数调用层次结构以及与 X 轴成比例的所用时间。它们是交互式的——您可以单击以放大程序的特定部分。

[![火焰图](https://www.brendangregg.com/FlameGraphs/cpu-bash-flamegraph.svg)](https://www.brendangregg.com/FlameGraphs/cpu-bash-flamegraph.svg)

要从 `perf` 数据生成火焰图：

```bash
# 记录个人资料
perf record -g ./my_program

# 生成火焰图（需要火焰图脚本）
perf script | stackcollapse-perf.pl | flamegraph.pl > flamegraph.svg
```

> 考虑使用 [speedscope](https://www.speedscope.app/) 进行基于 Web 的交互式火焰图查看器，或使用 [Perfetto](https://perfetto.dev/) 进行全面的系统级分析。

(debugging-profiling-valgrinds-callgrind-the-tracing-profiler)=
#### Valgrind 的 Callgrind：跟踪分析器

[`callgrind`](https://valgrind.org/docs/manual/cl-manual.html) 是一个分析工具，用于记录程序的调用历史记录和指令计数。与采样分析器不同，它提供精确的调用计数，并可以显示调用者和被调用者之间的关系：

```bash
# 使用 callgrind 运行
valgrind --tool=callgrind ./my_program

# 使用 callgrind_annotate（文本）或 kcachegrind（GUI）进行分析
callgrind_annotate callgrind.out.<pid>
kcachegrind callgrind.out.<pid>
```

Callgrind 比采样分析器慢，但提供精确的调用计数，并且如果您需要该信息，可以选择模拟缓存行为（使用 `--cache-sim=yes`）。

> 如果您使用特定语言，可能会有更专业的分析器。例如，Python 有 [`cProfile`](https://docs.python.org/3/library/profile.html) 和 [`py-spy`](https://github.com/benfred/py-spy)，Go 有 [`go tool pprof`](https://pkg.go.dev/cmd/pprof)，Rust 有 [`cargo-flamegraph`](https://github.com/flamegraph-rs/flamegraph)（实际上适用于任何已编译的程序！）。

(debugging-profiling-memory-profilers)=
### 内存分析器

内存分析器可帮助您了解程序如何随时间使用内存并查找内存泄漏。

(debugging-profiling-valgrinds-massif)=
#### Valgrind 的 Massif

[`massif`](https://valgrind.org/docs/manual/ms-manual.html) 分析堆内存使用情况：

```bash
valgrind --tool=massif ./my_program
ms_print massif.out.<pid>
```

这显示了一段时间内堆的使用情况，有助于识别内存泄漏和过度分配。

> 对于 Python，[`memory-profiler`](https://pypi.org/project/memory-profiler/) 提供逐行内存使用信息。

(debugging-profiling-benchmarking)=
### 基准测试

当您需要比较不同实现或工具的性能时，[`hyperfine`](https://github.com/sharkdp/hyperfine) 非常适合对命令行程序进行基准测试：

```bash
$ hyperfine --warmup 3 'fd -e jpg' 'find . -iname "*.jpg"'
Benchmark #1: fd -e jpg
  Time (mean ± σ):      51.4 ms ±   2.9 ms    [User: 121.0 ms, System: 160.5 ms]
  Range (min … max):    44.2 ms …  60.1 ms    56 runs

Benchmark #2: find . -iname "*.jpg"
  Time (mean ± σ):      1.126 s ±  0.101 s    [User: 141.1 ms, System: 956.1 ms]
  Range (min … max):    0.975 s …  1.287 s    10 runs

Summary
  'fd -e jpg' ran
   21.89 ± 2.33 times faster than 'find . -iname "*.jpg"'
```

> 对于 Web 开发，浏览器开发人员工具包括出色的分析器。请参阅 [Firefox Profiler](https://profiler.firefox.com/docs/) 和 [Chrome 开发工具](https://developers.google.com/web/tools/chrome-devtools/rendering-tools) 文档。

### Exercises

```{exercise} 用调试器修复归并排序
:label: exercise-debug-merge-sort

实现官方练习中的归并排序伪代码，用调试器单步进入 `merge`，使测试输入 `[3,1,4,1,5,9,2,6]` 得到正确结果。
```

```{solution} exercise-debug-merge-sort
:class: dropdown

错误位于右侧较小时的分支：追加的是 `right[i]`，应为 `right[j]`。给 `i`、`j`、`left[i]`、`right[j]` 加观察，第一次进入 `else` 就能看到索引不一致。修复后再加入空数组、重复值、已排序与逆序测试。
```

```{exercise} 用 rr 反向定位越界写
:label: exercise-debug-rr-corruption

保存官方 `corruption.c`，用 `gcc -g` 编译，`rr record` 后 `rr replay`；监视 `students[1].id` 并反向定位覆盖它的语句。
```

```{solution} exercise-debug-rr-corruption
:class: dropdown

`Student.scores` 只有 3 项，但 `curve_scores` 循环条件是 `i < 4`。`students[0].scores[3]` 与紧随其后的 `students[1].id` 重叠。修复为 `i < 3`，更稳妥地写成 `i < sizeof students[student_idx].scores / sizeof students[student_idx].scores[0]`。
```

```{exercise} 用 ASan 检测 use-after-free
:label: exercise-debug-asan-uaf

运行官方 `uaf.c`，先普通编译，再用 `gcc -fsanitize=address -g` 编译，阅读报告并修复。
```

```{solution} exercise-debug-asan-uaf
:class: dropdown

`free(greeting)` 后仍执行 `greeting[0] = 'J'` 和 `printf`，属于 heap-use-after-free。若仍需修改和打印，应把 `free` 移到最后一次使用之后；释放后把指针设为 `NULL` 能减少误用，但不能替代正确生命周期设计。
```

```{exercise} 跟踪系统调用
:label: exercise-debug-strace

用 `strace`（Linux）或 `dtruss`（macOS）跟踪 `ls -l`，再观察一个更复杂程序打开了哪些文件。
```

```{solution} exercise-debug-strace
:class: dropdown

Linux 可运行 `strace -f -e trace=file ls -l 2>trace.log`。常见调用包括 `execve`、动态库相关的 `openat`/`mmap`、读取目录的 `getdents64`、查询元数据的 `statx/newfstatat` 和输出的 `write`。实际名称随系统、libc 与版本变化。
```

```{exercise} 让 LLM 解释诊断
:label: exercise-debug-llm

选择一条难懂的编译错误、strace 片段或 ASan 报告，请 LLM 解释并提出修复，再验证结论。
```

```{solution} exercise-debug-llm
:class: dropdown

高质量提问应包含最小代码、完整错误、编译命令、环境和已尝试步骤，并先移除秘密。验收不是“模型给出回答”，而是最小复现从失败变成功、回归测试通过，并能用工具证据说明根因，而非仅掩盖症状。
```

```{exercise} 阅读 perf stat
:label: exercise-profile-perf-stat

对一个程序运行 `perf stat`，解释主要计数器。
```

```{solution} exercise-profile-perf-stat
:class: dropdown

`task-clock` 是获得 CPU 的时间；context-switches 是调度切换；page-faults 是页错误；cycles 是周期；instructions 是退休指令；IPC = instructions/cycles，需结合工作负载解释；branch-misses 是分支预测失败。虚拟机或内核权限可能限制硬件计数器。
```

```{exercise} perf record 与火焰图
:label: exercise-profile-perf-record

编译官方 `slow.c`：`gcc -g -O2 slow.c -o slow -lm`，运行 `perf record -g ./slow` 和 `perf report`，再尝试生成火焰图。
```

```{solution} exercise-profile-perf-record
:class: dropdown

热点应集中在 `slow_computation` 及数学库的 `sin`/`cos` 路径。宽的栈框代表样本累计较多，不等于单次调用最慢。保留优化级别以测真实代码，同时保留符号和 frame pointer；修改后用同一输入重新测量。
```

```{exercise} 用 hyperfine 比较实现
:label: exercise-profile-hyperfine

比较 `find` 与 `fd`、`grep` 与 `rg`，或自己的两个实现。
```

```{solution} exercise-profile-hyperfine
:class: dropdown

示例：`hyperfine --warmup 3 'find . -name "*.md"' 'fd -e md'`。先确认两条命令语义和输出集合相同；报告均值、标准差和范围，并注意文件系统缓存、后台负载与样本规模。
```

```{exercise} CPU 亲和性
:label: exercise-profile-taskset

在 htop 中观察 `taskset --cpu-list 0,2 stress -c 3`。为什么三个 worker 没有使用三个 CPU？
```

```{solution} exercise-profile-taskset
:class: dropdown

亲和性集合只允许 CPU 0 和 2，共两个逻辑 CPU。三个忙循环都能运行，但必须在两个 CPU 上竞争时间片，因此不可能同时占满三个 CPU。
```

```{exercise} 查找占用端口的进程
:label: exercise-debug-port

运行 `python -m http.server 4444`，在另一终端找出监听进程并终止它。
```

```{solution} exercise-debug-port
:class: dropdown

`ss -tlnp | grep ':4444'` 显示 PID/程序（查看其他用户进程可能需要 sudo）；也可用 `lsof -nP -iTCP:4444 -sTCP:LISTEN`。先发送 `kill PID`（SIGTERM）并确认端口释放，只有进程拒绝退出时才考虑 `kill -KILL`。
```

### 许可与署名

本页依据 MIT Missing Semester 2026 第四讲[官方 notes](https://missing.csail.mit.edu/2026/debugging-profiling/)整理，原材料采用 [CC BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可。
