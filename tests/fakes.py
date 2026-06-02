from collections import deque
from typing import TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class FakeAIClient:
    def __init__(self, responses: list[BaseModel]) -> None:
        self.responses = deque(responses)
        self.calls: list[tuple[str, str, type[BaseModel]]] = []

    async def parse(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        self.calls.append((system_prompt, user_prompt, response_model))
        if not self.responses:
            raise AssertionError("No fake AI responses left.")
        response = self.responses.popleft()
        return response_model.model_validate(response.model_dump())

