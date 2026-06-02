from txt_key_generator.agents.checker import CheckerAgent
from txt_key_generator.agents.generator import GeneratorAgent
from txt_key_generator.agents.reviser import ReviserAgent
from txt_key_generator.orchestrator import GenerationOrchestrator
from txt_key_generator.schemas import (
    CheckReport,
    CheckViolation,
    GeneratedDraft,
    GenerationKeys,
    RevisionResult,
)
from txt_key_generator.skills.key_extraction import KeyExtractionSkill
from txt_key_generator.skills.system import KeyValidationSkill
from tests.fakes import FakeAIClient


def complete_keys() -> GenerationKeys:
    return GenerationKeys(
        keywords=[],
        topic="CRM",
        language="ru",
        target_word_count=10,
    )


async def test_orchestrator_stops_after_successful_check() -> None:
    ai = FakeAIClient(
        [
            GeneratedDraft(text="one two three four five six seven eight nine ten"),
            CheckReport(passed=True, score=1),
        ]
    )
    orchestrator = GenerationOrchestrator(
        key_extractor=KeyExtractionSkill(ai),
        key_validator=KeyValidationSkill(),
        generator=GeneratorAgent(ai),
        checker=CheckerAgent(ai),
        reviser=ReviserAgent(ai),
        max_revision_cycles=3,
    )

    result = await orchestrator.run(complete_keys())

    assert result.final_text is not None
    assert result.cycles_used == 1
    assert result.needs_clarification is False


async def test_orchestrator_revises_until_check_passes() -> None:
    ai = FakeAIClient(
        [
            GeneratedDraft(text="too short"),
            CheckReport(
                passed=False,
                score=0.4,
                violations=[CheckViolation(criterion="style", description="Bad style")],
                revision_instructions=["Make it better"],
            ),
            RevisionResult(text="one two three four five six seven eight nine ten"),
            CheckReport(passed=True, score=1),
        ]
    )
    orchestrator = GenerationOrchestrator(
        key_extractor=KeyExtractionSkill(ai),
        key_validator=KeyValidationSkill(),
        generator=GeneratorAgent(ai),
        checker=CheckerAgent(ai),
        reviser=ReviserAgent(ai),
        max_revision_cycles=3,
    )

    result = await orchestrator.run(complete_keys())

    assert result.final_text is not None
    assert result.cycles_used == 2
    assert len(result.drafts) == 2


async def test_orchestrator_stops_after_three_failed_cycles() -> None:
    ai = FakeAIClient(
        [
            GeneratedDraft(text="bad"),
            CheckReport(
                passed=False,
                score=0.2,
                violations=[CheckViolation(criterion="quality", description="Bad")],
                revision_instructions=["Fix"],
                clarifying_questions=["Какой стиль нужен?"],
            ),
            RevisionResult(text="bad again"),
            CheckReport(
                passed=False,
                score=0.2,
                violations=[CheckViolation(criterion="quality", description="Still bad")],
                revision_instructions=["Fix again"],
            ),
            RevisionResult(text="bad final"),
            CheckReport(
                passed=False,
                score=0.2,
                violations=[CheckViolation(criterion="quality", description="Still bad")],
                revision_instructions=["Need clarification"],
                clarifying_questions=["Уточните редполитику."],
            ),
        ]
    )
    orchestrator = GenerationOrchestrator(
        key_extractor=KeyExtractionSkill(ai),
        key_validator=KeyValidationSkill(),
        generator=GeneratorAgent(ai),
        checker=CheckerAgent(ai),
        reviser=ReviserAgent(ai),
        max_revision_cycles=3,
    )

    result = await orchestrator.run(complete_keys())

    assert result.final_text is None
    assert result.cycles_used == 3
    assert result.needs_clarification is True
    assert result.report.clarifying_questions


async def test_orchestrator_requests_clarification_for_incomplete_keys() -> None:
    ai = FakeAIClient([GenerationKeys(topic="CRM")])
    orchestrator = GenerationOrchestrator(
        key_extractor=KeyExtractionSkill(ai),
        key_validator=KeyValidationSkill(),
        generator=GeneratorAgent(ai),
        checker=CheckerAgent(ai),
        reviser=ReviserAgent(ai),
        max_revision_cycles=3,
    )

    result = await orchestrator.run_from_text("Тема: CRM")

    assert result.final_text is None
    assert result.needs_clarification is True
    assert "language" in result.report.missing_requirements

