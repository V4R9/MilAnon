"""Compatibility shim — workflow module moved to milanon.config.workflow (CR-009).

The domain layer must have zero external dependencies. Since workflow.py
imports ``yaml`` (an external library), it belongs in the config layer.

All public symbols are re-exported so existing imports keep working.
"""

from milanon.config.workflow import DoctrineRef, WorkflowConfig, load_workflows  # noqa: F401

__all__ = ["DoctrineRef", "WorkflowConfig", "load_workflows"]
