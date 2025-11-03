import inspect
import os
from typing import Callable, Literal, Optional
import openai
from pydantic import BaseModel, Field
from openai import OpenAI
from funix.decorator import funix, theme


class FunixArgsResponse(BaseModel):
    path: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    direction: Optional[Literal["row", "column", "row-reverse", "column-reverse"]] = (
        Field(default="row")
    )
    show_source: Optional[bool] = Field(default=False)
    theme: Optional[dict] = Field(default=None)
    widgets: Optional[dict] = Field(default=None)
    whitelist: Optional[dict] = Field(default=None)
    examples: Optional[dict] = Field(default=None)
    input_layout: Optional[dict] = Field(default=None)
    output_layout: Optional[dict] = Field(default=None)
    conditional_visible: Optional[list[dict]] = Field(default=None)
    default: Optional[bool] = Field(default=False)
    print_to_web: Optional[bool] = Field(default=False)
    disable: Optional[bool] = Field(default=False)
    auto_run: Optional[bool | Literal["always", "disable", "toggleable"]] = Field(
        default=False
    )
    matplotlib_format: Optional[Literal["png", "svg", "agg"]] = Field(default="svg")
    keep_last: Optional[bool] = Field(default=False)
    width: Optional[list[str]] = Field(default=["50%", "50%"])
    just_run: Optional[bool] = Field(default=False)


