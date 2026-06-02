from txt_key_generator.agents.checker import CheckerAgent
from txt_key_generator.agents.generator import GeneratorAgent
from txt_key_generator.agents.reviser import ReviserAgent
from txt_key_generator.schemas import CheckReport, GenerationKeys, GenerationResult
from txt_key_generator.skills.key_extraction import KeyExtractionSkill
from txt_key_generator.skills.system import KeyValidationSkill


class GenerationOrchestrator:
    def __init__(
        self,
        key_extractor: KeyExtractionSkill,
        key_validator: KeyValidationSkill,
        generator: GeneratorAgent,
        checker: CheckerAgent,
        reviser: ReviserAgent,
        max_revision_cycles: int = 3,
    ) -> None:
        self.key_extractor = key_extractor
        self.key_validator = key_validator
        self.generator = generator
        self.checker = checker
        self.reviser = reviser
        self.max_revision_cycles = max_revision_cycles

    async def run_from_text(self, source_text: str) -> GenerationResult:
        keys = await self.key_extractor.extract(source_text)
        validation = self.key_validator.validate(keys)
        if not validation.is_complete:
            return GenerationResult(
                final_text=None,
                report=CheckReport(
                    passed=False,
                    score=0,
                    violations=[],
                    missing_requirements=validation.missing_fields,
                    revision_instructions=[],
                    clarifying_questions=validation.clarifying_questions,
                ),
                cycles_used=0,
                needs_clarification=True,
            )
        return await self.run(keys)

    async def run(self, keys: GenerationKeys) -> GenerationResult:
        draft = await self.generator.generate(keys)
        current_text = draft.text
        drafts = [current_text]
        report = await self.checker.check(current_text, keys)
        cycles_used = 1

        while not report.passed and cycles_used < self.max_revision_cycles:
            revision = await self.reviser.revise(
                text=current_text,
                keys=keys,
                report=report,
            )
            current_text = revision.text
            drafts.append(current_text)
            report = await self.checker.check(current_text, keys)
            cycles_used += 1

        return GenerationResult(
            final_text=current_text if report.passed else None,
            report=report,
            cycles_used=cycles_used,
            drafts=drafts,
            needs_clarification=not report.passed,
        )

