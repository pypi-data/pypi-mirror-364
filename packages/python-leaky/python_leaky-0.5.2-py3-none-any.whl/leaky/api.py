"""
The public api of Leaky. Functions in this module are imported into the main
`__init__.py` file, along with the interfaces defined in `interface.py`.
"""

import functools
from typing import Any, Callable, Dict

from leaky.interface import LeakMonitor
from leaky.monitors import LeakMonitorImpl, LeakMonitorThread
from leaky.options import Options
from leaky.output import get_output_writer
from leaky.reports import get_report_writer


def start(
    max_object_lifetime: float, warmup_time: float | None = None, **kwargs: Dict[str, Any]
) -> None:
    """
    Starts monitoring for memory leaks. A summary of potential leaks will be printed to the
    console every `max_object_lifetime` seconds, after `warmup_time` seconds.

    The `warmup_time` parameter can be changed to control how long Leaky will wait before
    starting to look for leaks. For example, if the program being monitored creates a lot
    of data on startup, this can be used to ignore that data. This defaults to
    `max_object_lifetime`.

    :param max_object_lifetime: The maximum time in seconds that an object can live before
    it is considered a potential leak.
    :param warmup_time: The number of seconds to wait before starting to look for leaks.
        This defaults to `max_object_lifetime`.
    :param kwargs: Additional options. See the `leaky.Options` class for more details.
    """
    if warmup_time is None:
        warmup_time = max_object_lifetime
    options = _create_options(kwargs)
    leak_monitor_thread = LeakMonitorThread(
        max_object_lifetime=max_object_lifetime,
        warmup_time=warmup_time,
        writer=get_output_writer(options=options),
        report_writer=get_report_writer(options=options),
        options=options,
    )
    leak_monitor_thread.start()


def leak_monitor(
    warmup_calls: int = 1, object_ttl_calls: int = 1, **kwargs: Dict[str, Any]
) -> Callable[[Any], Any]:
    """
    Decorator to monitor for memory leaks.

    After the decorated function has been called `warmup_calls` times, a memory leak report
    is generated every `object_ttl_calls` calls to the decorated function.

    By default, `warmup_calls` and `object_ttl_calls` are both set to `1`, so after the first
    call, leaks will be identified on every call.

    The `warmup_calls` parameter can be changed if data is created on some number of initial calls
    to the decorated function, but not created after that.

    The `object_ttl_calls` parameter can be changed if data created by the decorated function
    is permitted to live for a certain number of calls. Only objects that have lived for
    `object_ttl_calls` calls will be reported as potential leaks. For example, if
    `object_ttl_calls` is set to `2`, objects must live for two calls to be considered as
    potential leaks.

    The behavior of the decorator can be controlled by passing keyword arguments to the
    decorator. See the `leaky.Options` class for more details.
    """

    def decorator_func(func: Any) -> Callable[[Any], Any]:
        monitor = _create_leak_monitor(
            warmup_calls=warmup_calls, min_object_age_calls=object_ttl_calls, **kwargs
        )

        @functools.wraps(func)
        def wrapper(*inner_args: Any, **inner_kwargs: Any) -> Any:
            with monitor:
                return func(*inner_args, **inner_kwargs)

        return wrapper

    return decorator_func


def _create_leak_monitor(
    warmup_calls: int = 1,
    min_object_age_calls: int = 1,
    **kwargs: Dict[str, Any],
) -> LeakMonitor:
    """
    Creates a monitor for memory leaks.
    """
    options = _create_options(kwargs)
    return LeakMonitorImpl(
        writer=get_output_writer(options=options),
        report_writer=get_report_writer(options=options),
        warmup_calls=warmup_calls,
        calls_per_report=min_object_age_calls,
        options=options,
    )


def _create_options(kwargs: Dict[str, Any]) -> Options:
    return Options(**kwargs)
