"""VOD analysis workflow orchestration.

Provides the high-level workflow class that ties together filtering,
grid operations, and Icechunk persistence.

Depends on ``canvod-store`` at runtime::

    uv add canvod-store
"""

from canvod.grids.workflows.adapted_workflow import (
    AdaptedVODWorkflow,
    check_processed_data_status,
    get_workflow_for_store,
)

__all__ = [
    "AdaptedVODWorkflow",
    "check_processed_data_status",
    "get_workflow_for_store",
]
