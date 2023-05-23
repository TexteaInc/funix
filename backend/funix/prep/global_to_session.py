"""
Experimental, AST Global preprocessing, looking to transform specific global variables into funix sessions

Limited application cases/not fully considered
"""

from _ast import (
    Assign,
    Attribute,
    Call,
    Constant,
    Expr,
    FunctionDef,
    Global,
    List,
    Load,
    Module,
    Name,
)
from ast import NodeTransformer, parse, unparse
from os.path import join
from random import sample
from string import ascii_letters
from typing import Any

from funix.util.file import create_safe_tempdir

MESS_NAMES: list[str] = [
    "".join(sample("ABCDEF", 5)),
    "".join(sample("GHIJKL", 5)),
    "".join(sample("MNOPQR", 5)),
]
"""
Random names for `get_global_variable`, `set_global_variable`, `set_default_global_variable`.
"""

USE_METHOD: list[str] = list(map(lambda x: f"_FUNIX_SESSION_{x}", MESS_NAMES))
"""
There may be a conflict, perhaps.
"""

session_variables: set[str] = set()
"""
The global variables to transform.
"""


def add_force_import(source_code: str) -> str:
    """
    Add my own import. Don't trust the user's import.

    Parameters:
        source_code (str): The source code.

    Returns:
        str: The source code
    """
    import_text = (
        f"from funix.session import "
        f"get_global_variable as {USE_METHOD[0]}, "
        f"set_global_variable as {USE_METHOD[1]}, "
        f"set_default_global_variable as {USE_METHOD[2]}"
    )
    return import_text + "\n" + source_code


def read_and_clean_decorator_keywords(decorator: Call) -> Call:
    """
    Read and clean the decorator keywords. (for `session_variables`)

    Parameters:
        decorator (Call): The decorator keywords.

    Returns:
        Call: The new decorator.
    """
    keywords = decorator.keywords
    need_del = -1
    for index, keyword_ in enumerate(keywords):
        if keyword_.arg == "session_variables":
            assert isinstance(keyword_.value, List), "session_variables must be a list"
            for element in keyword_.value.elts:
                assert isinstance(
                    element, Constant
                ), "session_variables must be a list of string"
                session_variables.add(element.value)
            need_del = index
    if need_del != -1:
        del decorator.keywords[need_del]
    return decorator


class ScanSessionVariablesVisitor(NodeTransformer):
    """
    Only for two cases:

    ```python
    import funix  # This is the first case


    @funix.funix(
        session_variables=["user_word"],
    )
    def set_word(word: str) -> str:
        global user_word
        user_word = word
        return "Success"
    ```

    ```
    from funix import funix  # This is the second case


    @funix(
        session_variables=["user_word"],
    )
    def set_word(word: str) -> str:
        global user_word
        user_word = word
        return "Success"
    ```

    No `as`, and no `a = funix` or something like that

    And just `@` decorator, no `funix()(func)` or something like that,
    the session_variables must be a list of string, and the string must be a valid python variable name
    """

    def visit_FunctionDef(self, node: FunctionDef) -> FunctionDef:
        """
        Visit the function definition.
        Get all the session variables, and delete the `session_variables` keyword.

        Parameters:
            node (FunctionDef): The function definition.

        Returns:
            FunctionDef: The function definition.
        """
        if len(node.decorator_list) > 0:
            for decorator in node.decorator_list:
                if isinstance(decorator, Call):
                    if isinstance(decorator.func, Name):
                        if decorator.func.id == "funix":
                            read_and_clean_decorator_keywords(decorator)
                    if isinstance(decorator.func, Attribute):
                        if isinstance(decorator.func.value, Name):
                            if decorator.func.value.id == "funix":
                                read_and_clean_decorator_keywords(decorator)
        return node


def change_body_assignments(nodes: Module) -> Module:
    """
    Change the body of the function to add the session variables
    X = Y, just this case

    Parameters:
        nodes (Module): The module.

    Returns:
        Module: The module.
    """
    for index, node in enumerate(nodes.body):
        if isinstance(node, Assign):
            if isinstance(node.targets[0], Name):
                if node.targets[0].id in session_variables:
                    nodes.body[index] = Expr(
                        value=Call(
                            func=Name(id=USE_METHOD[2]),
                            args=[Constant(node.targets[0].id), node.value],
                            keywords=[],
                        )
                    )
    return nodes


class EditSessionVariablesTransformer(NodeTransformer):
    """
    Now let's transform the global variables to session variables
    """

    def visit_Global(self, node: Global) -> Any:
        """
        Visit the global variables.
        Remove the global variables that are in the session variables.

        Parameters:
            node (Global): The global variables.

        Returns:
            Any: Don't care.
        """
        if node.names[0] in session_variables:
            return []

    def visit_Assign(self, node: Any) -> Any:
        """
        Visit the assignment.
        Transform the global variables to session variables.

        Parameters:
            node (Any): The assignment.

        Returns:
            Any: The `set_global_variable` Call.
        """
        if isinstance(node.targets[0], Name):
            if node.targets[0].id in session_variables:
                node = Expr(
                    value=Call(
                        func=Name(id=USE_METHOD[1], ctx=Load()),
                        args=[Constant(node.targets[0].id), node.value],
                        keywords=[],
                    )
                )
        return node

    def visit_Name(self, node: Any) -> Any:
        """
        Visit the name.
        Transform the global variables to session variables.

        Parameters:
            node (Any): The name.

        Returns:
            Any: The `get_global_variable` Call.
        """
        if node.id in session_variables:
            node = Call(
                func=Name(id=USE_METHOD[0]), args=[Constant(node.id)], keywords=[]
            )
        return node


def do_global_to_session(source: str) -> str:
    """
    Preprocess the source code.

    Parameters:
        source (str): The source code.

    Returns:
        str: The source code.
    """
    pre_add_source = add_force_import(source)
    nodes = parse(pre_add_source)
    ScanSessionVariablesVisitor().visit(nodes)
    nodes = change_body_assignments(nodes)
    EditSessionVariablesTransformer().visit(nodes)
    return unparse(nodes)


def get_new_python_file(file_path: str) -> str:
    """
    Get the new python file path.

    Parameters:
        file_path (str): The python file path.

    Returns:
        str: The new python file path.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        source = file.read()

    new_source = do_global_to_session(source)
    new_dir = create_safe_tempdir()
    new_file_path = join(new_dir, "".join(sample(ascii_letters, 10)) + ".py")

    with open(new_file_path, "w", encoding="utf-8") as file:
        file.write(new_source)
    return new_file_path
