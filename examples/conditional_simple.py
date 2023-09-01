import typing 

import funix

@funix.funix(
    widgets={"prompt":"textarea", "model": "radio"}, 
    conditional_visible=[
        {
            "when": {"show_advanced": True,}, 
            "show": ["max_tokens", "model", "openai_key"]
        }
    ]
)
def ChatGPT_advanced(prompt: str, 
        show_advanced: bool = False,
        model : typing.Literal['gpt-3.5-turbo', 'gpt-3.5-turbo-0301']= 'gpt-3.5-turbo',
        max_tokens: range(100, 200, 20)=140,
        openai_key: funix.hint.StrPassword = "",)  -> str:      

    completion = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        model=model, 
        max_tokens=max_tokens,
    )
    return completion["choices"][0]["message"]["content"]