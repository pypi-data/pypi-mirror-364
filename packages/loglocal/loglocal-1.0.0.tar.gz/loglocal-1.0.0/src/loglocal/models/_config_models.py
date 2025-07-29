import os
from typing import Any
from loguru._logger import Core
from pydantic import BaseModel, Field, ConfigDict

class LogConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    level: str = Field(default="DEBUG")
    file_rotation: str = Field(default="30 days")
    file_retention: str = Field(default="90 days")
    serialize: bool = Field(default=True)
    enqueue: bool = Field(default=True)
    diagnose: bool = Field(default=False)  # avoid leaking vars in production

class LogLocalOptions(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    core: Core = Field(default_factory=Core)
    exception: Any = None
    depth: int = 0
    record: bool = False
    lazy: bool = False
    colors: bool = True
    raw: bool = False
    capture: bool = True
    patchers: list[Any] = []
    extra: dict[str, Any] = {}

class LogLocalConfig(BaseModel):
    log_path: str = os.environ.get("LOGLOCAL_PATH", os.path.join("logs", "app.log"))
    log_format: str = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | {message} | {extra}"
    log_level: str = "DEBUG"
    log_opt: LogLocalOptions = LogLocalOptions()
    log_config: LogConfig = LogConfig()
