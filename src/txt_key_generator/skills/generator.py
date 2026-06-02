from txt_key_generator.schemas import GenerationKeys


class StructurePlanningSkill:
    def build_plan(self, keys: GenerationKeys) -> str:
        if keys.structure:
            return f"Следуй структуре: {keys.structure}"
        return "Построй логичный текст с началом, основной частью и завершением."


class KeywordPlacementSkill:
    def instructions(self, keys: GenerationKeys) -> str:
        if not keys.keywords:
            return "Ключевые слова не заданы."
        keywords = ", ".join(keys.keywords)
        return (
            "Равномерно и естественно используй ключевые слова. "
            f"Ключевые слова: {keywords}."
        )


class LanguageToneSkill:
    def instructions(self, keys: GenerationKeys) -> str:
        parts = [
            f"Язык: {keys.language or 'не задан'}",
            f"Тон: {keys.tone or 'нейтральный'}",
            f"Аудитория: {keys.audience or 'широкая'}",
        ]
        return "\n".join(parts)


class PromptBuildSkill:
    def __init__(
        self,
        structure_planning: StructurePlanningSkill | None = None,
        keyword_placement: KeywordPlacementSkill | None = None,
        language_tone: LanguageToneSkill | None = None,
    ) -> None:
        self.structure_planning = structure_planning or StructurePlanningSkill()
        self.keyword_placement = keyword_placement or KeywordPlacementSkill()
        self.language_tone = language_tone or LanguageToneSkill()

    def build(self, keys: GenerationKeys) -> str:
        requirements = "\n".join(keys.additional_requirements) or "Нет дополнительных требований."
        must_include = ", ".join(keys.must_include) or "нет"
        must_avoid = ", ".join(keys.must_avoid) or "нет"
        return f"""
Создай текст по параметрам.

Тема: {keys.topic}
Целевой объем: {keys.target_word_count} слов
Редполитика: {keys.red_policy or "не задана"}
{self.language_tone.instructions(keys)}
{self.structure_planning.build_plan(keys)}
{self.keyword_placement.instructions(keys)}

Обязательно включить: {must_include}
Избегать: {must_avoid}
Дополнительные требования:
{requirements}
""".strip()

