# from typing import Any, Callable, Mapping, Sequence
from pydantic import BaseModel

class EnvironmentSettings(BaseModel):
    """
    Configuration model for jinja2.Environment.
    Mirrors the most common and useful Environment options.
    """

    block_start_string: str | None = None
    block_end_string: str | None = None
    variable_start_string: str | None = None
    variable_end_string: str | None = None
    comment_start_string: str | None = None
    comment_end_string: str | None = None

    line_statement_prefix: str | None = None
    line_comment_prefix: str | None = None

    trim_blocks: bool | None = None
    lstrip_blocks: bool | None = None
    newline_sequence: str | None = None
    keep_trailing_newline: bool | None = None

    optimized: bool | None = None
    enable_async: bool | None = None

    # -------------------------
    # Final model config
    # -------------------------
    model_config = {
        "frozen": True
    }


'''
    # -------------------------
    # Undefined handling
    # -------------------------
    undefined: type | None = None
    """
    Typically jinja2.Undefined, StrictUndefined, DebugUndefined, etc.
    Kept as `type` to avoid importing jinja in settings layer.
    """

    # -------------------------
    # Autoescaping
    # -------------------------
    autoescape: bool | Callable[[str | None], bool] = False

    # -------------------------
    # Extensions
    # -------------------------
    extensions: Sequence[str] = Field(default_factory=tuple)
    """
    List of extension import paths, e.g.:
    ('jinja2.ext.do', 'jinja2.ext.loopcontrols')
    """

    # -------------------------
    # Globals / filters / tests
    # -------------------------
    globals: Mapping[str, Any] = Field(default_factory=dict)
    filters: Mapping[str, Callable[..., Any]] = Field(default_factory=dict)
    tests: Mapping[str, Callable[..., bool]] = Field(default_factory=dict)
'''