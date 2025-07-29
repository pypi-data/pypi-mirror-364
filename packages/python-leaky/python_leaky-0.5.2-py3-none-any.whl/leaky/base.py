from typing import Generic, Iterable, Iterator, List, TypeVar

from pydantic.dataclasses import dataclass


class LeakyCount(int):
    """
    A count. This is used in preference to int so that it can be excluded from reports.
    """

    pass


@dataclass
class ApproximateSize:
    """
    Represents an approximate uncertain size. That is, a size where the lower bound is known
    approximately, and the upper bound may not be known at all.
    """

    approx_size: int = 0
    """
    If `upper_bound_known` is `True`, then this is the approximate size. If `upper_bound_known` is
    `False`, then this is the approximate lower bound of the size.
    """

    upper_bound_known: bool = True
    """
    Whether the upper bound of the size is known.
    """

    def __add__(self, other: "ApproximateSize") -> "ApproximateSize":
        return ApproximateSize(
            self.approx_size + other.approx_size, self.upper_bound_known and other.upper_bound_known
        )

    @property
    def prefix(self) -> str:
        if self.upper_bound_known:
            return "~"
        else:
            return ">="


T = TypeVar("T")


class CachingIterable(Generic[T]):
    """
    Iterable that caches the underlying iterable.

    Note: this class is *not* thread-safe!
    """

    def __init__(self, iterable: Iterable[T]):
        self._iterator = iter(iterable)
        self._cache: List[T] = []

    def __iter__(self) -> Iterator[T]:
        for item in self._cache:
            yield item
        try:
            while True:
                item = next(self._iterator)
                self._cache.append(item)
                yield item
        except StopIteration:
            pass
