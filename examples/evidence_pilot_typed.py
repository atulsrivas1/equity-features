"""Trusted local use of the optional external pilot; not a service endpoint."""
from pathlib import Path
from typing import Any

from evidence_pilot import record, replay


def produce_new_owned_export(path: Path) -> None:
    record(path)


def inspect_owned_export(path: Path) -> list[dict[str, Any]]:
    return replay(path, 'wheel-compute')
