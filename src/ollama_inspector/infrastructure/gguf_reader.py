"""Minimal, read-only GGUF metadata reader (pure Python, no torch).

Reads only the GGUF header + metadata key/value block — never tensor data or
weights — so an externally stored ``.gguf`` model can be inspected with the
same analyzers used for Ollama models. Supports GGUF versions 2 and 3.

Reference: the GGUF metadata KV section mirrors Ollama's ``model_info``
(``general.architecture``, ``<arch>.context_length``, ...), so the parsed dict
drops straight into :class:`ArchitectureAnalyzer`.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO

from ollama_inspector.domain.errors import LocalModelError
from ollama_inspector.utils.logging_config import get_logger

logger = get_logger("gguf")

GGUF_MAGIC = b"GGUF"

# GGUF metadata value type enum.
_UINT8, _INT8 = 0, 1
_UINT16, _INT16 = 2, 3
_UINT32, _INT32 = 4, 5
_FLOAT32 = 6
_BOOL = 7
_STRING = 8
_ARRAY = 9
_UINT64, _INT64 = 10, 11
_FLOAT64 = 12

# (struct format, byte size) for fixed-width scalar types.
_SCALAR: dict[int, tuple[str, int]] = {
    _UINT8: ("<B", 1),
    _INT8: ("<b", 1),
    _UINT16: ("<H", 2),
    _INT16: ("<h", 2),
    _UINT32: ("<I", 4),
    _INT32: ("<i", 4),
    _FLOAT32: ("<f", 4),
    _BOOL: ("<?", 1),
    _UINT64: ("<Q", 8),
    _INT64: ("<q", 8),
    _FLOAT64: ("<d", 8),
}

# Arrays longer than this are collapsed to their element count to keep the
# metadata dict (and any exported report) small. Vocab length is preserved.
_ARRAY_STORE_CAP = 128

# Common general.file_type quantization enum values.
_FILE_TYPES = {
    0: "F32",
    1: "F16",
    2: "Q4_0",
    3: "Q4_1",
    7: "Q8_0",
    8: "Q5_0",
    9: "Q5_1",
    10: "Q2_K",
    11: "Q3_K_S",
    12: "Q4_K_S",
    13: "Q4_K_M",
    14: "Q5_K_S",
    15: "Q5_K_M",
    16: "Q6_K",
    17: "Q8_K",
}


@dataclass
class GgufMetadata:
    """Parsed GGUF header + metadata."""

    version: int
    tensor_count: int
    metadata: dict[str, object] = field(default_factory=dict)

    @property
    def architecture(self) -> str | None:
        value = self.metadata.get("general.architecture")
        return value if isinstance(value, str) else None

    @property
    def name(self) -> str | None:
        value = self.metadata.get("general.name")
        return value if isinstance(value, str) else None

    @property
    def quantization(self) -> str | None:
        value = self.metadata.get("general.file_type")
        if isinstance(value, int):
            return _FILE_TYPES.get(value, f"file_type={value}")
        return None


def read_gguf_metadata(path: Path) -> GgufMetadata:
    """Read GGUF metadata from ``path``. Raises :class:`LocalModelError`."""

    try:
        with path.open("rb") as stream:
            return _read(stream, path)
    except LocalModelError:
        raise
    except OSError as exc:
        raise LocalModelError(f"Could not open the file: {path}") from exc
    except (struct.error, EOFError) as exc:
        raise LocalModelError(f"Could not parse the GGUF structure: {path}") from exc


def _read(stream: BinaryIO, path: Path) -> GgufMetadata:
    magic = stream.read(4)
    if magic != GGUF_MAGIC:
        raise LocalModelError("Not a GGUF file (magic mismatch).")

    version = _scalar(stream, _UINT32)
    if version < 2:
        raise LocalModelError(f"Unsupported GGUF version: {version} (2 or newer required).")

    tensor_count = _scalar(stream, _UINT64)
    kv_count = _scalar(stream, _UINT64)
    logger.debug("GGUF v%d tensors=%d kv=%d", version, tensor_count, kv_count)

    metadata: dict[str, object] = {}
    for _ in range(kv_count):
        key = _read_string(stream)
        value_type = _scalar(stream, _UINT32)
        metadata[key] = _read_value(stream, value_type)

    return GgufMetadata(version=version, tensor_count=tensor_count, metadata=metadata)


# -- primitive readers --------------------------------------------------


def _read_exact(stream: BinaryIO, count: int) -> bytes:
    data = stream.read(count)
    if len(data) != count:
        raise EOFError("File is shorter than expected.")
    return data


def _scalar(stream: BinaryIO, value_type: int) -> object:
    fmt, size = _SCALAR[value_type]
    return struct.unpack(fmt, _read_exact(stream, size))[0]


def _read_string(stream: BinaryIO) -> str:
    length = _scalar(stream, _UINT64)
    if length < 0 or length > (1 << 31):
        raise LocalModelError("Abnormal string length.")
    raw = _read_exact(stream, int(length))
    return raw.decode("utf-8", errors="replace")


def _read_value(stream: BinaryIO, value_type: int) -> object:
    if value_type in _SCALAR:
        return _scalar(stream, value_type)
    if value_type == _STRING:
        return _read_string(stream)
    if value_type == _ARRAY:
        return _read_array(stream)
    raise LocalModelError(f"Unknown GGUF value type: {value_type}")


def _read_array(stream: BinaryIO) -> object:
    elem_type = _scalar(stream, _UINT32)
    count = _scalar(stream, _UINT64)
    store = count <= _ARRAY_STORE_CAP
    collected: list[object] = []
    for _ in range(int(count)):
        value = _read_value(stream, elem_type)
        if store:
            collected.append(value)
    # Large arrays (e.g. tokenizer tokens) are represented by their length so
    # the metadata stays compact; callers use the count as vocabulary size.
    return collected if store else int(count)
