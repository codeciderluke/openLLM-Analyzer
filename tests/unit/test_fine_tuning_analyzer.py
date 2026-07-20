"""Step 8: fine-tuning analyzer."""

from __future__ import annotations

from ollama_inspector.analyzers.fine_tuning_analyzer import FineTuningAnalyzer
from ollama_inspector.analyzers.modelfile_parser import ModelfileParser
from ollama_inspector.domain.enums import FineTuningMethod


def _analyze(modelfile: str):
    parsed = ModelfileParser().parse(modelfile)
    return FineTuningAnalyzer().analyze(parsed)


def test_lora_confirmed() -> None:
    ft = _analyze("FROM base:latest\nADAPTER ./a.gguf")
    assert ft.is_fine_tuned is True
    assert ft.method is FineTuningMethod.LORA
    assert ft.adapters == ["./a.gguf"]


def test_prompt_customization() -> None:
    ft = _analyze("FROM base:latest\nSYSTEM hi")
    assert ft.method is FineTuningMethod.PROMPT_CUSTOMIZATION
    assert ft.is_fine_tuned is False


def test_unknown_when_no_evidence() -> None:
    ft = _analyze("FROM base:latest")
    assert ft.method is FineTuningMethod.UNKNOWN
    assert ft.is_fine_tuned is None
    assert ft.warnings


def test_training_details_never_guessed() -> None:
    ft = _analyze("FROM base:latest\nADAPTER ./a.gguf")
    assert ft.training_dataset is None
    assert ft.training_parameters_available is False
