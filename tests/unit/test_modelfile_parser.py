"""Step 5: Modelfile parser."""

from __future__ import annotations

from ollama_inspector.analyzers.modelfile_parser import ModelfileParser

EXAMPLE = """FROM llama3.1:8b

ADAPTER ./support-adapter.gguf

PARAMETER temperature 0.2
PARAMETER stop "<|eot_id|>"

SYSTEM \"\"\"
You are a technical support assistant.
\"\"\"
"""


def test_parses_spec_example() -> None:
    parsed = ModelfileParser().parse(EXAMPLE)
    assert parsed.from_model == "llama3.1:8b"
    assert parsed.adapters == ["./support-adapter.gguf"]
    assert parsed.parameters["temperature"] == ["0.2"]
    assert parsed.parameters["stop"] == ['"<|eot_id|>"']
    assert parsed.system_blocks == ["You are a technical support assistant."]


def test_directives_case_insensitive() -> None:
    parsed = ModelfileParser().parse("from base:latest\nsystem hello")
    assert parsed.from_model == "base:latest"
    assert parsed.system_blocks == ["hello"]


def test_comments_and_blank_lines_ignored() -> None:
    parsed = ModelfileParser().parse("# a comment\n\nFROM base:latest\n# another")
    assert parsed.from_model == "base:latest"


def test_repeated_parameter_accumulates() -> None:
    parsed = ModelfileParser().parse(
        "PARAMETER stop a\nPARAMETER stop b\nPARAMETER stop c"
    )
    assert parsed.parameters["stop"] == ["a", "b", "c"]


def test_unknown_directive_captured() -> None:
    parsed = ModelfileParser().parse("WEIRD something\nFROM base:latest")
    assert any("WEIRD" in d for d in parsed.unknown_directives)
    assert parsed.from_model == "base:latest"


def test_single_line_triple_quote() -> None:
    parsed = ModelfileParser().parse('SYSTEM """inline block"""')
    assert parsed.system_blocks == ["inline block"]


def test_unterminated_block_partial_success() -> None:
    parsed = ModelfileParser().parse('SYSTEM """line one\nline two')
    assert parsed.system_blocks
    assert "line one" in parsed.system_blocks[0]


def test_message_directive() -> None:
    parsed = ModelfileParser().parse('MESSAGE user "hello there"')
    assert parsed.messages == [{"role": "user", "content": "hello there"}]


def test_empty_input() -> None:
    parsed = ModelfileParser().parse("")
    assert parsed.from_model is None
    assert parsed.adapters == []
