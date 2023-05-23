"""
Experimental, AST Global preprocessing, looking to transform specific global variables into funix sessions

Limited application cases/not fully considered
"""


from ast import NodeTransformer


class GlobalChangingTransformer(NodeTransformer):
    """
    Transform the global variables into funix sessions.

    Base Class: ast.NodeTransformer
    """

    def __init__(self, user_id: str, global_variables: list[str]):
        """
        Create the transformer.

        Parameters:
            user_id (str): The user id.
            global_variables (list[str]): The global variables to transform.
        """
        super().__init__()
        self.user_id = user_id
        self.global_variables = global_variables
