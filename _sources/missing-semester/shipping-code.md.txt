# 第六讲：打包与交付代码

> 官方 notes：[Packaging and Shipping Code](https://missing.csail.mit.edu/2026/shipping-code/)  
> 视频：[YouTube](https://www.youtube.com/watch?v=KBMiB-8P4Ns)

```{note}
“在我的机器上能跑”不是交付。交付首先要定义产物（artifact），再明确它对运行时、系统库、操作系统、硬件和配置的假设。
```

## 依赖与环境

安装 `requests` 不只是复制一个目录：包管理器要查询索引、选择平台产物、解析传递依赖、下载并校验，然后安装到解释器能找到的位置。依赖约束互相冲突会导致 dependency hell，因此不同项目应使用隔离环境，不要修改操作系统自带的 Python。

Python 通过 PEP 517 规范构建接口、PEP 621 规范 `pyproject.toml` 元数据，允许 pip、uv、setuptools、hatch 等工具互操作。课程推荐 [`uv`](https://docs.astral.sh/uv/)：

```bash
uv init
uv add requests
uv run python app.py
uv lock
uv sync --locked
```

环境既隔离包，也能选择解释器版本。激活 venv 的本质是修改当前 Shell 的 `PATH` 等变量，让项目中的 `python`、`pip` 排在系统程序之前；uv 也可以直接用 `uv run`，无须手动激活。

## 产物与打包

源代码面向开发者，artifact 面向安装和部署。Python wheel 包含代码和名称、版本、依赖、入口点等元数据；源码分发包允许目标环境自行构建。现代项目把清单放在 `pyproject.toml`，可用 `uv build` 生成 `dist/*.whl` 与 `*.tar.gz`，再在全新环境安装测试。

纯 Python wheel 的标签可能是 `py3-none-any`；含本地扩展的 wheel 会绑定 Python ABI、操作系统和架构，例如 CPython 3.12/macOS/ARM64。预编译二进制安装快，但必须匹配平台；源码构建更通用，却要求编译器和系统头文件。

## 发布、版本与可复现性

SemVer 使用 `MAJOR.MINOR.PATCH`：兼容修复递增 PATCH，兼容功能递增 MINOR，破坏兼容递增 MAJOR；0.x 和预发布版本还有额外语义。CalVer 则把日期作为版本信息。版本号是兼容性承诺的一部分，但不能替代 changelog 与迁移说明。

依赖声明表达允许范围，锁文件记录解析出的精确版本、来源与哈希。库应避免过度收紧传递依赖，给使用者留出共同解析空间；应用/服务是最终消费者，更适合提交锁文件并按它部署。更强的可复现构建还要固定编译器、系统库和构建环境，Nix、Bazel 等工具面向这类 hermetic build。

锁定旧版本与修复安全漏洞存在张力。应借助 CI、Dependabot 类更新工具与回滚方案持续升级，而不是永久冻结。

## VM、容器与镜像

VM 虚拟化整台计算机和内核，隔离强、开销较大；容器共享宿主内核，把应用文件系统和进程隔离打包，启动更快，但隔离边界较弱。image 是只读模板，container 是它的运行实例。

Dockerfile 每条指令形成缓存层。良好镜像通常使用小型基础镜像、合并并清理系统安装、先复制锁文件以利用依赖缓存、以非 root 用户运行，并通过多阶段构建只保留运行产物。秘密不能写进 `ARG`、`ENV` 或任何层，因为删除文件也不会从旧层消失。

## 配置、服务与编排

同一份代码应仅靠运行时配置部署到开发、预发布和生产环境。配置可来自环境变量或文件；API key、数据库口令等秘密不可提交 Git，应交给秘密管理系统，并限制读取范围。

应用常依赖数据库、缓存与队列。Docker Compose 用 YAML 声明多个服务、网络、卷和启动关系；服务名可通过内部 DNS 解析。生产环境还需要健康检查、持久化、备份、重启策略和日志。systemd 能管理单机 Compose；Kubernetes 提供跨机调度和高可用，但其运维成本对小项目往往过高。

最终产物可以发布到 GitHub Releases、PyPI、crates.io、npm、容器 registry 等。发布链路应校验哈希/签名并保护发布凭据。静态网站适合 GitHub Pages；公开 Web 服务还涉及 DNS、TLS、反向代理、监控和回滚。

## Exercises

```{exercise} 观察虚拟环境激活
:label: exercise-ship-venv-env

分别在创建/激活 venv 前后保存 `printenv` 并 diff；解释 PATH 变化以及 `deactivate` 函数的作用。
```

````{solution} exercise-ship-venv-env
:class: dropdown

```bash
printenv | sort >before.txt
python -m venv .venv
source .venv/bin/activate
printenv | sort >after.txt
diff -u before.txt after.txt
type deactivate
```

通常新增 `VIRTUAL_ENV`，`PATH` 前置 `.venv/bin`，提示符也可能变化，所以命令查找优先选中 venv。`deactivate` 是由激活脚本注入当前 Shell 的函数，用保存的旧值恢复环境并删除自身；`type` 比 `which` 更适合检查函数。
````

```{exercise} 创建 uv 驱动的 Python 包
:label: exercise-ship-python-package

创建带 `pyproject.toml` 的包，在虚拟环境安装，生成并检查锁文件。
```

````{solution} exercise-ship-python-package
:class: dropdown

```bash
uv init --package greeting
cd greeting
uv add typer
uv lock
uv tree
uv build
uv run python -c 'import greeting; print(greeting.__file__)'
```

检查 `pyproject.toml` 中直接约束与 `uv.lock` 中传递依赖、来源和哈希；再在临时空环境中安装 `dist/*.whl`，避免只测试可编辑源码树。
````

```{exercise} 用 Compose 构建课程网站
:label: exercise-ship-missing-docker

安装 Docker，使用课程仓库已有的 Compose 配置在本地构建 Missing Semester 网站。
```

```{solution} exercise-ship-missing-docker
:class: dropdown

克隆官方仓库后先阅读 Compose/Dockerfile，再运行 `docker compose build` 与 `docker compose up`。以仓库 README 给出的端口为准；用 `docker compose logs -f` 排错，结束后 `docker compose down`。不要在不理解挂载范围时把主机敏感目录映射进去。
```

```{exercise} Python + Redis 多容器应用
:label: exercise-ship-python-redis

为简单 Python 应用编写 Dockerfile，再用 `compose.yaml` 同时运行应用与 Redis。
```

```{solution} exercise-ship-python-redis
:class: dropdown

Compose 中定义 `web: {build: ., environment: [REDIS_URL=redis://cache:6379]}` 与 `cache: {image: redis:7-alpine}`，并为 Redis 声明命名卷。应用连接主机名应为服务名 `cache`，不是 `localhost`。加入健康检查和重试；`depends_on` 的启动顺序不保证 Redis 已准备好。
```

```{exercise} 发布到 TestPyPI 与 GHCR
:label: exercise-ship-publish

把测试包发布到 TestPyPI，构建包含该包的镜像并推送到 `ghcr.io`。
```

```{solution} exercise-ship-publish
:class: dropdown

先 `uv build` 并在干净环境测试，然后用受限、短期 token 执行 `uv publish --publish-url https://test.pypi.org/legacy/`。镜像使用 `docker build -t ghcr.io/OWNER/NAME:VERSION .`，登录后 push。更推荐用 CI 的 trusted publishing/OIDC，避免长期 token；发布后从远端重新安装/拉取做冒烟测试。
```

```{exercise} 发布 GitHub Pages
:label: exercise-ship-pages

建立一个网站并用 GitHub Pages 发布；可选配置自定义域名。
```

```{solution} exercise-ship-pages
:class: dropdown

在仓库 Settings → Pages 选择分支或 GitHub Actions，确保构建产物含入口 `index.html`，部署后检查 Actions 与公开 URL。自定义域名需配置 `CNAME`/`A` 或 `AAAA`/`ALIAS` 记录、仓库中的 custom domain，并等待证书签发后启用 HTTPS；先按 GitHub 文档验证 DNS，避免域名接管风险。
```

## 许可与署名

本页依据 MIT Missing Semester 2026 第六讲[官方 notes](https://missing.csail.mit.edu/2026/shipping-code/)整理，原材料采用 [CC BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可。
