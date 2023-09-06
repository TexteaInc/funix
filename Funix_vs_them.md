# Funix vs. them

Here we will show how Funix and other solutions compare in <s>building apps in Python</s> transforming a Python function to a web app. 


## Hello, world! 

In Funix, all you need is a simple function: 

```py
def hello(your_name: str) -> str:
    return f"Hello, {your_name}."
```

Run the magic command `funix hello.py -l` and you get a web app. 

In Gradio, this is the code ([source](https://www.gradio.app/docs/interface)): 

```py
import gradio as gr

def hello(your_name: str) -> str: # type hint is optional 
    return f"Hello, {your_name}."

demo = gr.Interface(fn=hello, inputs="text", outputs="text")

if __name__ == "__main__":
    demo.launch()   
```

In Streamlit, this is the code: 
```py

import streamlit as st

def hello(your_name: str) -> str:
    return f"Hello, {your_name}."

col1, col2 = st.columns(2)

with col1:
    your_name = st.text_input('Your name')

with col2:
    st.write(hello(your_name))
```

Then you need to run the command `streamlit run THIS_FILE.py` 

### Takeaway
Streamlit requires you to manually create widgets. It does not by default creates the input and output panel. So you write the most amount of code in Streamlit. Gradio leverages the types of `inputs` and `outputs`to pick the UI widgets. But Funix goes on step furthe by simply using Python's native type hint. 


## Hangman 

Here is a comparison between Funix and Gradio in building a hangman game app. 
![Hangman Funix vs Gradio](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/hangman_gradio_vs_funix.png)

The resulting UI from Funix does not look too bad! 
![Hangman in Funix](https://raw.githubusercontent.com/TexteaInc/funix-doc/main/screenshots/hangman.png)

### Takeaway
Funix code is much shorter than Gradio one. In the Gradio's case, because a state variable `used_letters_var` is maintained and should not become a user input, the layout has to be manually arranged instead of being automatically generated. 
But Funix take a slightly risky approach by treating such a variable as a global variable (using Python's built-in keyword `global`) so it does not have to become part of the argument/input of the core function. 
