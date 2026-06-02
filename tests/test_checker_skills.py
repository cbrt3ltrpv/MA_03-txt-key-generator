from txt_key_generator.schemas import CheckReport, CheckViolation
from txt_key_generator.skills.checker import (
    ChecklistReportSkill,
    KeywordCoverageCheckSkill,
    WordCountCheckSkill,
)


def test_word_count_check_passes_with_tolerance() -> None:
    violation = WordCountCheckSkill(tolerance_ratio=0.1).check("one two three", 3)

    assert violation is None


def test_word_count_check_fails_outside_tolerance() -> None:
    violation = WordCountCheckSkill(tolerance_ratio=0.1).check("one two three", 20)

    assert violation is not None
    assert violation.criterion == "word_count"


def test_keyword_coverage_reports_missing_keywords() -> None:
    violations = KeywordCoverageCheckSkill().check("CRM для продаж", ["CRM", "analytics"])

    assert len(violations) == 1
    assert "analytics" in violations[0].description


def test_checklist_report_merges_deterministic_violations() -> None:
    ai_report = CheckReport(passed=True, score=1)
    merged = ChecklistReportSkill().merge(
        ai_report,
        [CheckViolation(criterion="word_count", description="Bad count")],
    )

    assert merged.passed is False
    assert merged.score < 1
    assert merged.revision_instructions == ["Bad count"]

