import funix 


y = "The default value of y."

description = """
This demo shows how to pass data between pages.

Each Funix-decorated function becomes a page. So just use a global variable to pass data between pages. The global variable is automatically sessionized to separate connections from different browser windows. 

After executing this page, you can go to Page 2 to call `get_y()` to display the changed global variable `y`. 

Another example is OpenAI demos where OpenAI key is set in one page while DallE and GPT3 demos use the key in other pages. Check them out using the function selector above"""

@funix.funix(
    title="Session/state: set",
    description="Set the global variable `y` to a new value. ",
)
def set_y(x: str="123") -> str:
    global y
    y = x 
    return "Y has been changed. Now check it in the get_y() page."


@funix.funix(
        title="Session/State: get",
    description="""    
Retrieve the sessionized global variable `y`. If you have NOT run `set_y()`, then after clicking the Run button, you will see the default value of `y`. 
""",
)
def get_y() -> str:
    return y 