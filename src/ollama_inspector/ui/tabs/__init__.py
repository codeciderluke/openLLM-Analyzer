"""Detail tabs shown for a selected model."""

from ollama_inspector.ui.tabs.fine_tuning_tab import FineTuningTab
from ollama_inspector.ui.tabs.lineage_tab import LineageTab
from ollama_inspector.ui.tabs.overview_tab import OverviewTab
from ollama_inspector.ui.tabs.prompt_tab import PromptTab
from ollama_inspector.ui.tabs.rag_tab import RagTab
from ollama_inspector.ui.tabs.raw_tab import RawTab
from ollama_inspector.ui.tabs.structure_tab import StructureTab

__all__ = [
    "FineTuningTab",
    "LineageTab",
    "OverviewTab",
    "PromptTab",
    "RagTab",
    "RawTab",
    "StructureTab",
]
