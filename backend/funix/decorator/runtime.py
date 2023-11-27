import ast
import inspect
from _ast import (
    Assign,
    Attribute,
    Call,
    ClassDef,
    Constant,
    Expr,
    FunctionDef,
    Load,
    Module,
    Name,
    Return,
    Store,
)
from typing import Any

import funix
from funix.session import get_global_variable, set_global_variable


def get_init_function(cls_name: str):
    inited_class = get_global_variable("__FUNIX_" + cls_name)

    if inited_class is None:
        raise Exception("Class must be inited first!")
    else:
        return inited_class


def set_init_function(cls_name: str, cls):
    set_global_variable("__FUNIX_" + cls_name, cls)


def get_imports(path) -> list:
    with open(path) as fh:
        root = ast.parse(fh.read(), path)

    imports = []

    for node in ast.iter_child_nodes(root):
        if isinstance(node, ast.Import):
            imports.append(node)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node)
        else:
            continue

    return imports


class RuntimeClassVisitor(ast.NodeVisitor):
    def __init__(self, cls_name: str, funix: Any, cls: Any):
        self.funix = funix
        self._cls_name = cls_name
        self._cls = cls
        source_path = inspect.getsourcefile(self._cls.__init__)
        self._imports = get_imports(source_path)

    def visit_ClassDef(self, node: ClassDef) -> Any:
        for cls_function in node.body:
            if isinstance(cls_function, FunctionDef):
                self.visit_FunctionDef(cls_function)

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        args = node.args

        is_static_method = False

        funix_decorator = Call(
            func=Attribute(
                value=Name(id="__funix__module__", ctx=Load()), attr="funix", ctx=Load()
            ),
            args=[],
            keywords=[],
        )

        for decorator in node.decorator_list:
            if hasattr(decorator, "id") and decorator.id == "staticmethod":
                is_static_method = True

            if hasattr(decorator, "func"):
                func = decorator.func
                if (hasattr(func, "id") and func.id == "funix_method") or (
                    hasattr(func, "value")
                    and hasattr(func.value, "id")
                    and func.value.id == "funix"
                    and hasattr(func, "attr")
                    and func.attr == "funix_method"
                ):
                    for key_word in decorator.keywords:
                        if key_word.arg == "disable" and key_word.value.value:
                            return
                    funix_decorator.keywords = decorator.keywords
                    funix_decorator.args = decorator.args

        if not is_static_method:
            # Yes .args
            args.args.pop(0)

        if node.name.startswith("_") and node.name != "__init__":
            return

        body = [
            *self._imports,
            FunctionDef(
                name=node.name,
                args=args,
                decorator_list=[funix_decorator],
                returns=node.returns,
                lineno=0,
            ),
        ]
        function = body[-1]
        new_module = Module(
            body=body,
            type_ignores=[],
        )

        if node.name == "__init__":
            # new_module.body[0].decorator_list[0].keywords = [
            #     keyword(arg="title", value=Constant(value=self._cls_name))
            # ]
            function.name = "initialize_" + self._cls_name
            function.body = [
                Expr(
                    value=Call(
                        func=Name(id="set_init_function", ctx=Load()),
                        args=[
                            Constant(value=self._cls_name),
                            Call(
                                func=Name(id=self._cls_name, ctx=Load()),
                                args=[
                                    Name(id=args.arg, ctx=Load()) for args in args.args
                                ],
                                keywords=[],
                            ),
                        ],
                        keywords=[],
                    )
                )
            ]
        else:
            if is_static_method:
                function.body = [
                    Return(
                        value=Call(
                            func=Attribute(
                                value=Name(id=f"{self._cls_name}", ctx=Load()),
                                attr=node.name,
                                ctx=Load(),
                            ),
                            args=[Name(id=arg.arg, ctx=Load()) for arg in args.args],
                            keywords=[],
                        )
                    )
                ]
            else:
                function.body = [
                    Assign(
                        targets=[Name(id="api", ctx=Store())],
                        value=Call(
                            func=Name(id="get_init_function", ctx=Load()),
                            args=[Constant(value=self._cls_name)],
                            keywords=[],
                        ),
                        lineno=0,
                    ),
                    Return(
                        value=Call(
                            func=Attribute(
                                value=Name(id="api", ctx=Load()),
                                attr=node.name,
                                ctx=Load(),
                            ),
                            args=[Name(id=args.arg, ctx=Load()) for args in args.args],
                            keywords=[],
                        )
                    ),
                ]

        globals()["__funix__module__"] = funix
        globals()[self._cls_name] = self._cls
        code = ast.unparse(new_module)
        try:
            exec(
                code,
                globals(),
                locals(),
            )
        except Exception as e:
            print("=== Executed code start ===")
            print(code)
            print("=== Executed code end ===")
            raise e
