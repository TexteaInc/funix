import openai 
openai.api_key = os.environ.get("OPENAI_KEY")

import funix 

@funix.funix(
        description="""Try the **ChatGPT** app in [Funix](http://funix.io)""",
        argument_labels = {
            "prompt" : "_What do you wanna ask?_",
            "max_tokens": "**Length** of the answer",
            "show_advanced": "Show advanced options",
            "openai_key": "Use your own OpenAI key",
            "model": "Choose a model",
        },
        widgets={"openai_key": "password", "model": "radio",
                 "show_advanced": "checkbox", "show_verbose": "switch"},
        conditional_visible=[
            {"when": {"show_advanced": True,}, 
             "show": ["max_tokens", "model", "openai_key"]}
        ],
        show_source=True 
)
def ChatGPT_advanced(prompt: str, 
            show_advanced: bool = False,
            model : typing.Literal['gpt-3.5-turbo', 'gpt-3.5-turbo-0301']= 'gpt-3.5-turbo',
            max_tokens: range(100, 500, 50)=150,
            openai_key: str = "use environment variable",)  -> str:      
    if openai_key != "use environment variable":     
        openai.api_key = openai_key
    completion = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        model=model, 
        max_tokens=max_tokens,
    )
    return completion["choices"][0]["message"]["content"]