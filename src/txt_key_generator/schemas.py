from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class InputKind(StrEnum):
    COMMAND = "command"
    TEXT_REQUEST = "text_request"
    FILE_REQUEST = "file_request"
    CLARIFICATION = "clarification"
    UNSUPPORTED_FILE = "unsupported_file"
    EMPTY = "empty"


class FileMetadata(BaseModel):
    filename: str
    extension: str
    mime_type: str | None = None
    size_bytes: int | None = None


class FileReadResult(BaseModel):
    text: str
    metadata: FileMetadata


class RouteResult(BaseModel):
    kind: InputKind
    reason: str
    extension: str | None = None


class CustomParameter(BaseModel):
    name: str
    value: str
    description: str | None = None

    @field_validator("name", "value", "description")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if isinstance(value, str) else value


class GenerationKeys(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    topic: str | None = None
    language: str | None = None
    target_word_count: int | None = Field(default=None, ge=1)
    red_policy: str | None = None
    tone: str | None = None
    audience: str | None = None
    structure: str | None = None
    must_include: list[str] = Field(default_factory=list)
    must_avoid: list[str] = Field(default_factory=list)
    additional_requirements: list[str] = Field(default_factory=list)
    custom_parameters: list[CustomParameter] = Field(default_factory=list)

    @field_validator("keywords", "must_include", "must_avoid", "additional_requirements")
    @classmethod
    def strip_list_values(cls, values: list[str]) -> list[str]:
        return [value.strip() for value in values if value and value.strip()]


class KeyValidationResult(BaseModel):
    is_complete: bool
    missing_fields: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    clarifying_questions: list[str] = Field(default_factory=list)


class GeneratedDraft(BaseModel):
    text: str
    notes: list[str] = Field(default_factory=list)


class CheckViolation(BaseModel):
    criterion: str
    description: str
    severity: str = "medium"


class CheckReport(BaseModel):
    passed: bool
    score: float = Field(ge=0, le=1)
    violations: list[CheckViolation] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    revision_instructions: list[str] = Field(default_factory=list)
    clarifying_questions: list[str] = Field(default_factory=list)


class RevisionResult(BaseModel):
    text: str
    changes_made: list[str] = Field(default_factory=list)


class GenerationResult(BaseModel):
    final_text: str | None
    report: CheckReport
    cycles_used: int
    drafts: list[str] = Field(default_factory=list)
    needs_clarification: bool = False
