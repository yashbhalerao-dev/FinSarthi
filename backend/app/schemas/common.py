from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody


class DataResponse(BaseModel, Generic[T]):
    data: T


class SourceEvidenceItem(BaseModel):
    field: str
    value: Any
    source: str | None = None
