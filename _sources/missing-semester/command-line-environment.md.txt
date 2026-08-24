# 第二讲：命令行环境

> 官方 notes：[Command-line Environment](https://missing.csail.mit.edu/2026/command-line-environment/)  
> 视频：[YouTube](https://www.youtube.com/watch?v=ccBGsPedE9Q)

```{note}
本文依据 2026 年第二讲官方 notes 整理。Shell 脚本围绕“启动程序并让程序高效通信”设计；理解约定，比背诵命令更重要。
```

## 命令行接口的五个通道

命令行程序之间主要通过五类机制协作：参数、数据流、环境变量、退出码与信号。它们共同构成了 CLI 的“函数签名”。

### 参数与 glob

Shell 把命令拆成字符串参数。脚本中 `$0` 是程序名，`$1` 到 `$9` 是位置参数，`$#` 是参数数量，`"$@"` 保留所有参数的边界。常见约定包括短选项 `-a`、长选项 `--all`、组合短选项 `-la`，以及用 `--` 标记选项结束。

glob 在程序启动前由 Shell 展开：`*` 匹配零个或多个字符，`?` 匹配一个字符，`{a,b}` 生成多个候选参数。例如 `mv *{.py,.sh} src/` 会把当前目录中的 Python 与 Shell 文件一起传给 `mv`。给变量加双引号仍是默认安全做法：`rm -- "$file"`。

### stdin、stdout 与 stderr

每个进程默认拥有标准输入 0、标准输出 1 和标准错误 2。管道 `|` 只连接 stdout；流水线中的程序并发运行，而不是等待上一条命令完整结束后才依次启动。

```bash
echo hello >output.txt       # 覆盖 stdout
echo world >>output.txt      # 追加 stdout
cmd 2>errors.txt             # 单独保存 stderr
cmd >all.txt 2>&1            # 合并两个输出流
grep pattern <input.txt      # 从文件提供 stdin
cmd >/dev/null 2>&1          # 丢弃输出
```

[`fzf`](https://github.com/junegunn/fzf) 是这一接口的典型例子：它从 stdin 读取候选行，交互筛选后把选择写到 stdout，因此可以自然嵌入任意管道。

### 变量、环境与替换

`foo=bar` 创建 Shell 变量，等号两侧不能有空格。`export DEBUG=1` 把变量加入环境，使后续子进程继承；`TZ=Asia/Tokyo date` 则只为这一条命令设置环境。`$(command)` 把 stdout 存入字符串，`<(command)` 把输出临时呈现为文件名，适合 `diff` 等要求文件参数的程序。

### 退出码与信号

退出码 0 按约定表示成功，非 0 表示不同失败。`&&` 在前一条成功时继续，`||` 在前一条失败时继续，`if` 和 `while` 也直接依据命令退出码判断。

`Ctrl-C` 通常发送 `SIGINT`，`Ctrl-Z` 发送 `SIGTSTP` 暂停前台任务；`fg`、`bg`、`jobs` 管理 Shell 作业。`SIGTERM` 请求进程优雅退出，`SIGKILL` 无法捕获，只应作为最后手段。脚本可用 `trap cleanup EXIT INT TERM` 保证清理临时资源。

## 远程机器与 SSH

SSH 在本地与远程机之间建立加密会话：

```bash
ssh user@server
ssh server 'journalctl -u sshd | tail'
scp local.txt server:/tmp/
rsync -avP project/ server:project/
```

公钥认证把公钥放到服务器的 `~/.ssh/authorized_keys`，私钥只留在本机并由 `ssh-agent` 缓存解密。常用主机应写入 `~/.ssh/config`，避免反复输入用户、端口和密钥路径。

端口转发让本地程序安全访问远端服务。`ssh -L 9999:localhost:8888 vm` 把本机 9999 转到远端 8888；`ssh -R` 是反向转发。先确认方向与监听地址，避免意外把内部服务暴露到公网。

## tmux、dotfiles 与终端

[`tmux`](https://github.com/tmux/tmux) 把会话、窗口、窗格分成三层，并支持断开后重新连接。默认前缀是 `Ctrl-b`：`c` 新建窗口，`%` 和 `"` 分割窗格，`d` 脱离，`tmux attach` 恢复。

Shell、Git、Vim、SSH 与 tmux 通常使用纯文本 dotfiles 配置。把它们放入版本库，再用符号链接或安装脚本部署，可以获得可追踪、可同步、可重复的工作环境。不要盲目复制他人的完整配置；逐项理解，尤其不要直接执行未审查的 `curl | bash`。

别忽略终端模拟器本身：字体、配色、快捷键、滚动缓冲与性能会长期影响体验。Shell 插件、别名和提示符应服务于真实的高频操作，而不是堆叠视觉效果。

## AI 在命令行中的位置

AI 可以把自然语言转换为候选命令、处理不规则文本，或作为能执行多步任务的“元 Shell”。执行前仍要检查路径、引号、权限与破坏性参数；处理秘密、生产数据或不可逆操作时尤其不能把确认权交给模型。

## Exercises

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

## 许可与署名

本页依据 MIT Missing Semester 2026 第二讲[官方 notes](https://missing.csail.mit.edu/2026/command-line-environment/)整理，原材料采用 [CC BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可。
