from io import BytesIO

from docx import Document
from pypdf import PdfWriter

from txt_key_generator.schemas import GenerationKeys, InputKind
from txt_key_generator.skills.system import (
    FileReaderSkill,
    InputRouterSkill,
    KeyValidationSkill,
    MessageSplitterSkill,
)


def test_input_router_routes_text() -> None:
    route = InputRouterSkill().route(text="Тема: CRM")

    assert route.kind == InputKind.TEXT_REQUEST


def test_input_router_rejects_unsupported_file() -> None:
    route = InputRouterSkill().route(filename="image.png")

    assert route.kind == InputKind.UNSUPPORTED_FILE
    assert route.extension == "png"


def test_key_validation_requires_core_fields() -> None:
    result = KeyValidationSkill().validate(GenerationKeys(keywords=["CRM"]))

    assert result.is_complete is False
    assert "topic" in result.missing_fields
    assert "language" in result.missing_fields
    assert "target_word_count" in result.missing_fields
    assert result.clarifying_questions


def test_key_validation_detects_conflicts() -> None:
    keys = GenerationKeys(
        topic="CRM",
        language="ru",
        target_word_count=100,
        keywords=["sales"],
        must_avoid=["sales"],
    )

    result = KeyValidationSkill().validate(keys)

    assert result.is_complete is False
    assert result.conflicts


def test_message_splitter_respects_limit() -> None:
    chunks = MessageSplitterSkill(max_length=10).split("one two three four five")

    assert all(len(chunk) <= 10 for chunk in chunks)
    assert len(chunks) > 1


def test_file_reader_reads_txt() -> None:
    result = FileReaderSkill().read_bytes("Привет".encode(), "keys.txt")

    assert result.text == "Привет"
    assert result.metadata.extension == "txt"


def test_file_reader_reads_md() -> None:
    result = FileReaderSkill().read_bytes(b"# Title\nBody", "keys.md")

    assert "Title" in result.text
    assert result.metadata.extension == "md"


def test_file_reader_reads_docx() -> None:
    document = Document()
    document.add_paragraph("Тема: CRM")
    buffer = BytesIO()
    document.save(buffer)

    result = FileReaderSkill().read_bytes(buffer.getvalue(), "keys.docx")

    assert "CRM" in result.text
    assert result.metadata.extension == "docx"


def test_file_reader_reads_pdf_with_extractable_text_smoke() -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    buffer = BytesIO()
    writer.write(buffer)

    try:
        FileReaderSkill().read_bytes(buffer.getvalue(), "blank.pdf")
    except ValueError as exc:
        assert "extractable text" in str(exc)

