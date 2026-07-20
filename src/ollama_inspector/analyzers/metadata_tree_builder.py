"""Convert flat dotted metadata keys into a sorted tree.

Example::

    qwen2.block_count
    qwen2.attention.head_count
    qwen2.attention.head_count_kv

becomes::

    qwen2
    ├── block_count
    └── attention
        ├── head_count
        └── head_count_kv

The builder is Qt-free and stateless (safe to call from worker threads); the
UI decides how to render/abbreviate values.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TreeNode:
    """A node in the metadata tree.

    ``value`` is meaningful only when ``has_value`` is ``True`` (which
    distinguishes a genuine ``None`` value from "no direct value present").
    """

    key: str
    value: Any = None
    has_value: bool = False
    children: list[TreeNode] = field(default_factory=list)

    @property
    def is_leaf(self) -> bool:
        return not self.children


@dataclass
class _Builder:
    """Mutable intermediate node with dict-indexed children for fast lookup."""

    key: str
    value: Any = None
    has_value: bool = False
    children: dict[str, _Builder] = field(default_factory=dict)

    def child(self, segment: str) -> _Builder:
        node = self.children.get(segment)
        if node is None:
            node = _Builder(key=segment)
            self.children[segment] = node
        return node

    def finalize(self) -> TreeNode:
        ordered = [self.children[k] for k in sorted(self.children)]
        return TreeNode(
            key=self.key,
            value=self.value,
            has_value=self.has_value,
            children=[child.finalize() for child in ordered],
        )


def build_metadata_tree(metadata: Mapping[str, Any]) -> list[TreeNode]:
    """Build a sorted list of root :class:`TreeNode` from flat metadata."""

    root = _Builder(key="")
    for key in sorted(metadata.keys()):
        node = root
        for segment in key.split("."):
            node = node.child(segment)
        node.value = metadata[key]
        node.has_value = True
    return [root.children[k].finalize() for k in sorted(root.children)]
