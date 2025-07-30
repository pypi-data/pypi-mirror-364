from collections import deque
from collections.abc import Callable
import threading
from typing import Any
import logging

# Module-level logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class BFSMRO:
    """
    Context manager that enhances method lookup for a class or instance.
    Supports @classmethod, @staticmethod, and instance methods from subclasses.
    
    Lookup order:
        1. Normal MRO (default Python behavior)
        2. BFS search in subclasses (downward only)
    
    BFS search uses cls.__subclasses__(), which in CPython returns subclasses 
    in definition order. Method resolution among peers is not guaranteed in all Python implementations.
    """
    
    _lock = threading.RLock()

    def __init__(self, target: Any, thread_safe: bool = False, debug: bool = False):
        self.target = target
        self.thread_safe = thread_safe
        self.debug = debug
        self.proxy = None

    def __enter__(self):
        target = self.target
        is_class = isinstance(target, type)
        base_cls = target if is_class else target.__class__

        class UniversalProxy:
            def __getattr__(_, name: str):
                def unsafe_getattr():
                    # 1. Try normal lookup first (MRO)
                    try:
                        return getattr(target, name)
                    except AttributeError:
                        pass

                    if self.debug:
                        logger.debug(f"[BFSMRO] {base_cls.__name__}.{name} not in MRO, searching subclasses...")

                    # 2. BFS search in subclasses (downward)
                    queue = deque([base_cls])
                    visited = set()

                    while queue:
                        current = queue.popleft()
                        if current in visited:
                            continue
                        visited.add(current)

                        if name in current.__dict__:
                            raw_attr = current.__dict__[name]

                            # Case 1: @classmethod
                            if isinstance(raw_attr, classmethod):
                                bound = raw_attr.__func__.__get__(base_cls, base_cls)
                                if self.debug:
                                    bound = _wrap_for_debug(bound, name, current, base_cls)
                                return bound

                            # Case 2: @staticmethod
                            elif isinstance(raw_attr, staticmethod):
                                func = raw_attr.__func__
                                if self.debug:
                                    func = _wrap_for_debug(func, name, current, base_cls)
                                return func

                            # Case 3: instance method (only for instance proxies)
                            elif isinstance(raw_attr, Callable) and not is_class:
                                def bound(*args, **kwargs):
                                    return raw_attr(target, *args, **kwargs)
                                if self.debug:
                                    bound = _wrap_for_debug(bound, name, current, base_cls)
                                return bound

                        # Add subclasses
                        for sub in current.__subclasses__():
                            if sub not in visited:
                                queue.append(sub)

                    raise AttributeError(f"Method '{name}' not found in inheritance graph")

                # Use lock if thread_safe is enabled
                if self.thread_safe:
                    with BFSMRO._lock:
                        return unsafe_getattr()
                else:
                    return unsafe_getattr()

            def __repr__(self) -> str:
                return f"<BFSMRO for {target}>"

        def _wrap_for_debug(func, name: str, source_cls: type, target_cls: type):
            """Wrap callable to enhance error messages in debug mode."""
            def wrapped(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except TypeError as e:
                    raise TypeError(
                        f"Error calling {name} (from {source_cls.__name__}) "
                        f"on {target_cls.__name__}: {e}"
                    ) from e
            wrapped.__name__ = func.__name__
            wrapped.__qualname__ = func.__qualname__
            wrapped.__doc__ = func.__doc__
            wrapped.__module__ = func.__module__
            return wrapped

        self.proxy = UniversalProxy()
        return self.proxy

    def __exit__(self, exc_type, exc_value, exc_tb) -> bool:
        self.proxy = None
        return False