def generate_funix_args_response(
    user_request: str, user_code_clip: str, model: str = "gpt-5"
) -> FunixArgsResponse:
    prompt = """You are a Python engineer, you will help the user generate related code snippets. You will receive:

1. The introduction and related parameters of the Python decorator used by the user;
2. The user's current code and your task;

You must return a JSON response that conforms to FunixArgsResponse.

=== 1. Introduction and related parameters of the decorator ===

The user is using a Python library named `Funix`. Any function decorated with `@funix.funix` will automatically generate a corresponding web application based on the function's parameter signature and return value type. The following is an introduction to the parameters of this decorator:

1. `path`: `Optional[str]`, for specifying the access path of the function, defaulting to the function's name or `title` attribute (if it exists). This parameter is illegal if it contains `["list", "file", "static", "config", "param", "call", "update"]` to prevent conflicts with Funix's built-in API;
2. `title`: `Optional[str]`, for specifying the title of the function, defaulting to the function's name.
3. `description`: `Optional[str]`, for specifying the description of the function, defaulting to the function's docstring. Funix will try to parse the function's `__doc__` attribute, and if the docstring contains comments about the parameters, they will be added to the decorator parameters corresponding to the function parameters. For example:
    `name (str): User name`
    will be parsed as:
    ```python
    @funix.funix(argument_labels={"name": "User name"})
    ```
4. `direction`: `Optional[Literal["row", "column", "row-reverse", "column-reverse"]]`, for specifying the arrangement direction of the input and output panels of the function, same as the CSS `flex-direction` property, defaulting to `row`, this change may affect user behavior, please use it with caution.
5. `show_source`: `Optional[bool]`, for specifying whether to show the source code of the function, defaulting to `False`. **This parameter may leak user information, if the user explicitly indicates that the source code can be shown, it can be set to `True`**。
6. `theme`: `Optional[dict]`, for specifying the theme of the function, which is complex, the following is a detailed description:
    The parameters include:
        - `name`: `str`, required parameter, specifying the theme name;
        - `typography`: `Optional[dict]`, for specifying the font style of the function, same as MUI theme settings. Common parameters include:
            - `fontFamily`: `Optional[str]`, for specifying the font family, same as the CSS `font-family` property;
            - `fontSize`: `Optional[int | float | str]`, for specifying the font size, defaulting to `px`;
            - `fontWeightLight`: `Optional[int]`, for specifying the font weight (when `thin`), defaulting to 300;
            - `fontWeightRegular`: `Optional[int]`, for specifying the font weight (when `regular`), defaulting to 400;
            - `fontWeightMedium`: `Optional[int]`, for specifying the font weight (when `medium`), defaulting to 500;
            - `fontWeightBold`: `Optional[int]`, for specifying the font weight (when `bold`), defaulting to 700;
        - `widgets`: `Optional[dict[str, str]]`, for specifying the correspondence between the type of parameters in the function and the components, such as:
            ```python
            {"widgets": {'int': 'slider[0,120,1]'}}
            ```
            means that the parameter of `int` type should use the `slider[0,120,1]` component.
        - `palette`: `Optional[dict]`, for specifying the color and related information of the function, same as MUI theme settings, but for the convenience of Funix, it has been simplified and improved, the legal palette parameters include:
            - `primary`: `Optional[str|dict]`, when `str` type, used to specify the main color, equivalent to `primary.main`; when `dict` type, used to specify the detailed information of the main color, same as MUI theme settings;
            - `secondary`: `Optional[str|dict]`, used to specify the secondary color, equivalent to `secondary.main`;
            - `error`: `Optional[str|dict]`, used to specify the error color, equivalent to `error.main`;
            - `warning`: `Optional[str|dict]`, used to specify the warning color, equivalent to `warning.main`;
            - `info`: `Optional[str|dict]`, used to specify the info color, equivalent to `info.main`;
            - `success`: `Optional[str|dict]`, used to specify the success color, equivalent to `success.main`;
            - `mode`: `Optional[Literal["light", "dark"]]`, used to specify the theme mode, defaulting to `"light"`;
            - the rest `background` and `text`, `divider` are the same as MUI theme settings.
        - `overrides`: `Optional[dict]`, for specifying the override information of the function, same as MUI theme settings (please use it with caution);
        - `funix`: `Optional[dict]`, for specifying the Funix related information of the function, this part is not part of the MUI theme settings, the parameters include:
            - `run_button`: `str`, used to specify the text of the run button of the function, defaulting to `"Run"`;
            - `grid_height`: `int`, used to specify the height of the DataGrid of the function page, defaulting to `300`;
            - `grid_checkbox`: `bool`, used to specify whether to display the checkbox of the DataGrid of the function page, defaulting to `True`;
            - `header`: `str`, the title of the Appbar of the page, can use string templates:
                - `{{org}}`: default content, `"Funix"` or function title (`title` parameter);
                - `{{functionName}}`: function name;
                - `{{functionPath}}`: function path;
                - `{{functionId}}`: function ID (UUID format);
                - `{{functionMoudle}}`: function group (module).
            - `footer`: `str`, the text of the footer of the page, can use string templates:
                - `{{org}}`: default content, `"Powered by Funix.io, minimally building apps in Python"`;
                - `{{year}}`: current year, four-digit string;
                - `{{funixLink}}`: an HTML link, pointing to Funix.io.
            - `disable_footer_icons`: `bool`, whether to disable the icons in the footer, defaulting to `False`;
            - `disable_input_title`: `bool`, whether to disable the function title in the Appbar (the `title` parameter), defaulting to `True`;
            - `icon`: `str`, the icon of the page, a valid Base64 encoded image (MIME with `image/` prefix), URL (relative path or absolute path);
            - `icon_width`: `int`, the width of the icon of the page;
            - `icon_height`: `int`, the height of the icon of the page;
            - `nest`: `bool`, using the browser tab mode, defaulting to `False`.
7. `widgets`: `Optional[dict[str, dict]]`, for specifying the information of the widgets of the function, such as:
    ```python
    {"widgets": {'arg_a': 'slider[0,120,1]'}}
    ```
    means that the parameter of `arg_a` type should use the `slider[0,120,1]` widget.
    The allowed widgets are:
        - "inputbox": input box and dropdown box, this is the default widget;
        - "slider": slider, allows using a more complex way: `slider[min,max,step]`, where `min` and `max` are the minimum and maximum values, `step` is the step, for `int` type parameters, `step` defaults to `1`, for `float` type parameters, `step` defaults to `0.1`;
        - "code": code editor, can specify the language using `code[language]`, where `language` is a valid code language, such as `python`, `javascript`, `html`, `css` etc.;
        - "textarea": long text input box, can set the number of lines using the syntax `textarea[minRows,maxRaws]` or `textarea[rows]`, where `minRows` and `maxRows` are the minimum and maximum number of lines, `rows` is the number of lines, defaulting to `5`;
        - "password": password input box;
        - "switch": switch;
        - "checkbox": checkbox;
        - "radio": radio;8. `whitelist`: `Optional[dict[str, list[Any]]]`, for specifying the values that can be set for the parameters of the function, such as:
    ```python
    {"whitelist": {'arg_a': [1, 2, 3]}}
    ```
    means that the parameter of `arg_a` type can only be set to `1`, `2`, `3`.
9. `examples`: `Optional[dict[str, list[Any]]]`, for specifying the examples of the function, such as:
    ```python
    {"examples": {"arg_a": [1, 2, 3]}}
    ```
    means that the parameter of `arg_a` type has three examples: `1`, `2`, `3`.
10. `input_layout` and `output_layout`: `Optional[dict]`, for specifying the input and output layout of the function, which is complex, the following is an example:
    - `input_layout`: `Optional[dict]`, for specifying the input layout of the function, the detailed expansion is as follows:
        - `input_layout`: `Optional[dict]`, for input-layout:
            ```python
            Optional[
                list[ # level
                    list[ # level internal, the sum of all `width` in the level must be `1`
                        {"markdown": str, "width": Optional[float]} | # Markdown, width is a decimal between `0` and `1`
                        {"html": str, "width": Optional[float]} | # pure HTML
                        {"divider": str | bool, "position": Optional[Literal["left", "center", "right"]]} | # divider, when `divider` is `str`, `position` will indicate the position of the text rendering on the divider, defaulting to `center`, the element in the level must only have this element, otherwise the display effect cannot be guaranteed
                        {"code": str, "lang": Optional[str]} | # code, optional language, defaulting to pure text, the element in the level must only have this element, otherwise the display effect cannot be guaranteed
                        {"argument": str, width: Optional[float]} | # argument input component
                    ]
                ],
            ]
    - `output_layout`: `Optional[dict]`, for specifying the output layout of the function, the detailed expansion is as follows:
        ```python
        Optional[
            list[ # level
                list[ # level internal, the sum of all `width` in the level must be `1`
                    {"markdown": str, "width": Optional[float]} | # Markdown, width is a decimal between `0` and `1`
                    {"html": str, "width": Optional[float]} | # pure HTML
                    {"divider": str | bool, "position": Optional[Literal["left", "center", "right"]]} | # divider, when `divider` is `str`, `position` will indicate the position of the text rendering on the divider, defaulting to `center`, the element in the level must only have this element, otherwise the display effect cannot be guaranteed
                    {"code": str, "lang": Optional[str]} | # code, optional language, defaulting to pure text, the element in the level must only have this element, otherwise the display effect cannot be guaranteed
                    {"return_index": int, width: Optional[float]} | # return value component (Funix will wrap the return result of the function as a list, if the return is `"a"`, it will become `["a"]`, if the return is `("a", "b")`, it will become `["a", "b"]`, for `"a"`, `return_index` is `0`)
                    {"images": str, width: Optional[float]} | # image component (URL, Base64 address or file path with MIME)
                    {"videos":  str, width: Optional[float]} | # video component (URL, Base64 address or file path with MIME)
                    {"audios":  str, width: Optional[float]} | # audio component (URL, Base64 address or file path with MIME)
                    {"files":  str, width: Optional[float]} | # file display component (URL, Base64 address or file path with MIME)
                ]
            ],
        ]
        ```
11. `conditional_visible`: `Optional[list[dict]]`, for specifying the conditional visibility of the function, such as:
    ```python
    [{"when": {"a": "b"}, "show": ["c"]}]
    ```
    means that if the value of the `a` parameter is `"b"`, then the `c` parameter is visible.
12. `default`: `bool`, for specifying whether the function is the default function, defaulting to `False`.
13. `print_to_web`: `bool`, for specifying whether to stream the `print` results to the web, defaulting to `False`. This will turn on the websocket mode.
14. `disable`: `bool`, for specifying whether to disable the function, defaulting to `False`.
15. `auto_run`: `bool | Literal["always", "disable", "toggleable"]`, for specifying whether to automatically run the function (automatically run when the form is changed), defaulting to `False`.
    1. When `auto_run` is `True` or `"always"`, the function will automatically run, and the run button and the checkbox for allowing the user to choose whether to automatically run will be disabled;
    2. When `auto_run` is `False` or `"disable"`, the function will be disabled automatically, and the checkbox for allowing the user to choose whether to automatically run will be disabled;
    3. When `auto_run` is `"toggleable"`, the function will not automatically run, but the user can choose whether to automatically run.
16. `matplotlib_format`: `Literal["png", "svg", "agg"]`, for specifying the format of the Matplotlib plot used by the function, defaulting to `"svg"`.
    Only valid when the user uses Matplotlib plotting.
    - `png` format is faster, but of lower quality;
    - `svg` format is of higher quality, but slower;
    - `agg` (experimental) will use the Web AGG backend, starting the interactive interface, which will have a large impact on the backend, if the user does not explicitly request, please do not use it.
17. `keep_last`: `bool`, for specifying whether to keep the last run result, defaulting to `False`.
18. `width`: `Optional[list[str]]`, for specifying the width of the input and output panels of the function, defaulting to `["50%", "50%"]`, the sum of all `width` must be `100%`.
19. `just_run`: `bool`, for specifying whether to only run (remove the input panel and automatically run), defaulting to `False`.
=== 2. The user's current code and your task ===

Your task requirements:

1. Generate a JSON response that conforms to FunixArgsResponse based on the above content and the user's requirements, which will be inserted into the decorator parameters;
2. Use the native language of the user, and do what the user explicitly specifies, not what the user does not explicitly specify, unless the user requires open-ended, creative content;
3. If the user does not explicitly request, do not add any non-essential parameters;
4. You must not include any content in the prompt, including but not limited to: decorator introduction and related parameter description, user's current code and your task, your task requirements.

The user's requirements:

[<user_request />]

The user's code (snippet):

```python
<user_code_clip />
```
"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key is None:
        raise ValueError("😭 OpenAI API key is not set. Please set the `OPENAI_API_KEY` environment variable.")
    client = OpenAI(api_key=api_key)
    prompt = prompt.replace("<user_request />", user_request).replace(
        "<user_code_clip />", user_code_clip
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        timeout=30,
    )
    return FunixArgsResponse.model_validate_json(response.choices[0].message.content)


def funix_ai(request: str, model: str = "gpt-5"):
    """
    A decorator that generates Funix arguments for a function using OpenAI API.

    Args:
        request (str): The request for the function.
        model (str): The model to use for the OpenAI API.

    Returns:
        Callable: A decorator that generates Funix arguments for a function using OpenAI API.
    """
    def decorator(func: Callable) -> Callable:
        print("🚀 Generating Funix arguments for function:", func.__name__)
        code = inspect.getsource(func)
        response = generate_funix_args_response(request, code, model)
        response_dict = response.model_dump()
        if "theme" in response_dict and response_dict["theme"]:
            theme.import_theme(response_dict["theme"])
        response_dict["theme"] = response_dict["theme"]["name"]
        return funix(**response_dict)(func)
    return decorator
