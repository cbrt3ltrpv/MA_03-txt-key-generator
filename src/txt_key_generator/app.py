from txt_key_generator.agents.checker import CheckerAgent
from txt_key_generator.agents.generator import GeneratorAgent
from txt_key_generator.agents.reviser import ReviserAgent
from txt_key_generator.ai import OpenAIResponsesClient
from txt_key_generator.config import Settings
from txt_key_generator.orchestrator import GenerationOrchestrator
from txt_key_generator.skills.key_extraction import KeyExtractionSkill
from txt_key_generator.skills.system import KeyValidationSkill


def build_orchestrator(settings: Settings) -> GenerationOrchestrator:
    ai_client = OpenAIResponsesClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )
    return GenerationOrchestrator(
        key_extractor=KeyExtractionSkill(ai_client),
        key_validator=KeyValidationSkill(),
        generator=GeneratorAgent(ai_client),
        checker=CheckerAgent(ai_client),
        reviser=ReviserAgent(ai_client),
        max_revision_cycles=settings.max_revision_cycles,
    )

