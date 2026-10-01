"""Output Hub"""

from ._hub import OutputHub

logger = OutputHub(
    name="default",
    log_level="ERROR",
    console_log_level="ERROR",
)

__all__ = ["OutputHub", "logger"]
