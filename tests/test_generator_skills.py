from txt_key_generator.schemas import CustomParameter, GenerationKeys
from txt_key_generator.skills.generator import PromptBuildSkill


def test_prompt_builder_includes_custom_parameters() -> None:
    keys = GenerationKeys(
        topic="CRM",
        language="ru",
        target_word_count=100,
        custom_parameters=[
            CustomParameter(
                name="CTA",
                value="Записаться на демо",
                description="призыв в конце текста",
            )
        ],
    )

    prompt = PromptBuildSkill().build(keys)

    assert "Пользовательские ключи" in prompt
    assert "CTA: Записаться на демо" in prompt
    assert "призыв в конце текста" in prompt

