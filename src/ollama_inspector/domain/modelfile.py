"""Parsed representation of a Modelfile."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ParsedModelfile(BaseModel):
    """Structured view of the directives found in a Modelfile.

    The original text is preserved separately; this model only holds the
    parsed directives. Adapter/file strings are never opened.
    """

    from_model: str | None = None
    adapters: list[str] = Field(default_factory=list)
    system_blocks: list[str] = Field(default_factory=list)
    templates: list[str] = Field(default_factory=list)
    parameters: dict[str, list[str]] = Field(default_factory=dict)
    messages: list[dict[str, str]] = Field(default_factory=list)
    license_blocks: list[str] = Field(default_factory=list)
    unknown_directives: list[str] = Field(default_factory=list)
