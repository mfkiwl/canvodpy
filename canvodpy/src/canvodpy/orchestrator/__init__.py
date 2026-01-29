"""Processing orchestration and pipeline management.

This module contains the high-level orchestration logic for GNSS processing pipelines.
It coordinates RINEX data processing, auxiliary data handling, and dataset management
across multiple sites and receivers.

Key Components:
    - PipelineOrchestrator: Orchestrates multi-receiver, multi-date processing
    - RinexDataProcessor: Core RINEX data processing with parallel execution

This is the application layer that ties together building blocks from canvod-* packages.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from canvodpy.orchestrator.pipeline import (
        PipelineOrchestrator,
        SingleReceiverProcessor,
    )
    from canvodpy.orchestrator.processor import RinexDataProcessor

__all__ = [
    "PipelineOrchestrator",
    "RinexDataProcessor",
    "SingleReceiverProcessor",
]


def __getattr__(name: str):
    """Lazy import to avoid circular dependencies."""
    if name == "PipelineOrchestrator":
        from canvodpy.orchestrator.pipeline import PipelineOrchestrator
        return PipelineOrchestrator
    if name == "SingleReceiverProcessor":
        from canvodpy.orchestrator.pipeline import SingleReceiverProcessor
        return SingleReceiverProcessor
    if name == "RinexDataProcessor":
        from canvodpy.orchestrator.processor import RinexDataProcessor
        return RinexDataProcessor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
