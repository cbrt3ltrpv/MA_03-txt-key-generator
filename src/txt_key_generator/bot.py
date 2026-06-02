from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiohttp import web

from txt_key_generator.app import build_orchestrator
from txt_key_generator.config import get_settings
from txt_key_generator.formatting import format_generation_result
from txt_key_generator.schemas import InputKind
from txt_key_generator.skills.system import (
    ErrorFormatterSkill,
    FileReaderSkill,
    InputRouterSkill,
    MessageSplitterSkill,
)


logger = logging.getLogger(__name__)


def build_router() -> Router:
    settings = get_settings()
    orchestrator = build_orchestrator(settings)
    input_router = InputRouterSkill()
    file_reader = FileReaderSkill()
    splitter = MessageSplitterSkill()
    errors = ErrorFormatterSkill()
    router = Router()

    async def answer_long(message: Message, text: str) -> None:
        for chunk in splitter.split(text):
            await message.answer(chunk)

    @router.message(Command("start"))
    async def start(message: Message) -> None:
        await message.answer(
            "Отправьте текст или TXT/MD/DOCX/PDF файл с ключами: тема, язык, "
            "количество слов, редполитика, ключевые слова и ограничения."
        )

    @router.message(Command("help"))
    async def help_message(message: Message) -> None:
        await message.answer(
            "Пример:\n"
            "Тема: запуск продукта\n"
            "Язык: русский\n"
            "Объем: 500 слов\n"
            "Ключевые слова: CRM, автоматизация, продажи\n"
            "Редполитика: без канцелярита, короткие абзацы."
        )

    @router.message(F.document)
    async def document_message(message: Message, bot: Bot) -> None:
        document = message.document
        if document is None:
            await message.answer(errors.file_read_error(ValueError("Document is missing.")))
            return

        route = input_router.route(filename=document.file_name)
        if route.kind == InputKind.UNSUPPORTED_FILE:
            await message.answer(errors.unsupported_file(route.extension))
            return

        await message.answer("Читаю файл и запускаю агентную проверку.")
        try:
            file = await bot.get_file(document.file_id)
            buffer = await bot.download_file(file.file_path)
            if buffer is None:
                raise ValueError("Telegram returned an empty file payload.")
            content = buffer.read()
            file_result = file_reader.read_bytes(
                content=content,
                filename=document.file_name or "document",
                mime_type=document.mime_type,
            )
            result = await orchestrator.run_from_text(file_result.text)
            await answer_long(message, format_generation_result(result))
        except Exception as exc:  # noqa: BLE001 - Telegram handler must report failures.
            logger.exception("Document processing failed")
            await answer_long(message, errors.file_read_error(exc))

    @router.message(F.text)
    async def text_message(message: Message) -> None:
        route = input_router.route(
            text=message.text,
            is_command=bool(message.text and message.text.startswith("/")),
        )
        if route.kind == InputKind.EMPTY:
            await message.answer("Отправьте текст с ключами или файл TXT/MD/DOCX/PDF.")
            return
        if route.kind == InputKind.COMMAND:
            return

        await message.answer("Запускаю generator -> checker -> reviser.")
        try:
            result = await orchestrator.run_from_text(message.text or "")
            await answer_long(message, format_generation_result(result))
        except Exception as exc:  # noqa: BLE001 - Telegram handler must report failures.
            logger.exception("Text processing failed")
            await answer_long(message, f"Ошибка генерации: {exc}")

    return router


async def run_polling(bot: Bot, dispatcher: Dispatcher) -> None:
    await dispatcher.start_polling(bot)


async def run_webhook(bot: Bot, dispatcher: Dispatcher) -> None:
    settings = get_settings()
    if settings.webhook_url is None:
        raise RuntimeError("WEBHOOK_URL is required when BOT_RUN_MODE=webhook.")

    await bot.set_webhook(str(settings.webhook_url))
    app = web.Application()
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    SimpleRequestHandler(dispatcher=dispatcher, bot=bot).register(app, path="/webhook")
    setup_application(app, dispatcher, bot=bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, settings.webhook_host, settings.webhook_port)
    await site.start()
    logger.info("Webhook server started on %s:%s", settings.webhook_host, settings.webhook_port)
    await asyncio.Event().wait()


async def async_main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = get_settings()
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required.")
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required.")

    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(build_router())

    if settings.bot_run_mode == "webhook":
        await run_webhook(bot, dispatcher)
    else:
        await run_polling(bot, dispatcher)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()

