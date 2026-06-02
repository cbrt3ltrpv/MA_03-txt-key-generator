from txt_key_generator.ai import StructuredAIClient
from txt_key_generator.schemas import GenerationKeys


class KeyExtractionSkill:
    def __init__(self, ai_client: StructuredAIClient) -> None:
        self.ai_client = ai_client

    async def extract(self, source_text: str) -> GenerationKeys:
        return await self.ai_client.parse(
            system_prompt=(
                "Ты skill KeyExtractionSkill. Извлеки из свободного текста параметры "
                "для генерации. Если параметр не указан, оставь null или пустой список. "
                "Не придумывай отсутствующие требования."
            ),
            user_prompt=source_text,
            response_model=GenerationKeys,
        )

