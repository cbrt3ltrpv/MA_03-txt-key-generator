# Telegram AI Agent Text Generator

Telegram bot that accepts text or `TXT/MD/DOCX/PDF` files, extracts generation keys, and runs a 3-agent workflow:

1. `generator` creates a draft.
2. `checker` validates the draft.
3. `reviser` fixes violations for up to 3 cycles.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Fill `.env`, then run:

```bash
txt-key-generator-bot
```

Use `BOT_RUN_MODE=polling` for local/VPS startup or `BOT_RUN_MODE=webhook` with `WEBHOOK_URL` for production webhook mode.

