from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
import os
from typing import cast

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


def run_llm(user_prompt: str, model: str, system_prompt: str = ""):
    messages: list[ChatCompletionMessageParam] = []
    if system_prompt:
        messages.append(
            cast(
                ChatCompletionMessageParam, {"role": "system", "content": system_prompt}
            )
        )

    messages.append(
        cast(ChatCompletionMessageParam, {"role": "user", "content": user_prompt})
    )

    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
    )

    return response.choices[0].message.content
