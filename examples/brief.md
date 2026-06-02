# Sample Generation Brief

This file is a ready-to-send input for the Telegram bot. Copy the text into a
message or upload this Markdown file to exercise the key-extraction,
generator/checker/reviser, and custom-parameter paths.

```text
Тема: запуск CRM для отдела продаж
Язык: русский
Объем: 500 слов
Ключевые слова: CRM, автоматизация, продажи, воронка
Редполитика: без канцелярита, короткие абзацы, конкретные формулировки
Аудитория: руководители отделов продаж в B2B-компаниях
Тон: деловой, спокойный
Структура: заголовок, вступление, 3 смысловых блока, CTA
Обязательно включить: выгоды для руководителя, пример автоматизации рутины
Избегать: обещаний мгновенного роста, технического жаргона
CTA: записаться на демо
Platform: Telegram post
Forbidden words: революционный, уникальный, гарантированный
```

Expected workflow:

1. `KeyExtractionSkill` maps the known fields into `GenerationKeys` and keeps
   `CTA`, `Platform`, and `Forbidden words` as custom parameters.
2. `KeyValidationSkill` confirms the required fields: topic, language, and
   target word count.
3. `GeneratorAgent` creates a first draft.
4. `CheckerAgent` combines deterministic word-count and keyword checks with
   model-backed review of tone, structure, red policy, and custom parameters.
5. `ReviserAgent` rewrites failed drafts until the checker passes or
   `MAX_REVISION_CYCLES` is reached.

If you need to test clarification handling, remove `Язык` or `Объем` before
sending the brief.
