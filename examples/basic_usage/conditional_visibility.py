import typing 

import ipywidgets

import funix

@funix.funix(
    widgets={"prompt":"textarea"}, 
    conditional_visible=[
        {
            "when": {"show_advanced": True,}, 
            "show": ["max_tokens", "model", "openai_key"]
        }
    ]
)
def conditional_visible(prompt: str, 
        show_advanced: bool = False,
        model : typing.Literal['gpt-3.5-turbo', 'gpt-3.5-turbo-0301']= 'gpt-3.5-turbo',
        max_tokens: range(100, 200, 20)=140,
        # openai_key: ipywidgets.Password = "",)  -> str:      
        # BUG: Reported elsewhere as well. If I replace the type to ipywidgets.Password, I will get an error at the frontend: Unsupported field schema for field root_openai_key: Unknown field type str.
        openai_key: funix.hint.StrPassword = "",)  -> str:      


    completion = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        model=model, 
        max_tokens=max_tokens,
    )
    return completion["choices"][0]["message"]["content"]