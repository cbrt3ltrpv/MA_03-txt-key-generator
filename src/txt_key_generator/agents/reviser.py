from txt_key_generator.ai import StructuredAIClient, model_dump_json
from txt_key_generator.schemas import CheckReport, GenerationKeys, RevisionResult
from txt_key_generator.skills.reviser import TextRewriteSkill


class ReviserAgent:
    def __init__(
        self,
        ai_client: StructuredAIClient,
        rewrite_skill: TextRewriteSkill | None = None,
    ) -> None:
        self.ai_client = ai_client
        self.rewrite_skill = rewrite_skill or TextRewriteSkill()

    async def revise(
        self,
        *,
        text: str,
        keys: GenerationKeys,
        report: CheckReport,
    ) -> RevisionResult:
        return await self.ai_client.parse(
            system_prompt=(
                "Ты агент reviser. Исправляй текст только по отчету checker и "
                "сохраняй выполненные требования. Верни RevisionResult."
            ),
            user_prompt=(
                self.rewrite_skill.build_prompt(text, keys, report)
                + "\n\nКлючи:\n"
                + model_dump_json(keys)
            ),
            response_model=RevisionResult,
        )

