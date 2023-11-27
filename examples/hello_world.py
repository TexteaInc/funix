import funix     # This line can be commented out in the lazy mode of funix. 
@funix.funix()   # This line can be commented out in the lazy mode of funix.
def hello_world(name: str="Funix") -> str:
    return f"Hello {name}!"