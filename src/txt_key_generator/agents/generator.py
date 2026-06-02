from txt_key_generator.ai import StructuredAIClient
from txt_key_generator.schemas import GeneratedDraft, GenerationKeys
from txt_key_generator.skills.generator import PromptBuildSkill


class GeneratorAgent:
    def __init__(
        self,
        ai_client: StructuredAIClient,
        prompt_builder: PromptBuildSkill | None = None,
    ) -> None:
        self.ai_client = ai_client
        self.prompt_builder = prompt_builder or PromptBuildSkill()

    async def generate(self, keys: GenerationKeys) -> GeneratedDraft:
        return await self.ai_client.parse(
            system_prompt=(
                "Ты агент generator. Создавай только текст по заданным ключам. "
                "Ответ должен соответствовать схеме GeneratedDraft."
            ),
            user_prompt=self.prompt_builder.build(keys),
            response_model=GeneratedDraft,
        )

