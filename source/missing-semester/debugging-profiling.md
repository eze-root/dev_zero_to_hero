# 第四讲：调试与性能分析

> 官方 notes：[Debugging and Profiling](https://missing.csail.mit.edu/2026/debugging-profiling/)  
> 视频：[YouTube](https://www.youtube.com/watch?v=8VYT9TcUmKs)

```{note}
代码执行的是你告诉它做的事，而不是你以为自己告诉它做的事。调试缩小“预期与事实”的差距；性能分析则先测量，再把优化精力放在真正的热点上。
```

## 从日志到调试器

有节制的打印是有效的第一步；长期代码应使用日志框架，获得级别、目标、时间与结构化字段。复现问题时也要检查第三方程序的 `-v/--verbose`、`journalctl -u SERVICE` 和系统日志。修复问题后，可把关键临时打印改成 DEBUG 日志，而不是全部删除。

当不知道该打印什么、状态难以重建，或重启代价高时，应使用调试器。GDB/LLDB 的基本动作是：断点 `break`、运行 `run`、继续 `continue`、单步进入/越过/退出 `step/next/finish`、打印 `print`、调用栈 `backtrace`、监视表达式 `watch`。原生程序应带 `-g` 调试符号；`-fno-omit-frame-pointer` 还能改善栈追踪。

[`rr`](https://rr-project.org/) 在 Linux 记录一次执行并确定性重放，支持 `reverse-continue` 等反向调试。典型流程是：运行到损坏状态，给损坏变量设 watchpoint，再反向继续找到首次写坏它的位置。它依赖硬件性能计数器，并不适用于所有 VM 或 GPU 工作负载。

## 从程序追到系统

`strace` 观察 Linux 系统调用：`-e trace=file` 聚焦文件，`-f` 跟踪子进程，`-p PID` 附加，`-T` 显示耗时。macOS 可用 `dtruss`。需要更低开销、内核探针和聚合时，可使用 eBPF / `bpftrace`；它通常需要 root，过滤范围必须谨慎。

网络问题可用 `tcpdump`/Wireshark 查看包，浏览器 Network 面板查看已解密的 Web 请求。HTTPS 抓包涉及敏感信息与证书信任，使用中间人代理前必须明确授权。

原生内存错误优先使用编译器 Sanitizer：ASan 检测越界与 use-after-free，TSan 检测数据竞争，MSan 检测未初始化读取，UBSan 检测未定义行为。无法重编译时可尝试 Valgrind，但通常更慢。

LLM 适合解释编译器错误、跨语言边界和栈追踪，也会生成看似合理但错误的根因。把它当作提出假设的助手，再用复现、断点、trace 或 sanitizer 验证。

## 先测量，再优化

`time` 区分 real（墙钟）、user（用户态 CPU）与 sys（内核态 CPU）。real 很大而 user+sys 较小，通常意味着等待网络、磁盘或锁。

资源总览可用 `htop`/`btop`，I/O 用 `iotop`，内存用 `free`，打开文件用 `lsof`，端口与连接用 `ss`，网络流量用 `nethogs`/`iftop`。记录数据时采用 CSV 或结构化 JSON，便于用 gnuplot、matplotlib 或 ggplot2 观察周期、尖峰和分组差异。

CPU profiler 分两类：tracing 记录每次调用，信息精确但开销高；sampling 周期采样调用栈，通常更适合真实工作负载。Linux 的 `perf stat` 给出计数器，`perf record -g` 记录采样，火焰图用横向宽度表示累计时间。Valgrind Callgrind 提供精确调用计数，Massif 记录堆随时间的变化。比较实现应使用 [`hyperfine`](https://github.com/sharkdp/hyperfine) 做预热、多次运行和统计，而不是只跑一次。

## Exercises

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

## 许可与署名

本页依据 MIT Missing Semester 2026 第四讲[官方 notes](https://missing.csail.mit.edu/2026/debugging-profiling/)整理，原材料采用 [CC BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可。
