"""Theme tokens, stylesheet and icon builder."""

from __future__ import annotations

from ollama_inspector.ui.theme import (
    DARK,
    LIGHT,
    ThemeName,
    build_stylesheet,
    palette_for,
    toggle,
)


def test_toggle_roundtrip() -> None:
    assert toggle(ThemeName.DARK) == ThemeName.LIGHT
    assert toggle(ThemeName.LIGHT) == ThemeName.DARK


def test_palette_for() -> None:
    assert palette_for(ThemeName.DARK) is DARK
    assert palette_for(ThemeName.LIGHT) is LIGHT


def test_stylesheet_substitutes_all_tokens() -> None:
    for palette in (DARK, LIGHT):
        qss = build_stylesheet(palette)
        # No leftover unsubstituted $tokens.
        assert "$" not in qss
        assert palette.accent in qss
        assert palette.bg in qss
