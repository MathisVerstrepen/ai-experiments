from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
import os
from typing import cast, Type, TypeVar
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


def run_llm(user_prompt: str, model: str, system_prompt: str = "") -> str:
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

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
    )

    content = response.choices[0].message.content
    if content is None:
        raise ValueError("No content in response from LLM")
    return content


T = TypeVar("T", bound=BaseModel)


def run_llm_with_schema(
    user_prompt: str, model: str, schema: Type[T], system_prompt: str = ""
) -> T:
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

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema.__name__,
                "strict": True,
                "schema": schema.model_json_schema(),
            },
        },
    )

    content = response.choices[0].message.content
    if content is None:
        raise ValueError("No content in response")
    return schema.model_validate_json(content)
