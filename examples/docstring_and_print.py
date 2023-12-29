from funix import funix

@funix(
    print_to_web=True
)
def foo() -> None:
    """
    ## What a great app in Funix! 
    
    Funix won't let your docstring go to waste.
    """
    print("It supports **Markdown**.")
    print ("And <b>HTML</b>.")
    return None