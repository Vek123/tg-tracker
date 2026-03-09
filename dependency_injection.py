from copy import copy
from functools import wraps
import inspect
from typing import Any, Callable, ParamSpec, TypeVar

Param = ParamSpec("Param")
RetType = TypeVar("RetType")


def injected(func: Callable[Param, RetType]) -> Callable[Param, RetType]:
    @wraps(func)
    def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
        sig = inspect.signature(func)
        for kw, param in sig.parameters.items():
            val = param.default
            if isinstance(val, Injection):
                kwargs[kw] = val()

        return func(*args, **kwargs)

    return wrapper


class Injection:
    def __init__(self, inj: Any, *args: Any, **kwargs: Any):
        self.inj = inj
        self.args = args
        self.kwargs = kwargs

    def __call__(self) -> Any:
        args = list(copy(self.args))
        kwargs = copy(self.kwargs)
        for idx, val in enumerate(args):
            if isinstance(val, Injection):
                args[idx] = val()

        for key, val in kwargs.items():
            if isinstance(val, Injection):
                kwargs[key] = val()

        return self.inj(*args, **kwargs)
