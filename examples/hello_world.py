# import funix
# @funix.funix()

# The two lines above can be commented out if using the lazy model, i.e., $ funix -l hello_world.py 

def hello_world(name: str="Funix") -> str:
    return f"Hello {name}!"