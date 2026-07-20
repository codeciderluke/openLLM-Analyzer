"""Architecture analyzer.

Normalises heterogeneous ``model_info`` metadata into a common
:class:`CanonicalArchitecture`, without depending on specific model names.
Unknown architectures still get name, raw metadata, discovered numeric
structural values and capability-based modalities.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ollama_inspector.analyzers import metadata_utils as mu
from ollama_inspector.domain.architecture import (
    AudioArchitecture,
    CanonicalArchitecture,
    VisionArchitecture,
)
from ollama_inspector.domain.enums import EvidenceStatus
from ollama_inspector.domain.evidence import Evidence

_SOURCE = "model_info"


class ArchitectureAnalyzer:
    """Produces a :class:`CanonicalArchitecture` from ``/api/show`` data."""

    def analyze(
        self,
        model_info: Mapping[str, Any] | None,
        details: Mapping[str, Any] | None,
        capabilities: list[str] | None,
    ) -> CanonicalArchitecture:
        model_info = model_info or {}
        details = details or {}
        capabilities = capabilities or []

        arch_name, arch_evidence = self._resolve_architecture(model_info, details)
        result = CanonicalArchitecture(
            architecture=arch_name,
            raw_metadata=dict(model_info),
        )
        result.evidence.append(arch_evidence)

        prefix = arch_name if arch_name and arch_name != "unknown" else None
        self._populate_core(result, model_info, prefix)
        self._populate_vision(result, model_info, prefix)
        self._populate_audio(result, model_info, prefix)
        self._derive_values(result)
        result.modalities = self._detect_modalities(model_info, capabilities)
        return result

    # -- architecture name ---------------------------------------------

    def _resolve_architecture(
        self, model_info: Mapping[str, Any], details: Mapping[str, Any]
    ) -> tuple[str, Evidence]:
        arch = model_info.get("general.architecture")
        if isinstance(arch, str) and arch.strip():
            return arch.strip(), Evidence(
                field="architecture",
                status=EvidenceStatus.CONFIRMED,
                source=_SOURCE,
                description="Using general.architecture value",
                value=arch.strip(),
            )

        family = details.get("family")
        if isinstance(family, str) and family.strip():
            return family.strip(), Evidence(
                field="architecture",
                status=EvidenceStatus.DETECTED,
                source="details.family",
                description="Inferred architecture from details.family",
                value=family.strip(),
                confidence=0.6,
            )

        families = details.get("families")
        if isinstance(families, list) and families:
            first = families[0]
            if isinstance(first, str) and first.strip():
                return first.strip(), Evidence(
                    field="architecture",
                    status=EvidenceStatus.DETECTED,
                    source="details.families",
                    description="Inferred architecture from details.families[0]",
                    value=first.strip(),
                    confidence=0.5,
                )

        prefix = self._guess_prefix(model_info)
        if prefix is not None:
            return prefix, Evidence(
                field="architecture",
                status=EvidenceStatus.DETECTED,
                source="metadata.key_prefix",
                description="Inferred architecture from metadata key prefix",
                value=prefix,
                confidence=0.4,
            )

        return "unknown", Evidence(
            field="architecture",
            status=EvidenceStatus.UNKNOWN,
            source=_SOURCE,
            description="Architecture could not be determined.",
        )

    @staticmethod
    def _guess_prefix(model_info: Mapping[str, Any]) -> str | None:
        """Most common leading segment among structural (non-general/tokenizer) keys."""

        counts: dict[str, int] = {}
        for key in model_info:
            if not isinstance(key, str) or "." not in key:
                continue
            head = key.split(".", 1)[0]
            if head in {"general", "tokenizer"}:
                continue
            counts[head] = counts.get(head, 0) + 1
        if not counts:
            return None
        return max(counts, key=lambda k: counts[k])

    # -- core structural values ----------------------------------------

    def _populate_core(
        self, result: CanonicalArchitecture, mi: Mapping[str, Any], prefix: str | None
    ) -> None:
        result.context_length = self._pick_int(
            result, mi, prefix, ["context_length"], "context_length"
        )
        result.embedding_length = self._pick_int(
            result, mi, prefix, ["embedding_length"], "embedding_length"
        )
        result.block_count = self._pick_int(
            result, mi, prefix, ["block_count"], "block_count"
        )
        result.feed_forward_length = self._pick_int(
            result, mi, prefix, ["feed_forward_length"], "feed_forward_length"
        )
        result.attention_heads = self._pick_int(
            result, mi, prefix, ["attention.head_count"], "attention_heads"
        )
        result.kv_heads = self._pick_int(
            result, mi, prefix, ["attention.head_count_kv"], "kv_heads"
        )
        result.vocabulary_size = self._pick_vocab(result, mi, prefix)

    def _populate_vision(
        self, result: CanonicalArchitecture, mi: Mapping[str, Any], prefix: str | None
    ) -> None:
        block, _ = self._first_int_for(mi, prefix, ["vision.block_count"])
        emb, _ = self._first_int_for(mi, prefix, ["vision.embedding_length"])
        heads, _ = self._first_int_for(mi, prefix, ["vision.attention.head_count"])
        patch, _ = self._first_int_for(mi, prefix, ["vision.patch_size"])
        if any(v is not None for v in (block, emb, heads, patch)):
            result.vision = VisionArchitecture(
                block_count=block,
                embedding_length=emb,
                attention_heads=heads,
                patch_size=patch,
            )

    def _populate_audio(
        self, result: CanonicalArchitecture, mi: Mapping[str, Any], prefix: str | None
    ) -> None:
        block, _ = self._first_int_for(mi, prefix, ["audio.block_count"])
        emb, _ = self._first_int_for(mi, prefix, ["audio.embedding_length"])
        if any(v is not None for v in (block, emb)):
            result.audio = AudioArchitecture(block_count=block, embedding_length=emb)

    # -- derived values -------------------------------------------------

    def _derive_values(self, result: CanonicalArchitecture) -> None:
        emb = result.embedding_length
        heads = result.attention_heads
        if emb and heads and heads > 0 and emb % heads == 0:
            result.head_dimension = emb // heads
            result.evidence.append(
                Evidence(
                    field="head_dimension",
                    status=EvidenceStatus.DERIVED,
                    source="calculation",
                    description="embedding_length / attention_heads",
                    value=result.head_dimension,
                )
            )

        kv = result.kv_heads
        if heads and kv and kv > 0:
            ratio = heads / kv
            result.gqa_ratio = ratio
            result.evidence.append(
                Evidence(
                    field="gqa_ratio",
                    status=EvidenceStatus.DERIVED,
                    source="calculation",
                    description="attention_heads / kv_heads",
                    value=ratio,
                )
            )

    # -- modality detection --------------------------------------------

    def _detect_modalities(
        self, mi: Mapping[str, Any], capabilities: list[str]
    ) -> list[str]:
        modalities: list[str] = []

        has_completion = mu.has_capability(capabilities, mu.CAP_COMPLETION)
        has_template = any(
            isinstance(k, str) and k.endswith("tokenizer.chat_template") for k in mi
        )
        if has_completion or has_template:
            modalities.append("text")

        has_vision_meta = any(isinstance(k, str) and ".vision." in k for k in mi)
        if mu.has_capability(capabilities, mu.CAP_VISION) or has_vision_meta:
            modalities.append("vision")

        if mu.has_capability(capabilities, mu.CAP_EMBEDDING):
            modalities.append("embedding")

        has_audio_meta = any(isinstance(k, str) and ".audio." in k for k in mi)
        if mu.has_capability(capabilities, mu.CAP_AUDIO) or has_audio_meta:
            modalities.append("audio")

        return modalities

    # -- helpers --------------------------------------------------------

    def _pick_int(
        self,
        result: CanonicalArchitecture,
        mi: Mapping[str, Any],
        prefix: str | None,
        suffixes: list[str],
        field_name: str,
    ) -> int | None:
        value, key = self._first_int_for(mi, prefix, suffixes)
        if value is not None and key is not None:
            result.evidence.append(
                Evidence(
                    field=field_name,
                    status=EvidenceStatus.CONFIRMED,
                    source=_SOURCE,
                    description=f"Using {key} value",
                    value=value,
                )
            )
        return value

    def _pick_vocab(
        self, result: CanonicalArchitecture, mi: Mapping[str, Any], prefix: str | None
    ) -> int | None:
        value, key = self._first_int_for(mi, prefix, ["vocab_size", "vocabulary_size"])
        if value is None:
            tokens = mi.get("tokenizer.ggml.tokens")
            # tokens may be the full list (Ollama) or a pre-counted int (GGUF
            # reader collapses large arrays to their length).
            length = mu.sequence_length(tokens)
            if length is None and isinstance(tokens, int):
                length = tokens
            if length is not None:
                result.evidence.append(
                    Evidence(
                        field="vocabulary_size",
                        status=EvidenceStatus.DERIVED,
                        source=_SOURCE,
                        description="Using length of tokenizer.ggml.tokens",
                        value=length,
                    )
                )
                return length
            return None
        result.evidence.append(
            Evidence(
                field="vocabulary_size",
                status=EvidenceStatus.CONFIRMED,
                source=_SOURCE,
                description=f"Using {key} value",
                value=value,
            )
        )
        return value

    @staticmethod
    def _first_int_for(
        mi: Mapping[str, Any], prefix: str | None, suffixes: list[str]
    ) -> tuple[int | None, str | None]:
        candidates: list[str] = []
        for suffix in suffixes:
            if prefix:
                candidates.append(f"{prefix}.{suffix}")
            candidates.append(suffix)
        return mu.first_int(mi, candidates)
