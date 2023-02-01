# Funix —— 无需手动创建部件，即可构建 Web 程序

> 你的旨意行在地上，如同行在天上。 —— 马太福音，6:10
>
> 你的代码跑在云端，如同跑在本机。 —— 凤凰经，3:16

[![PyPI version](https://badge.fury.io/py/funix.svg)](https://badge.fury.io/py/funix)

[English](README.md)

Funix 可自动将一个普通的 Python 函数转换为一个可用的 Web 程序，而无需你手动创建部件。仅仅只需在你的函数上添加 `@funix` 装饰器，它就会成为 Web 应用供任何人使用，他们无需任何编程支持。

Funix 还支持复杂的数据类型和部件，如多列数据表或者 Matplotlib 图表。Funix 是同时也是非侵入式的，你仍然可以像往常一样在本地运行或调试你的 Python 代码。Funix 还有一个后端，用于自己的前端以及那些想将 Python 函数转换为 RESTful API 的人。

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

> **Note**
> 默认前端服务将开放 80 端口。如果前端页面不可用，你可能需要以 root 权限运行 Funix，或修改前端端口号。

```text
usage: funix [-h] [--host HOST] [--port PORT] [--front-port FRONT_PORT] [--no-frontend] [--no-browser]
             this_class main_class

Funix

positional arguments:
  this_class            this class
  main_class            main class to import

options:
  -h, --help            show this help message and exit
  --host HOST, -H HOST  host of frontend & backend
  --port PORT, -p PORT  port of backend
  --front-port FRONT_PORT, -P FRONT_PORT
                        port of frontend
  --no-frontend, -F     disable frontend
  --no-browser, -B      disable auto open browser
```

通常你可以使用 `python -m funix [module]` 直接启动，在 `examples` 文件夹里有一些简单的例子带你了解 Funix，你可以通过以下命令打开示例：

```bash
cd examples
python -m funix examples
python -m funix examples_better # Examples V2 😄
```

## 构建前端

在 Funix 中，我们已经打包好了前端，你可以直接使用，同时也有一个部署在[公网的前端页面](https://pdf.textea.io/)。如果你想自行构建前端，你可以通过以下命令：

```bash
# 请先 clone 本项目并进入项目文件夹
cd frontend
yarn install # 安装依赖
yarn build # 构建
yarn funix:build # 构建到 Funix Python 中
yarn funix:test # 启动 Funix 前端开发环境（这会自动设置后端为 http://127.0.0.1:8080）
```
