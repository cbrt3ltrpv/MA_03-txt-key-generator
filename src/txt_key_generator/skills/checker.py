from __future__ import annotations

import re

from txt_key_generator.schemas import CheckReport, CheckViolation, GenerationKeys


WORD_RE = re.compile(r"[\wА-Яа-яЁё]+(?:[-'][\wА-Яа-яЁё]+)?", re.UNICODE)


class WordCountCheckSkill:
    def __init__(self, tolerance_ratio: float = 0.1) -> None:
        self.tolerance_ratio = tolerance_ratio

    def count(self, text: str) -> int:
        return len(WORD_RE.findall(text))

    def check(self, text: str, target_word_count: int | None) -> CheckViolation | None:
        if target_word_count is None:
            return None
        actual = self.count(text)
        tolerance = max(5, round(target_word_count * self.tolerance_ratio))
        if abs(actual - target_word_count) <= tolerance:
            return None
        return CheckViolation(
            criterion="word_count",
            description=(
                f"Текст содержит {actual} слов, целевой объем {target_word_count} "
                f"слов с допуском +/-{tolerance}."
            ),
            severity="high",
        )


class KeywordCoverageCheckSkill:
    def check(self, text: str, keywords: list[str]) -> list[CheckViolation]:
        normalized_text = text.casefold()
        missing = [keyword for keyword in keywords if keyword.casefold() not in normalized_text]
        if not missing:
            return []
        return [
            CheckViolation(
                criterion="keyword_coverage",
                description="Не использованы ключевые слова: " + ", ".join(missing),
                severity="high",
            )
        ]


class RedPolicyCheckSkill:
    def instructions(self, keys: GenerationKeys) -> str:
        return keys.red_policy or "Редполитика не задана."


class LanguageCheckSkill:
    def instructions(self, keys: GenerationKeys) -> str:
        return f"Проверь, что текст написан на языке: {keys.language}."


class StructureCheckSkill:
    def instructions(self, keys: GenerationKeys) -> str:
        return keys.structure or "Специальная структура не задана."


class ChecklistReportSkill:
    def merge(self, ai_report: CheckReport, deterministic: list[CheckViolation]) -> CheckReport:
        violations = [*deterministic, *ai_report.violations]
        missing_requirements = list(ai_report.missing_requirements)
        revision_instructions = list(ai_report.revision_instructions)

        for violation in deterministic:
            revision_instructions.append(violation.description)
            missing_requirements.append(violation.criterion)

        passed = ai_report.passed and not deterministic and not violations
        penalty = min(0.5, len(deterministic) * 0.15)
        score = max(0.0, ai_report.score - penalty)

        return CheckReport(
            passed=passed,
            score=score,
            violations=violations,
            missing_requirements=missing_requirements,
            revision_instructions=revision_instructions,
            clarifying_questions=ai_report.clarifying_questions,
        )

