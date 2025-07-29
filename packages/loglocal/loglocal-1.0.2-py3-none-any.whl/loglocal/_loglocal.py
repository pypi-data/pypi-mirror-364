import sys
import time
import asyncio
from functools import wraps
from loguru._logger import Logger as LoguruLogger
from loglocal.models._config_models import LogLocalConfig

class LogLocal(LoguruLogger):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _config_logger(self, _config: LogLocalConfig):
        self.add(
            sys.stderr,
            level=_config.log_config.level,
            format=_config.log_format,
            colorize=True,
            backtrace=True,
            diagnose=_config.log_config.diagnose
        )
        self.add(
            _config.log_path,
            level=_config.log_config.level,
            format=_config.log_format,
            rotation=_config.log_config.file_rotation,
            retention=_config.log_config.file_retention,
            compression="zip",
            serialize=_config.log_config.serialize,
            enqueue=_config.log_config.enqueue,
            backtrace=True,
            diagnose=_config.log_config.diagnose
        )

    def wrap(self, func=None):
        """
        Decorator to wrap sync or async functions for logging:
        :param func:
        :return:
        """

        def decorator(fn):
            _log = self.patch(lambda r: r.update(function=fn.__name__, name=fn.__module__, line=fn.__code__.co_firstlineno))
            @wraps(fn)
            async def async_wrapper(*args, **kwargs):
                extra = {"args": repr(args)[:200], "kwargs": repr(kwargs)[:200]}
                _log.bind(**extra).info(f"→ started")
                start = time.monotonic()
                try:
                    result = await fn(*args, **kwargs)
                    elapsed = time.monotonic() - start
                    _log.bind(result={repr(result)[:200]}, duration=f"{elapsed:.3f}s").info(f"← finished")
                    return result
                except Exception as e:
                    _log.bind(exception=str(e)).exception(f"❌ ←→ error")
                    raise

            @wraps(fn)
            def sync_wrapper(*args, **kwargs):
                extra = {"args": repr(args)[:200], "kwargs": repr(kwargs)[:200]}
                _log.bind(**extra).info(f"→ started")
                start = time.monotonic()
                try:
                    result = fn(*args, **kwargs)
                    elapsed = time.monotonic() - start
                    _log.bind(result={repr(result)[:200]}, duration=f"{elapsed:.3f}s").info(f"← finished")
                    return result
                except Exception as e:
                    _log.bind(exception=str(e)).exception(f"❌ ←→ error")
                    raise

            return async_wrapper if asyncio.iscoroutinefunction(fn) else sync_wrapper

        return decorator(func) if func else decorator

    @classmethod
    def from_config(cls, config: LogLocalConfig = LogLocalConfig(), **kwargs) -> 'LogLocal':
        """
        Create a logger instance from a LogLocalConfig object.
        """
        _instance = cls(**config.log_opt.model_dump(), **kwargs)
        _instance.remove()
        _instance._config_logger(config)
        return _instance

    @classmethod
    def default(cls) -> 'LogLocal':
        return cls.from_config(LogLocalConfig())
