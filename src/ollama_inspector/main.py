"""Console/GUI entry point."""

from __future__ import annotations

import sys

from ollama_inspector.app import run


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
