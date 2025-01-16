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
    Tuple,
    keyword,
)
from ast import NodeVisitor, unparse
from typing import Any

import funix
from funix.app import app, get_new_app_and_sock_for_jupyter, sock
from funix.config.switch import GlobalSwitchOption
from funix.decorator.lists import (
    set_class,
    set_class_method_funix,
    set_class_method_org,
)
from funix.hint import WrapperException
from funix.session import get_global_variable, set_global_variable


def get_init_function(cls_name: str) -> Any:
    """
    Get the inited class. Used in the funix ast handler.

    Parameters:
        cls_name (str): The class name.

    Returns:
        Any: The inited class.

    Raises:
        WrapperException: If the class is not inited.
    """
    inited_class = get_global_variable("__FUNIX_" + cls_name)

    if inited_class is None:
        raise WrapperException("Class must be inited first!")
    else:
        return inited_class


def set_init_function(cls_name: str, cls: Any):
    """
    Set the inited class. Used in the funix ast handler.

    Parameters:
        cls_name (str): The class name.
        cls (Any): The inited class.
    """
    set_global_variable("__FUNIX_" + cls_name, cls)


class RuntimeClassVisitor(NodeVisitor):
    """
    The runtime class visitor.

    Base Class:
        ast.NodeVisitor: The ast node visitor.

    Attributes:
        funix (Any): The funix module.
        _cls_name (str): The class name.
        _cls (Any): The class (no instance).
        _imports (list): The imports.
        open_function (bool): Whether to start function import.
    """

    def __init__(self, cls_name: str, funix_: Any, cls: Any, menu: str):
        """
        Initialize the runtime class visitor.

        Parameters:
            cls_name (str): The class name.
            funix_ (Any): The funix module.
            cls (Any): The class (no instance).
            menu (str): The menu.
        """
        self.funix = funix_
        self._cls_name = cls_name
        self._cls = cls
        self._imports = []
        self.menu = menu
        if GlobalSwitchOption.in_notebook:
            self.class_app, self.class_sock = get_new_app_and_sock_for_jupyter()
        else:
            self.class_app = app
            self.class_sock = sock

        self.open_function = False

        # keep order number track
        self.number_tracker = 0

    def visit_Import(self, node):
        """
        Visit the import node, and append it to the imports.

        Parameters:
            node (_ast.Import): The import node.
        """
        self._imports.append(node)

    def visit_ImportFrom(self, node):
        """
        Visit the import from node, and append it to the imports.

        Parameters:
            node (_ast.ImportFrom): The import from node.
        """
        self._imports.append(node)

    def visit_ClassDef(self, node: ClassDef):
        """
        Visit the class definition node.

        If this is the class we want, then visit the function definition node.

        Parameters:
            node (_ast.ClassDef): The class definition node.
        """
        if node.name != self._cls_name:
            return
        set_class(self.class_app.name, self._cls.__qualname__, self._cls)
        for cls_function in node.body:
            if isinstance(cls_function, FunctionDef):
                self.open_function = True
                self.visit_FunctionDef(cls_function)
                self.open_function = False

    def visit_FunctionDef(self, node: FunctionDef):
        """
        Visit the function definition node. And create the function.

        Parameters:
            node (_ast.FunctionDef): The function definition node.
        """
        if not self.open_function:
            return
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

        if GlobalSwitchOption.in_notebook:
            funix_decorator.keywords.append(
                keyword(
                    arg="app_and_sock",
                    value=Tuple(
                        elts=[
                            Name(id="class_app", ctx=Load()),
                            Name(id="class_sock", ctx=Load()),
                        ],
                        ctx=Load(),
                    ),
                ),
            )

            funix_decorator.keywords.append(
                keyword(
                    arg="jupyter_class",
                    value=Constant(value=True),
                )
            )

        funix_decorator.keywords.append(
            keyword(
                arg="menu",
                value=Constant(
                    value=self.menu
                    if self.menu
                    else self._cls_name.replace("_", " ")
                    if GlobalSwitchOption.AUTO_CONVERT_UNDERSCORE_TO_SPACE_IN_NAME
                    else self._cls_name
                ),
            )
        )

        if not node.name.startswith("_") or node.name == "__init__":
            funix_decorator.keywords.append(
                keyword(
                    arg="class_method_qualname",
                    value=Constant(value=self._cls.__dict__[node.name].__qualname__),
                )
            )

        funix_decorator.keywords.append(
            keyword(
                arg="is_class_method",
                value=Constant(value=True),
            )
        )

        funix_decorator.keywords.append(
            keyword(
                arg="order",
                value=Constant(value=self.number_tracker),
            )
        )

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

        node_doc_string = None
        if node.body:
            if isinstance(node.body[0], Expr) and isinstance(
                node.body[0].value, Constant
            ):
                node_doc_string = node.body[0].value.value

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
            if node_doc_string:
                function.body.insert(0, Expr(value=Constant(value=node_doc_string)))
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
                if node_doc_string:
                    function.body.insert(0, Expr(value=Constant(value=node_doc_string)))
            else:
                function.body = [
                    Assign(
                        targets=[Name(id="_funix_self", ctx=Store())],
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
                                value=Name(id="_funix_self", ctx=Load()),
                                attr=node.name,
                                ctx=Load(),
                            ),
                            args=[Name(id=args.arg, ctx=Load()) for args in args.args],
                            keywords=[],
                        )
                    ),
                ]
                if node_doc_string:
                    function.body.insert(0, Expr(value=Constant(value=node_doc_string)))

        globals()["__funix__module__"] = funix
        globals()[self._cls_name] = self._cls
        globals()["class_app"] = self.class_app
        globals()["class_sock"] = self.class_sock
        code = unparse(new_module)
        # print(code)
        try:
            exec(
                code,
                globals(),
                locals(),
            )
            set_class_method_org(
                app_name=self.class_app.name,
                method_qualname=self._cls.__dict__[node.name].__qualname__,
                org_method=self._cls.__dict__[node.name],
            )
            self.number_tracker += 1
        except Exception as e:
            print("=== Executed code start ===")
            print(code)
            print("=== Executed code end ===")
            raise e
