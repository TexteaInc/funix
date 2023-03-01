# Funix —— 无需手动创建部件，即可构建 Web 程序

Funix 可自动将一个普通的 Python 函数转换为一个可用的 Web 程序，而无需你手动创建部件（见下文示例）。仅仅只需在你的函数上添加 `@funix` 装饰器，它就会成为 Web 应用供任何人使用，他们无需任何编程知识。

Funix 还支持复杂的数据类型和部件，如多列数据表或者 Matplotlib 图表。如果你想要自定义 UI，没关系，Funix 支持声明式语法，可以在装饰器中完成对组件的自定义。Funix 是同时也是非侵入式的，你仍然可以像往常一样在本地运行或调试你的 Python 代码。

<div align="center">

[![PyPI version](https://badge.fury.io/py/funix.svg)](https://badge.fury.io/py/funix)

<h3><a href="https://github.com/TexteaInc/funix-doc/blob/main/QuickStart.md">快速入门指南和例子展示（英语）</a>  </h3>

[English](README.md)

https://user-images.githubusercontent.com/438579/219586150-7ff491dd-dfea-41ea-bfad-4610abf1fe20.mp4

<a href="https://www.youtube.com/watch?v=UGp5gbR8f3c">在 YouTube 上播放</a>

<br /><br />

</div>


> **WIP**: Funix 仍在开发中, 如果你有任何问题，不必拘束，请[开启一个 issue](https://github.com/TexteaInc/funix/issues/new)。

## 快速浏览

在你的函数上面只需添加两行代码，该函数就会被转换为一个 Web 程序：

```python
from funix import funix # 添加第一行

@funix()                # 添加第二行
def hello(your_name: str) -> str:
    return f"Hello, {your_name}."
```

将上述代码保存为 `hello.py`，随后在终端中执行：

```bash
funix hello
```

这个 Web 程序将会在 `http://localhost:3000` 中启动，并自动在浏览器窗口打开。

![screenshots/hello.png](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/hello.png)

## 案例展览

### 在 Python 中最短的 Dall-E Web 程序

```python
from funix import funix                      # 添加第一行
from funix.hint import Images                # 添加第二行
import openai  # pip install openai

openai.api_key = os.environ.get("OPENAI_KEY")

@funix()                                     # 添加第三行
def dalle(prompt: str = "a cat") -> Image:
    response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    return response["data"][0]["url"]
```

![Dalle demo](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/dalle.jpg)

### 复合式 UI

```python
from typing import List
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

@funix(
        widgets={
           "a": "sheet",
           "b": ["sheet", "slider[0,1,0.01]"]
        }
)

# 下面是一个简单的 matplotlib 函数
def table_plot(a: List[int], b: List[float]) -> Figure:
    fig = plt.figure()
    plt.plot(a, b)
    return fig
```

![table plot demo static](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/table_plot.png)


### 声明式的 UI 配置

在 Funix 中，你的 UI 配置可以单独写到额外的配置文件或主题中，这么做可以使你只需要关注功能而非 UI。

```python
from funix import funix_yaml

@funix_yaml("""
    widgets:
        x: slider[0,10,1]
        op: radio
    whitelist:
        op:
            - square
            - cube
""")

def power(x: int, op: str) -> Markdown:
    if op =="square":
        return  f"\
* The _square_ of {x} is **{x * x}**. \n \
* Made by [Funix](http://funix.io)"
    elif op == "cube":
        # return x * x * x
        return  f"\
* The _cube_ of {x} is **{x * x * x}**. \n \
* Made by [Funix](http://funix.io)"
```

![power slider radio](https://github.com/TexteaInc/funix-doc/raw/main/screenshots/power_slider_radio.png)

## 安装

### 从 PyPI 安装

```bash
pip install funix
```

### 从 GitHub 安装

你可以直接透过以下命令直接安装：

```bash
pip install "git+https://github.com/TexteaInc/funix.git"
```

### 本地安装

如果你想手动从本地安装：

1. `git clone https://github.com/TexteaInc/funix`
2. `cd funix`
3. `pip install -e .` (如果 pip 坚持要安装到全局环境中，请带上 `--prefix=~/.local` 参数。 参见 [#24](https://github.com/TexteaInc/funix/issues/24) 和 [#23](https://github.com/TexteaInc/funix/issues/23))


## 使用

```text
usage: funix [-h] [-H 127.0.0.1] [-p 3000] [-F] [-B] [main_class]

Funix: Building web apps without manually creating widgets

positional arguments:
  main_class            Main class to import

options:
  -h, --help            show this help message and exit
  -H 127.0.0.1, --host 127.0.0.1
                        Host of frontend and backend
  -p 3000, --port 3000  Port of frontend and backend
  -F, --no-frontend     Disable frontend server
  -B, --no-browser      Disable auto open browser
```

通常你可以使用 `python -m funix [module]` 直接启动，在 `examples` 文件夹里有一些简单的例子带你了解 Funix，你可以通过以下命令打开示例：

```bash
cd examples
python -m funix examples
python -m funix examples_better # Examples V2 😄
```

安装位于 GitHub 的最新代码，你可以直接通过 `funix [module]` 命令启动。

## 构建前端

在 Funix 中，我们已经打包好了前端，你可以直接使用，同时也有一个部署在[公网的前端页面](https://funix.vercel.app/)。如果你想自行构建前端，你可以通过以下命令：

```bash
# 请先 clone 本项目并进入项目文件夹
cd frontend
yarn install # 安装依赖
yarn build # 构建
yarn funix:build # 构建到 Funix Python 中
yarn funix:test # 启动 Funix 前端开发环境（这会自动设置后端为 http://127.0.0.1:8080）
```

## 如何参与贡献

Funix 是在 MIT 许可证下开源的。我们不但欢迎而且希望社区做出贡献。当你准备好的时候，请随意 fork 本项目并 PR。你也可以通过 [Issue Tracker](https://github.com/TexteaInc/funix/issues/new) 报告错误，建议新功能等。

## 团队

Textea 的 Funix 团队由以下人员组成：

* [Ruixuan Tu](https://github.com/Turx)
* [Yazawazi](https://github.com/Yazawazi)
* [Forrest Sheng Bao](https://forrestbao.github.io/)
