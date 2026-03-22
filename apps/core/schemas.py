from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Observer:
    name: str
    filters: list[Callable[..., Any]]
    flags: dict[str, Any] | None = None
    kwargs: dict[str, Any] = field(default_factory=dict)
