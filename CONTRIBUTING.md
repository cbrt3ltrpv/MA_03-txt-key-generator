# Contributing

This project is a Telegram bot around a generator/checker/reviser workflow.
Changes should keep the deterministic skills testable and the model-backed
agents constrained by typed schemas.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Fill `.env` with local Telegram and OpenAI credentials before running the bot.

## Development Checks

Run the test suite before opening a pull request:

```bash
python -m pytest
```

For behavior changes, also run at least one manual Telegram text request. For
file parsing changes, upload a representative `TXT`, `MD`, `DOCX`, or text-based
`PDF` file.

## Change Guidelines

- Keep schema changes in `src/txt_key_generator/schemas.py` backwards-aware.
- Keep deterministic parsing, validation, splitting, and checker helpers covered
  by unit tests.
- Do not add new required environment variables without documenting them in
  `.env.example` and `README.md`.
- Preserve the human-review assumption for generated content.
- Avoid committing real bot tokens, OpenAI keys, generated drafts with private
  customer data, or local `.env` files.

## Pull Requests

Use the pull request template and include:

- a concise summary of the bot or workflow behavior changed;
- tests and manual checks performed;
- any runtime impact for polling, webhook mode, credentials, model selection, or
  revision-cycle behavior;
- known risks and an appropriate rollback path.
