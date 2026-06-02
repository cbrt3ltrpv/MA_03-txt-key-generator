from txt_key_generator.schemas import CheckReport, GenerationKeys


class RevisionPlanSkill:
    def build(self, report: CheckReport) -> str:
        if not report.revision_instructions:
            return "Сохрани текст без существенных изменений."
        return "\n".join(f"- {item}" for item in report.revision_instructions)


class ConstraintPreservationSkill:
    def instructions(self, keys: GenerationKeys) -> str:
        keywords = ", ".join(keys.keywords) or "нет"
        avoid = ", ".join(keys.must_avoid) or "нет"
        return (
            "Сохрани смысл и уже выполненные требования. "
            f"Не потеряй ключевые слова: {keywords}. "
            f"Не используй запрещенное: {avoid}."
        )


class TextRewriteSkill:
    def build_prompt(self, text: str, keys: GenerationKeys, report: CheckReport) -> str:
        revision_plan = RevisionPlanSkill().build(report)
        preservation = ConstraintPreservationSkill().instructions(keys)
        return f"""
Исправь текст по отчету проверки.

План правок:
{revision_plan}

Ограничения:
{preservation}

Исходный текст:
{text}
""".strip()

