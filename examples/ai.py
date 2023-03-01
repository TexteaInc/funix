from funix import funix
from funix.hint import Image
from funix import run
import openai  # pip install openai
import os

openai.api_key = os.environ.get("OPENAI_KEY")


@funix(
    description="Set OpenAI API key",
    argument_labels={
        "api_key": "API key"
    }
)
def set(api_key: str) -> str:
    if openai.api_key is None:
        openai.api_key = api_key
        return "OpenAI API key is set! You may start using AI features now."
    else:
        return "OpenAI API key is already set! Not changed."


@funix(
    description="Generate an image by prompt with DALL-E",
    argument_labels={
        "prompt": "Prompt"
    }
)
def dalle(prompt: str = "a cat") -> Image:
    response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    return response["data"][0]["url"]


@funix(
    description="Ask some question to GPT-3",
    argument_labels={
        "question": "Question"
    }
)
def chatgpt(question: str = "Who is Cauchy?") -> str:
    response = openai.Completion.create(
        engine="davinci",
        prompt="Answer the question in one sentence: " + question,
        temperature=0.5,
        max_tokens=100,
        top_p=0.3,
        frequency_penalty=0.6,
        presence_penalty=0.0,
    )
    return '{}'.format(response.choices[0].text)


if __name__ == "__main__":
    run(port=3000, main_class="ai")
