import funix 


y = "Y is in its default value. Please change it using set_word() in Page 1."

@funix.funix(
    title="Demo for multipage and Sessions/states: Page 1",
    description="""
This demo shows how to pass data between pages.

Each Funix-decorated function becomes a page. So just use a global variable to pass data between pages. The global variable is automatically sessionized to separate connections from different browser windows. 

After executing this page, you can go to Page 2 to call `get_y()` to display the changed global variable `y`. 

Another example is OpenAI demos where OpenAI key is set in one page while DallE and GPT3 demos use the key in other pages. Check them out using the function selector above""",
)
def set_y(x: str="Haha") -> str:
    global y
    y = x 
    return "The value of the sessionized global variable y has been changed. Now go to Page 2 to see the effect. "


@funix.funix(
        title="Demo for multipage and Sessions/States: Page 2",
    description="""    
Click the Run button to retrieve the sessionized global variabel `y` set in Page 1 using `set_y()`. If you have NOT run Page 1 or `set_y()`, then after clicking the Run button, you will see the default value of `y`. 
""",
)
def get_y() -> str:
    return y 