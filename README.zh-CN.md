# Funix

> 你的旨意行在地上，如同行在天上。 —— 马太福音，6:10
> 
> 你的代码跑在云端，如同跑在本机。 —— 凤凰经，3:16

[![PyPI version](https://badge.fury.io/py/funix.svg)](https://badge.fury.io/py/funix)

[English](README.md)

Funix 可自动将你的 Python 函数生成前后端，可部署到云端对外提供服务。你几乎不需要修改原有的代码，只需要为你的函数加上简单的 `@funix` 装饰器即可。

## 安装

### 从 GitHub 安装

你可以直接透过以下命令直接安装：

```bash
pip install "git+https://github.com/TexteaInc/funix.git"
```

如果你想手动从本地安装：

1. `git clone https://github.com/TexteaInc/funix`
2. `cd funix`
3. `pip install -e .`

### 从 PyPI 安装

```bash
pip install funix
```

## 使用

```text
usage: funix [-h] [--host HOST] [--port PORT] [--front-port FRONT_PORT] [--no-frontend] this_class main_class

Funix

positional arguments:
  this_class            this class
  main_class            main class to import

options:
  -h, --help            show this help message and exit
  --host HOST           host of frontend & backend
  --port PORT           port of backend
  --front-port FRONT_PORT
                        port of frontend
  --no-frontend         disable frontend
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
