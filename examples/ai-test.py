from funix import funix_ai


@funix_ai("我想要一个简单的函数，用于展示一个 Hello, world! 的页面。粉红色样式。并为 `name` 设置几个例子。")
def hello(name: str) -> str:
    return f"Hello, {name}!"
