"""Central logging configuration.

Sensitive SYSTEM / Modelfile text is never written to the default log; only
structural facts (endpoints, key names, analyzer stages) are logged.
"""

from __future__ import annotations

import logging

_CONFIGURED = False


def configure_logging(level: int = logging.INFO) -> None:
    """Configure the root logger once, idempotently."""

    global _CONFIGURED
    if _CONFIGURED:
        return
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger under the application root."""

    return logging.getLogger(f"ollama_inspector.{name}")
