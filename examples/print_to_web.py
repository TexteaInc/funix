from funix import funix
@funix(
    print_to_web=True
)
def my_main(x: str="123", debug:bool=True) -> None:
    if debug:
        print("### This is a debug message.")

    return x 
