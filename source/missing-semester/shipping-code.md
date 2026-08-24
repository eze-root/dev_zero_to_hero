# 第六讲：打包与交付代码

> 官方 notes：[https://missing.csail.mit.edu/2026/shipping-code/](https://missing.csail.mit.edu/2026/shipping-code/)  
> 视频：[YouTube](https://www.youtube.com/watch?v=KBMiB-8P4Ns)

```{note}
本文依照 Missing Semester 2026 官方 notes 的原文结构完整翻译；保留标题层级、命令示例、工具链接、引用与提示。练习采用 MyST exercise，并在官方题目之外补充折叠参考答案。
```


让代码按预期工作是很困难的；让相同的代码在与您自己的机器不同的机器上运行通常更困难。

交付代码意味着获取您编写的代码并将其转换为可用的形式，其他人无需对您的计算机进行精确设置即可运行。交付代码有多种形式，取决于编程语言、系统库和操作系统的选择以及许多其他因素。它还取决于您要构建的内容：软件库、命令行工具和 Web 服务都有不同的要求和部署步骤。无论如何，所有这些场景之间都有一个共同的模式：我们需要定义可交付成果是什么——又名“产物”——以及它对周围环境做出的假设。

在本次讲座中，我们将介绍：

- {ref}`依赖关系和环境 <shipping-code-dependencies--environments>`
- {ref}`产物和包装 <shipping-code-artifacts--packaging>`
- {ref}`发布和版本控制 <shipping-code-releases--versioning>`
- {ref}`再现性 <shipping-code-reproducibility>`
- {ref}`虚拟机和容器 <shipping-code-vms--containers>`
- {ref}`配置 <shipping-code-configuration>`
- {ref}`服务与编排 <shipping-code-services--orchestration>`
- {ref}`出版 <shipping-code-publishing>`

我们将通过Python生态系统中的示例来解释这些概念，因为具体的示例有助于理解。虽然其他编程语言生态系统的工具有所不同，但概念基本上是相同的。

(shipping-code-dependencies--environments)=
# 依赖与环境

在现代软件开发中，抽象层无处不在。程序自然地将逻辑卸载到其他库或服务。然而，这在您的程序和它运行所需的库之间引入了_依赖_关系。例如，在 Python 中，要获取网站的内容，我们经常这样做：

```python
import requests

response = requests.get("https://missing.csail.mit.edu")
```

然而，`requests` 库并未与 Python 运行时捆绑在一起，因此，如果我们尝试在未安装 `requests` 的情况下运行此代码，Python 将引发错误：

```console
$ python fetch.py
Traceback (most recent call last):
  File "fetch.py", line 1, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'
```

为了使这个库可用，我们需要首先运行 `pip install requests` 来安装它。 `pip` 是 Python 编程语言提供的用于安装包的命令行工具。执行 `pip install requests` 会产生以下操作序列：

1. 在 Python 包索引 ([PyPI](https://pypi.org/)) 中搜索请求
1. 搜索适合我们正在运行的平台的产物
1. 解决依赖关系 --- `requests` 库本身依赖于其他包，因此安装程序必须找到所有传递依赖项的兼容版本并预先安装它们
1. 下载产物，然后解压并将文件复制到文件系统中的正确位置

```console
$ pip install requests
Collecting requests
  Downloading requests-2.32.3-py3-none-any.whl (64 kB)
Collecting charset-normalizer<4,>=2
  Downloading charset_normalizer-3.4.0-cp311-cp311-manylinux_x86_64.whl (142 kB)
Collecting idna<4,>=2.5
  Downloading idna-3.10-py3-none-any.whl (70 kB)
Collecting urllib3<3,>=1.21.1
  Downloading urllib3-2.2.3-py3-none-any.whl (126 kB)
Collecting certifi>=2017.4.17
  Downloading certifi-2024.8.30-py3-none-any.whl (167 kB)
Installing collected packages: urllib3, idna, charset-normalizer, certifi, requests
Successfully installed certifi-2024.8.30 charset-normalizer-3.4.0 idna-3.10 requests-2.32.3 urllib3-2.2.3
```

在这里我们可以看到 `requests` 有自己的依赖项，例如 `certifi` 或 `charset-normalizer`，并且必须先安装它们，然后才能安装 `requests`。安装后，Python 运行时在导入时可以找到该库。

```console
$ python -c 'import requests; print(requests.__path__)'
['/usr/local/lib/python3.11/dist-packages/requests']

$ pip list | grep requests
requests        2.32.3
```

编程语言有不同的工具、约定和实践来安装和发布库。在 Rust 等某些语言中，工具链是统一的 --- `cargo` 处理构建、测试、依赖管理和发布。在 Python 等其他语言中，统一发生在规范级别——而不是单个工具，而是有标准化规范来定义打包的工作方式，允许每个任务使用多个竞争工具（`pip` 与 [`uv`](https://docs.astral.sh/uv/)、`setuptools` 与 [`hatch`](https://hatch.pypa.io/) 与 [`poetry`](https://python-poetry.org/)）。在 LaTeX 等生态系统中，TeX Live 或 MacTeX 等发行版捆绑了数千个预安装的软件包。

引入依赖也会引入依赖冲突。当程序需要同一依赖项的不兼容版本时，就会发生冲突。例如，如果 `tensorflow==2.3.0` 需要 `numpy>=1.16.0,<1.19.0`，`pandas==1.2.0` 需要 `numpy>=1.16.5`，则满足 `numpy>=1.16.5,<1.19.0` 的任何版本都将有效。但是，如果项目中的另一个包需要 `numpy>=1.19`，则会发生冲突，因为没有满足所有约束的有效版本。

这种情况——多个包需要共享依赖项的相互不兼容的版本——通常被称为“依赖地狱”。处理冲突的一种方法是将每个程序的依赖项隔离到它们自己的_环境_中。在 Python 中，我们通过运行以下命令创建虚拟环境：

```console
$ which python
/usr/bin/python
$ pwd
/home/missingsemester
$ python -m venv venv
$ source venv/bin/activate
$ which python
/home/missingsemester/venv/bin/python
$ which pip
/home/missingsemester/venv/bin/pip
$ python -c 'import requests; print(requests.__path__)'
['/home/missingsemester/venv/lib/python3.11/site-packages/requests']

$ pip list
Package Version
------- -------
pip     24.0
```

您可以将环境视为语言运行时的完整独立版本，具有自己的一组已安装软件包。此虚拟环境或 venv 将已安装的依赖项与全局 Python 安装隔离。为每个项目提供一个包含其所需依赖项的虚拟环境是一个很好的做法。

> 虽然许多现代操作系统都附带了 Python 等编程语言运行时的安装，但修改这些安装是不明智的，因为操作系统可能依赖它们来实现其自身的功能。更喜欢使用单独的环境。

在某些语言中，安装协议不是由工具定义的，而是作为规范定义的。在 Python 中，[PEP 517](https://peps.python.org/pep-0517/) 定义构建系统接口，[PEP 621](https://peps.python.org/pep-0621/) 指定项目元数据如何存储在 `pyproject.toml` 中。这使得开发人员能够改进 `pip` 并生成更优化的工具，例如 `uv`。要安装 `uv`，只需执行 `pip install uv` 即可。

使用 `uv` 代替 `pip` 遵循相同的界面，但速度明显更快：

```console
$ uv pip install requests
Resolved 5 packages in 12ms
Prepared 5 packages in 0.45ms
Installed 5 packages in 8ms
 + certifi==2024.8.30
 + charset-normalizer==3.4.0
 + idna==3.10
 + requests==2.32.3
 + urllib3==2.2.3
```

> 我们强烈建议尽可能使用 `uv pip` 而不是 `pip`，因为它可以大大减少安装时间。

除了依赖隔离之外，环境还允许您拥有不同版本的编程语言运行时。

```console
$ uv venv --python 3.12 venv312
Using CPython 3.12.7
Creating virtual environment at: venv312

$ source venv312/bin/activate && python --version
Python 3.12.7

$ uv venv --python 3.11 venv311
Using CPython 3.11.10
Creating virtual environment at: venv311

$ source venv311/bin/activate && python --version
Python 3.11.10
```

当您需要跨多个 Python 版本测试代码或项目需要特定版本时，这会很有帮助。

> 在某些编程语言中，每个项目都会自动为其依赖项获取自己的环境，而不是手动创建它，但原理是相同的。如今，大多数语言还具有一种机制，可以在单个系统上管理该语言的多个版本，然后指定各个项目使用哪个版本。

(shipping-code-artifacts--packaging)=
# 产物与打包

在软件开发中，我们区分源代码和产物。开发人员编写和读取源代码，而产物是从该源代码生成的打包的、可分发的输出——准备安装或部署。产物可以像我们运行的代码文件一样简单，也可以像包含应用程序所有必要部分的整个虚拟机一样复杂。考虑以下示例，当前目录中有一个 Python 文件 `greet.py`：

```console
$ cat greet.py
def greet(name):
    return f"Hello, {name}!"

$ python -c "from greet import greet; print(greet('World'))"
Hello, World!

$ cd /tmp
$ python -c "from greet import greet; print(greet('World'))"
ModuleNotFoundError: No module named 'greet'
```

一旦我们移动到不同的目录，导入就会失败，因为 Python 只搜索特定位置的模块（当前目录、已安装的包和 `PYTHONPATH` 中的路径）。打包通过将代码安装到已知位置来解决这个问题。

在 Python 中，打包库涉及生成一个产物，`pip` 或 `uv` 等软件包安装程序可以使用该产物来安装相关文件。 Python 产物称为 _wheels_，包含安装包所需的所有信息：代码文件、有关包的元数据（名称、版本、依赖项）以及有关在环境中放置文件的位置的说明。构建产物需要我们编写一个项目文件（通常也称为清单），详细说明项目的具体情况、所需的依赖项、包的版本和其他信息。在 Python 中，我们使用 `pyproject.toml` 来实现此目的。

> `pyproject.toml` 是现代且推荐的方式。虽然仍支持 `requirements.txt` 或 `setup.py` 等早期打包方法，但您应尽可能首选 `pyproject.toml`。

以下是还提供命令行工具的库的最小 `pyproject.toml`：

```toml
[project]
name = "greeting"
version = "0.1.0"
description = "A simple greeting library"
dependencies = ["typer>=0.9"]

[project.scripts]
greet = "greeting:cli"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

`typer` 库是一个流行的 Python 包，用于使用最少的样板创建命令行界面。

以及对应的`greeting.py`：

```python
import typer


def greet(name: str) -> str:
    return f"Hello, {name}!"


def cli():
    typer.run(greet)


if __name__ == "__main__":
    cli()
```

有了这个文件，我们现在可以构建wheel 包：

```console
$ uv build
Building source distribution...
Building wheel from source distribution...
Successfully built dist/greeting-0.1.0.tar.gz
Successfully built dist/greeting-0.1.0-py3-none-any.whl

$ ls dist/
greeting-0.1.0-py3-none-any.whl
greeting-0.1.0.tar.gz
```

`.whl` 文件是wheel 包（具有特定结构的 zip 存档），`.tar.gz` 是需要从源代码构建的系统的源码分发包。

您可以检查wheel 包的内容以查看打包的内容：

```console
$ unzip -l dist/greeting-0.1.0-py3-none-any.whl
Archive:  dist/greeting-0.1.0-py3-none-any.whl
  Length      Date    Time    Name
---------  ---------- -----   ----
      150  2024-01-15 10:30   greeting.py
      312  2024-01-15 10:30   greeting-0.1.0.dist-info/METADATA
       92  2024-01-15 10:30   greeting-0.1.0.dist-info/WHEEL
        9  2024-01-15 10:30   greeting-0.1.0.dist-info/top_level.txt
      435  2024-01-15 10:30   greeting-0.1.0.dist-info/RECORD
---------                     -------
      998                     5 files
```

现在，如果我们要把这个wheel 包给其他人，他们可以通过运行以下命令来安装它：

```console
$ uv pip install ./greeting-0.1.0-py3-none-any.whl
$ greet Alice
Hello, Alice!
```

这会将我们之前构建的库安装到他们的环境中，包括 `greet` cli 工具。

这种方法有局限性。特别是如果我们的库依赖于特定于平台的库，例如CUDA 用于 GPU 加速，那么我们的产物仅适用于安装了这些特定库的系统，并且我们可能需要为不同平台（Linux、macOS、Windows）和架构（x86、ARM）构建单独的wheel 包。


安装软件时，从源代码安装和安装预构建的二进制文件之间存在重要区别。从源代码安装意味着下载原始代码并在您的计算机上编译它——这需要安装编译器和构建工具，并且对于大型项目可能会花费大量时间。

安装预构建的二进制文件意味着下载已经由其他人编译的产物——更快、更简单，但二进制文件必须与您的平台和体系结构相匹配。例如，[ripgrep 的发布页面](https://github.com/BurntSushi/ripgrep/releases) 显示适用于 Linux（x86_64、ARM）、macOS（Intel、Apple Silicon）和 Windows 的预构建二进制文件。


(shipping-code-releases--versioning)=
# 发布与版本管理

代码是在连续的过程中构建的，但在离散的基础上发布。在软件开发中，开发环境和生产环境之间有明显的区别。在交付产品之前，需要证明代码可以在开发环境中运行。发布过程涉及许多步骤，包括测试、依赖管理、版本控制、配置、部署和发布。


软件库不是静态的，会随着时间的推移而不断发展，获得修复和新功能。我们通过与库在某个时间点的状态相对应的离散版本标识符来跟踪这种演变。库行为的变化范围很广，从修复非关键功能的补丁、扩展其功能的新特性，到破坏向后兼容性的更改。更改日志记录了版本引入的更改——软件开发人员使用这些文档来传达与新版本相关的更改。

然而，跟踪每个依赖项中正在进行的更改是不切实际的，当我们考虑传递依赖项（即依赖项的依赖项）时更是如此。

> 您可以使用 `uv tree` 可视化项目的整个依赖关系树，它以树格式显示所有包及其传递依赖关系。

为了简化这个问题，存在关于如何对软件进行版本控制的约定，最流行的约定之一是 [语义化版本](https://semver.org/) 或 SemVer。在语义化版本下，版本具有 MAJOR.MINOR.PATCH 形式的标识符，其中每个值都采用整数值。简短的版本是升级：

- PATCH（例如，1.2.3 → 1.2.4）应仅包含错误修复并完全向后兼容
- MINOR（例如 1.2.3 → 1.3.0）以向后兼容的方式添加新功能
- MAJOR（例如，1.2.3 → 2.0.0）表示可能需要修改代码的重大更改

> 这是一种简化，我们鼓励阅读完整的 SemVer 规范，以了解例如为什么从 0.1.3 到 0.2.0 可能会导致重大更改或 1.0.0-rc.1 的含义。
Python 打包本身支持语义化版本，因此当我们指定依赖项的版本时，我们可以使用各种说明符：

在 `pyproject.toml` 中，我们有不同的方法来限制依赖项的兼容版本的范围：

```toml
[project]
dependencies = [
    "requests==2.32.3",  # Exact version - only this specific version
    "click>=8.0",        # Minimum version - 8.0 or newer
    "numpy>=1.24,<2.0",  # Range - at least 1.24 but less than 2.0
    "pandas~=2.1.0",     # Compatible release - >=2.1.0 and <2.2.0
]
```

版本说明符存在于许多包管理器（npm、cargo 等）中，具有不同的确切语义。 `~=` 运算符是 Python 的“兼容版本”运算符 --- `~=2.1.0` 的意思是“与 2.1.0 兼容的任何版本”，翻译过来就是 `>=2.1.0` 和 `<2.2.0`。这大致相当于 npm 和 Cargo 中的插入符 (`^`) 运算符，它遵循 SemVer 的兼容性概念。

并非所有软件都使用语义化版本。常见的替代方案是日历版本控制 (CalVer)，其中版本基于发布日期而不是语义。例如，Ubuntu 使用 `24.04`（2024 年 4 月）和 `24.10`（2024 年 10 月）等版本。 CalVer 可以轻松查看版本的发布时间，但它不会传达任何有关兼容性的信息。  最后，语义化版本并非万无一失，有时维护者会无意中在次要版本或补丁版本中引入重大更改。


(shipping-code-reproducibility)=
# 可复现性

在现代软件开发中，您编写的代码位于大量抽象层之上。这包括编程语言运行时、第三方库、操作系统，甚至硬件本身。这些层之间的任何差异都可能会改变代码的行为，甚至阻止其按预期工作。此外，即使底层硬件的差异也会影响您发布软件的能力。

固定库是指指定确切的版本而不是范围，例如`requests==2.32.3` 而不是 `requests>=2.0`。

包管理器的部分工作是考虑依赖项（以及传递依赖项）提供的所有约束，然后生成满足所有约束的有效版本列表。然后，可以将特定的版本列表保存到文件中以供重复使用；这些文件称为_锁定文件_。

```console
$ uv lock
Resolved 12 packages in 45ms

$ cat uv.lock | head -20
version = 1
requires-python = ">=3.11"

[[package]]
name = "certifi"
version = "2024.8.30"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/...", hash = "sha256:..." }
wheels = [
    { url = "https://files.pythonhosted.org/...", hash = "sha256:..." },
]
...
```

处理依赖项版本控制和可重复性时的一个关键区别是库和应用程序/服务之间的差异。库旨在由可能具有自己的依赖项的其他代码导入和使用，因此指定过于严格的版本约束可能会导致与用户的其他依赖项发生冲突。相比之下，应用程序或服务是软件的最终消费者，通常通过用户界面或 API（而不是通过编程接口）公开其功能。对于库，最好指定版本范围，以最大限度地提高与更广泛的包生态系统的兼容性。对于应用程序来说，固定确切的版本可以确保可重复性——运行该应用程序的每个人都使用完全相同的依赖项。


对于需要最大可重复性的项目，[Nix](https://nixos.org/) 和 [Bazel](https://bazel.build/) 等工具提供了_hermetic_构建——其中每个输入（包括编译器、系统库，甚至构建环境本身）都被固定和内容寻址。无论构建何时何地运行，这都保证了逐位相同的输出。

> 您甚至可以使用 NixOS 来管理整个计算机安装，以便您可以轻松启动计算机设置的新副本，并通过版本控制的配置文件管理其完整配置。

软件开发中永无休止的紧张局势是，新软件版本有意或无意地引入破坏，而另一方面，随着时间的推移，旧软件版本会因安全漏洞而受到损害。我们可以通过使用持续集成管道（我们将在 [代码质量和 CI](code-quality.md) 讲座中了解更多内容）来解决这个问题，该管道针对新软件版本测试我们的应用程序，并通过自动化来检测何时发布依赖项的新版本，例如 [Dependabot](https://github.com/dependabot)。

即使进行了 CI 测试，升级软件版本时仍然会出现问题，通常是因为开发环境和生产环境之间不可避免地不匹配。在这种情况下，最好的做法是制定_回滚_计划，其中版本升级将被恢复，并重新部署已知的良好版本。

(shipping-code-vms--containers)=
# 虚拟机和容器

当您开始依赖更复杂的依赖项时，代码的依赖项很可能会超出包管理器可以处理的范围。一个常见的原因是必须与特定的系统库或硬件驱动程序交互。例如，在科学计算和人工智能中，程序通常需要专门的库和驱动程序来利用 GPU 硬件。许多系统级依赖项（GPU 驱动程序、特定编译器版本、OpenSSL 等共享库）仍然需要系统范围内的安装。

传统上，这种更广泛的依赖性问题是通过虚拟机 (VM) 解决的。虚拟机对整个计算机进行抽象，并提供一个完全隔离的环境及其自己的专用操作系统。更现代的方法是容器，它将应用程序及其依赖项、库和文件系统打包，但共享主机的操作系统内核，而不是虚拟化整个计算机。容器比虚拟机更轻，因为它们共享内核，因此启动速度更快，运行效率更高。

最流行的容器平台是 [Docker](https://www.docker.com/)。 Docker 引入了一种构建、分发和运行容器的标准化方法。在底层，Docker 使用 containerd 作为其容器运行时——这是 Kubernetes 等其他工具也使用的行业标准。

运行容器很简单。例如，要在容器内运行 Python 解释器，我们使用 `docker run`（`-it` 标志使容器与终端交互。当您退出时，容器会停止。）。

```console
$ docker run -it python:3.12 python
Python 3.12.7 (main, Nov  5 2024, 02:53:25) [GCC 12.2.0] on linux
>>> print("Hello from inside a container!")
Hello from inside a container!
```

实际上，您的程序可能依赖于整个文件系统。为了克服这个问题，我们可以使用容器镜像来将应用程序的整个文件系统作为产物提供。容器镜像是以编程方式创建的。通过 docker，我们可以使用 Dockerfile 语法准确指定镜像的依赖项、系统库和配置：

```dockerfile
FROM python:3.12
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y libpq-dev
RUN pip install numpy
RUN pip install pandas
COPY . /app
WORKDIR /app
RUN pip install .
```

一个重要的区别：Docker **镜像**是打包的产物（如模板），而**容器**是该镜像的运行实例。您可以从同一个镜像运行多个容器。镜像是分层构建的，Dockerfile 中的每条指令（`FROM`、`RUN`、`COPY` 等）都会创建一个新层。 Docker 会缓存这些层，因此如果您更改 Dockerfile 中的一行，则只需重建该层和后续层。

以前的 Dockerfile 有几个问题：它使用完整的 Python 镜像而不是精简版本，运行单独的 `RUN` 命令创建不必要的层，版本未固定，并且不清理包管理器缓存，传送不必要的文件。其他常见错误包括以 root 身份不安全地运行容器以及意外地将机密嵌入层中。

这是一个改进版本

```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY . .
RUN uv sync --locked --no-dev
```

在前面的示例中，我们看到我们不是从源安装 `uv`，而是从 `ghcr.io/astral-sh/uv:latest` 映像复制预构建的二进制文件。这称为 _builder_ 模式。使用这种模式，我们不需要提供编译代码所需的所有工具，只需提供运行应用程序所需的最终二进制文件（在本例中为 `uv`）。

Docker 有一些需要注意的重要限制。首先，容器镜像通常是特定于平台的——如果没有模拟，为 `linux/amd64` 构建的镜像将无法在 `linux/arm64` (Apple Silicon Mac) 上本机运行，速度很慢。其次，Docker 容器需要 Linux 内核，因此在 macOS 和 Windows 上，Docker 实际上在底层运行一个轻量级 Linux 虚拟机，从而增加了开销。第三，Docker的隔离性比VM弱——容器共享主机内核，这在多租户环境中是一个安全问题。

> 如今，越来越多的项目也利用 nix 通过 [Nix Flakes](https://serokell.io/blog/practical-nix-flakes) 来管理每个项目的“系统范围”库和应用程序。

(shipping-code-configuration)=
# 配置

软件本质上是可配置的。在 [命令行环境](command-line-environment.md) 讲座中，我们看到程序通过标志、环境变量甚至配置文件（又称为dotfiles）接收选项。即使对于更复杂的应用程序也是如此，并且存在用于大规模管理配置的既定模式。软件配置不应嵌入代码中，而应在运行时提供。一些常见的是环境变量和配置文件。

以下是通过环境变量配置的应用程序的示例：

```python
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///local.db")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
API_KEY = os.environ["API_KEY"]  # Required - will raise if not set
```

应用程序还可以通过配置文件（例如，通过 `yaml.load` 加载配置的 Python 程序）`config.yaml` 进行配置：

```yaml
database:
  url: "postgresql://localhost/myapp"
  pool_size: 5
server:
  host: "0.0.0.0"
  port: 8080
  debug: false
```

考虑配置的一个好的右手规则是，相同的代码库应该可以部署到不同的环境（开发、登台、生产），只需更改配置，而无需更改代码。

在众多配置选项中，通常存在 API 密钥等敏感数据。秘密需要小心处理，避免意外泄露，并且不得包含在版本控制中。


(shipping-code-services--orchestration)=
# 服务与编排

现代应用程序很少孤立存在。典型的 Web 应用程序可能需要用于持久存储的数据库、用于性能的缓存、用于后台任务的消息队列以及各种其他支持服务。现代架构通常将功能分解为可以独立开发、部署和扩展的单独服务，而不是将所有内容捆绑到单个整体应用程序中。

举个例子，如果我们确定我们的应用程序可能会受益于使用缓存，那么我们可以利用现有的经过实战测试的解决方案，例如 [Redis](https://redis.io/) 或 [Memcached](https://memcached.org/)，而不是自行推出。我们可以通过将 Redis 构建为容器的一部分来将 Redis 嵌入到我们的应用程序依赖项中，但这意味着协调 Redis 和我们的应用程序之间的所有依赖项可能具有挑战性，甚至是不可行的。相反，我们可以做的是将每个应用程序单独部署在其自己的容器中。这通常称为微服务架构，其中每个组件作为独立服务运行，通过网络（通常通过 HTTP API）进行通信。

[Docker Compose](https://docs.docker.com/compose/) 是用于定义和运行多容器应用程序的工具。您无需单独管理容器，而是在单个 YAML 文件中声明所有服务并将它们编排在一起。现在我们的完整应用程序包含多个容器：

```yaml
# docker-compose.yml
services:
  web:
    build: .
    ports:
      - "8080:8080"
    environment:
      - REDIS_URL=redis://cache:6379
    depends_on:
      - cache

  cache:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

使用 `docker compose up`，两个服务一起启动，Web 应用程序可以使用主机名 `cache` 连接到 Redis（Docker 的内部 DNS 自动解析服务名称）。 Docker Compose 让我们可以声明如何部署一项或多项服务，并处理将它们一起启动、在它们之间建立网络以及管理共享卷以实现数据持久性的编排。

对于生产部署，您通常希望 docker compose 服务在启动时自动启动并在失败时重新启动。一种常见的方法是使用 systemd 来管理 docker compose 部署：

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/myapp
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down

[Install]
WantedBy=multi-user.target
```

此 systemd 单元文件可确保您的应用程序在系统启动时（Docker 准备就绪后）启动，并提供 `systemctl start myapp`、`systemctl stop myapp` 和 `systemctl status myapp` 等标准控件。

随着部署需求变得越来越复杂——需要跨多台机器的可扩展性、服务崩溃时的容错能力以及高可用性保证——组织转向复杂的容器编排平台，如 Kubernetes (k8s)，它可以跨机器集群管理数千个容器。也就是说，Kubernetes 具有陡峭的学习曲线和显着的运营开销，因此对于较小的项目来说通常是大材小用。

这种多容器设置在一定程度上是可行的，因为现代服务通过标准化 API 和 HTTP REST API 相互通信。例如，每当程序与 OpenAI 或 Anthropic 等 LLM 提供商交互时，它都会向其服务器发送 HTTP 请求并解析响应：

```text
$ curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "content-type: application/json" \
    -H "anthropic-version: 2023-06-01" \
    -d '{"model": "claude-sonnet-4-20250514", "max_tokens": 256,
         "messages": [{"role": "user", "content": "Explain containers vs VMs in one sentence."}]}'
```

(shipping-code-publishing)=
# 发布

一旦您证明代码可以工作，您可能有兴趣将其分发给其他人下载和安装。分发有多种形式，并且本质上与您所使用的编程语言和环境相关。

最简单的分发形式是上传产物供人们在本地下载和安装。这仍然很常见，您可以在 [Ubuntu 的软件包存档](http://archive.ubuntu.com/ubuntu/pool/main/) 等地方找到它，它本质上是 `.deb` 文件的 HTTP 目录列表。

如今，GitHub 已成为事实上的源代码和产物发布平台。虽然源代码通常是公开可用的，但 GitHub Releases 允许维护者将预构建的二进制文件和其他产物附加到标记版本。


包管理器有时支持直接从 GitHub 安装，无论是从源代码还是从预构建的wheel 包：

```console
# 从源安装（将克隆和构建）
$ pip install git+https://github.com/psf/requests.git

# 从特定标签/分支安装
$ pip install git+https://github.com/psf/requests.git@v2.32.3

# 直接从 GitHub 版本安装 Wheel
$ pip install https://github.com/user/repo/releases/download/v1.0/package-1.0-py3-none-any.whl
```

事实上，像 Go 这样的一些语言使用分散的分发模型——而不是中央包仓库，Go 模块直接从其源代码仓库分发。像 `github.com/gorilla/mux` 这样的模块路径指示代码所在的位置，`go get` 直接从那里获取。但是，大多数包管理器（例如 `pip`、`cargo` 或 `brew`）都具有预打包项目的中心索引，以便于分发和安装。如果我们跑

```console
$ uv pip install requests --verbose --no-cache 2>&1 | grep -F '.whl'
DEBUG Selecting: requests==2.32.5 [compatible] (requests-2.32.5-py3-none-any.whl)
DEBUG No cache entry for: https://files.pythonhosted.org/packages/1e/db/4254e3eabe8020b458f1a747140d32277ec7a271daf1d235b70dc0b4e6e3/requests-2.32.5-py3-none-any.whl.metadata
DEBUG No cache entry for: https://files.pythonhosted.org/packages/1e/db/4254e3eabe8020b458f1a747140d32277ec7a271daf1d235b70dc0b4e6e3/requests-2.32.5-py3-none-any.whl
```

我们可以看到从哪里获取 `requests` 轮。请注意文件名中的 `py3-none-any` --- 这意味着该wheel 包适用于任何 Python 3 版本、任何操作系统、任何架构。对于带有编译代码的包，wheel 包是特定于平台的：

```console
$ uv pip install numpy --verbose --no-cache 2>&1 | grep -F '.whl'
DEBUG Selecting: numpy==2.2.1 [compatible] (numpy-2.2.1-cp312-cp312-macosx_14_0_arm64.whl)
```

这里 `cp312-cp312-macosx_14_0_arm64` 表示该wheel 包专门用于 macOS 14+ for ARM64 (Apple Silicon) 上的 CPython 3.12。如果您使用不同的平台，`pip` 将下载不同的wheel 包或从源代码构建。

相反，为了让人们能够找到我们创建的包，我们需要将其发布到这些注册表之一。在 Python 中，主注册表是 [Python 包索引 (PyPI)](https://pypi.org)。与安装一样，发布包的方式有多种。 `uv publish` 命令提供了一个用于将包上传到 PyPI 的现代界面：

```console
$ uv publish --publish-url https://test.pypi.org/legacy/
Publishing greeting-0.1.0.tar.gz
Publishing greeting-0.1.0-py3-none-any.whl
```

在这里，我们使用 [测试PyPI](https://test.pypi.org)——一个单独的包注册表，旨在测试您的发布工作流程，而不会污染真正的 PyPI。上传后，您可以从 TestPyPI 安装：

```console
$ uv pip install --index-url https://test.pypi.org/simple/ greeting
```

发布软件时的一个关键考虑因素是信任。用户如何验证他们下载的包确实来自您并且没有被篡改？包注册表使用校验和来验证完整性，一些生态系统支持包签名以提供作者身份的加密证明。

不同的语言有自己的包注册表：用于 Rust 的 [crates.io](https://crates.io)、用于 JavaScript 的 [npm](https://www.npmjs.com)、用于 Ruby 的 [RubyGems](https://rubygems.org) 以及用于容器镜像的 [Docker Hub](https://hub.docker.com)。同时，对于私有或内部包，组织通常部署自己的包仓库（例如私有 PyPI 服务器或私有 Docker 注册表）或使用云提供商的托管解决方案。

将 Web 服务部署到 Internet 涉及额外的基础设施：域名注册、将域指向服务器的 DNS 配置，以及通常使用 nginx 等反向代理来处理 HTTPS 和路由流量。对于文档或静态站点等更简单的用例，[GitHub Pages](https://pages.github.com/) 直接从仓库提供免费托管。

<!--
(shipping-code-documentation)=
## 文档

到目前为止，我们已经强调可交付的产物作为打包与交付代码的主要输出。除了产物之外，我们还需要为用户记录代码的功能、安装说明和使用示例。

[Sphinx](https://www.sphinx-doc.org/) (Python) 和 [MkDocs](https://www.mkdocs.org/) 等工具可以从文档字符串和 Markdown 文件自动生成可浏览的文档，这些文档通常托管在 [Read the Docs](https://readthedocs.org/) 等服务上。对于基于 HTTP 的 API，[OpenAPI Specification](https://www.openapis.org/)（以前称为 Swagger）提供了用于描述 API 端点的标准格式，工具可使用该格式自动生成交互式文档和客户端库。 -->

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
