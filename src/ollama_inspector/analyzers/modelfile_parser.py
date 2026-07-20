"""Modelfile parser.

Line-oriented parser supporting the directives Ollama emits. Directives are
case-insensitive, comments and blank lines are ignored, and triple-quoted
blocks may span multiple lines. Parsing is best-effort: on malformed input the
parser returns whatever it managed to extract. Adapter/file strings are never
opened.
"""

from __future__ import annotations

from ollama_inspector.domain.modelfile import ParsedModelfile

_TRIPLE_QUOTE = '"""'
_KNOWN_DIRECTIVES = {
    "FROM",
    "ADAPTER",
    "SYSTEM",
    "TEMPLATE",
    "PARAMETER",
    "MESSAGE",
    "LICENSE",
}


class ModelfileParser:
    """Parses raw Modelfile text into a :class:`ParsedModelfile`."""

    def parse(self, text: str) -> ParsedModelfile:
        result = ParsedModelfile()
        if not text:
            return result

        lines = text.splitlines()
        index = 0
        total = len(lines)
        while index < total:
            raw_line = lines[index]
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                index += 1
                continue

            directive, remainder = self._split_directive(stripped)
            upper = directive.upper()
            if upper not in _KNOWN_DIRECTIVES:
                result.unknown_directives.append(stripped)
                index += 1
                continue

            # A value may open a triple-quoted block that spans lines.
            if _TRIPLE_QUOTE in remainder:
                value, index = self._collect_block(remainder, lines, index)
            else:
                value = remainder
            self._apply(result, upper, value)
            index += 1

        return result

    # -- directive handling --------------------------------------------

    @staticmethod
    def _split_directive(line: str) -> tuple[str, str]:
        parts = line.split(None, 1)
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], parts[1]

    def _apply(self, result: ParsedModelfile, directive: str, value: str) -> None:
        if directive == "FROM":
            if result.from_model is None and value.strip():
                result.from_model = value.strip()
        elif directive == "ADAPTER":
            if value.strip():
                result.adapters.append(value.strip())
        elif directive == "SYSTEM":
            result.system_blocks.append(value.strip())
        elif directive == "TEMPLATE":
            result.templates.append(value.strip())
        elif directive == "LICENSE":
            result.license_blocks.append(value.strip())
        elif directive == "PARAMETER":
            self._apply_parameter(result, value)
        elif directive == "MESSAGE":
            self._apply_message(result, value)

    @staticmethod
    def _apply_parameter(result: ParsedModelfile, value: str) -> None:
        parts = value.split(None, 1)
        if not parts or not parts[0]:
            return
        key = parts[0]
        param_value = parts[1].strip() if len(parts) > 1 else ""
        result.parameters.setdefault(key, []).append(param_value)

    @staticmethod
    def _apply_message(result: ParsedModelfile, value: str) -> None:
        parts = value.split(None, 1)
        if not parts or not parts[0]:
            return
        role = parts[0]
        content = parts[1].strip() if len(parts) > 1 else ""
        content = _strip_wrapping_quotes(content)
        result.messages.append({"role": role, "content": content})

    # -- triple-quote block collection ---------------------------------

    @staticmethod
    def _collect_block(remainder: str, lines: list[str], index: int) -> tuple[str, int]:
        """Collect a possibly multi-line triple-quoted value.

        Returns the block content and the index of the last consumed line.
        Unterminated blocks return what was gathered (partial success).
        """

        open_pos = remainder.find(_TRIPLE_QUOTE)
        after_open = remainder[open_pos + len(_TRIPLE_QUOTE) :]

        close_pos = after_open.find(_TRIPLE_QUOTE)
        if close_pos != -1:
            return after_open[:close_pos], index

        collected = [after_open]
        cursor = index + 1
        total = len(lines)
        while cursor < total:
            line = lines[cursor]
            close_pos = line.find(_TRIPLE_QUOTE)
            if close_pos != -1:
                collected.append(line[:close_pos])
                return "\n".join(collected), cursor
            collected.append(line)
            cursor += 1
        # Unterminated block: consume the rest of the file.
        return "\n".join(collected), total - 1


def _strip_wrapping_quotes(text: str) -> str:
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
        return text[1:-1]
    return text
