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
