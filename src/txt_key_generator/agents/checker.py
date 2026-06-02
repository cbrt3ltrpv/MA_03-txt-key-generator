from txt_key_generator.ai import StructuredAIClient, model_dump_json
from txt_key_generator.schemas import CheckReport, GenerationKeys
from txt_key_generator.skills.checker import (
    ChecklistReportSkill,
    KeywordCoverageCheckSkill,
    LanguageCheckSkill,
    RedPolicyCheckSkill,
    StructureCheckSkill,
    WordCountCheckSkill,
)


class CheckerAgent:
    def __init__(
        self,
        ai_client: StructuredAIClient,
        word_count: WordCountCheckSkill | None = None,
        keyword_coverage: KeywordCoverageCheckSkill | None = None,
        red_policy: RedPolicyCheckSkill | None = None,
        language: LanguageCheckSkill | None = None,
        structure: StructureCheckSkill | None = None,
        checklist: ChecklistReportSkill | None = None,
    ) -> None:
        self.ai_client = ai_client
        self.word_count = word_count or WordCountCheckSkill()
        self.keyword_coverage = keyword_coverage or KeywordCoverageCheckSkill()
        self.red_policy = red_policy or RedPolicyCheckSkill()
        self.language = language or LanguageCheckSkill()
        self.structure = structure or StructureCheckSkill()
        self.checklist = checklist or ChecklistReportSkill()

    async def check(self, text: str, keys: GenerationKeys) -> CheckReport:
        deterministic = [
            violation
            for violation in [
                self.word_count.check(text, keys.target_word_count),
                *self.keyword_coverage.check(text, keys.keywords),
            ]
            if violation is not None
        ]
        ai_report = await self.ai_client.parse(
            system_prompt=(
                "Ты агент checker. Проверяй текст строго по ключам, редполитике, "
                "языку, структуре и ограничениям. Не исправляй текст. "
                "Верни только структурированный CheckReport."
            ),
            user_prompt=self._build_prompt(text, keys),
            response_model=CheckReport,
        )
        return self.checklist.merge(ai_report, deterministic)

    def _build_prompt(self, text: str, keys: GenerationKeys) -> str:
        return f"""
Ключи генерации:
{model_dump_json(keys)}

Проверки:
- {self.language.instructions(keys)}
- Редполитика: {self.red_policy.instructions(keys)}
- Структура: {self.structure.instructions(keys)}
- Запрещенные элементы: {", ".join(keys.must_avoid) or "нет"}
- Обязательные элементы: {", ".join(keys.must_include) or "нет"}
- Пользовательские ключи из GenerationKeys тоже обязательны к проверке.

Текст для проверки:
{text}
""".strip()
