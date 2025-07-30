from typing import Callable, TypeVar

HOOKS = ["request", "response"]
T = TypeVar("T")


def default_hooks():
    return {event: [] for event in HOOKS}


def dispatch_hook(key: str, hooks: dict[str, Callable | list[Callable]],
                  hook_data: T, **kwargs) -> T:
    """
    this function was copied from requests library
    Dispatches a hook dictionary on a given piece of data.
    """
    hooks = hooks or {}
    hooks = hooks.get(key)
    if hooks:
        if hasattr(hooks, "__call__"):
            hooks = [hooks]
        for hook in hooks:
            _hook_data = hook(hook_data, **kwargs)
            if _hook_data is not None:
                hook_data = _hook_data
    return hook_data
