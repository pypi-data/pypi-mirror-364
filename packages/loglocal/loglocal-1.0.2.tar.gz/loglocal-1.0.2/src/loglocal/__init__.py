from collections.abc import Callable

from loglocal._loglocal import LogLocal as _LogLocal
from loglocal.models import LogLocalConfig as _LogLocalConfig

logger = _LogLocal.default()
Logger: Callable[..., _LogLocal] = _LogLocal.from_config
__all__ = [
    "logger",
    "Logger"
]