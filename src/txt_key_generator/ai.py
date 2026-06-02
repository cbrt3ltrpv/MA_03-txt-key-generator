from __future__ import annotations

import json
from typing import Any, Protocol, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class StructuredAIClient(Protocol):
    async def parse(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        """Return a Pydantic object parsed from model output."""


class OpenAIResponsesClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)

    async def parse(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        try:
            response = await self.client.responses.parse(
                model=self.model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                text_format=response_model,
            )
            parsed = getattr(response, "output_parsed", None)
            if parsed is None:
                output_text = getattr(response, "output_text", "")
                return response_model.model_validate_json(output_text)
            return parsed
        except AttributeError:
            return await self._parse_with_json_schema(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=response_model,
            )

    async def _parse_with_json_schema(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        response = await self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": response_model.__name__,
                    "schema": response_model.model_json_schema(),
                    "strict": True,
                }
            },
        )
        output_text = getattr(response, "output_text", "")
        return response_model.model_validate_json(output_text)


def model_dump_json(data: BaseModel | dict[str, Any]) -> str:
    if isinstance(data, BaseModel):
        return data.model_dump_json(indent=2)
    return json.dumps(data, ensure_ascii=False, indent=2)

