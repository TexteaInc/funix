import funix 


@funix.funix(
    title="""Automatic vectorization""",
    description="""Funix automatically vectorizes a scalar function on arguments declared to be cells in a sheet. See the source code for details. In this example, arguments `a` and `b` are declared so and hence the function is partially mapped onto them -- partial because the argument `isAdd` is not declared so. 
    
**Usage:** Simply click 'Add a row' button to create new rows and then double-click cells to add numeric values. Then click the Run button. In the output panel, click the `Sheet` radio button to view the result as a headed table.
        
    """,
    widgets={
        ("a", "b"): "sheet",
    },
    treat_as={("a", "b"): "cell"},
    show_source=True,
)
def cell_test(a: int, b: int, isAdd: bool) -> int:
    return a + b if isAdd else a - b