from abc import ABC, abstractmethod
from typing import Callable, NewType, Protocol, Sequence, runtime_checkable
from dataclasses import dataclass, InitVar, field

__all__ = ['BitOrdering', 'lsb', 'msb', 'swiz']

BitOrdering = Callable[[int],int]
"""Function that takes an integer and returns a bitmask with a 1 bit in that bit position."""

@dataclass(frozen=True)
class _lsb(BitOrdering):
    def __call__(self, n: int) -> int:
        return 1 << n
    def __repr__(self):
        return "lsb"
@dataclass(frozen=True)
class _msb(BitOrdering):
    def __call__(self, n: int) -> int:
        return 0x80 >> n
    def __repr__(self):
        return "msb"

lsb = _lsb()
msb = _msb()

@dataclass(frozen=True)
class swiz(BitOrdering):
    order: int | str | Sequence[int] = (0,1,2,3,4,5,6,7)
    base: BitOrdering = lsb

    def __post_init__(self):
        order = self.order
        order_changed = False

        if isinstance(order, int):
            order_changed = True
            order = f"{order:08d}"[:8]

        if isinstance(order, str):
            order_changed = True
            # ValueError raised by int() for non 0-9 has better message than I could write:
            order = [int(c) for c in order]
        
        if len(order) != 8:
            raise ValueError(f"swizzle length {len(order)} must be 8: {order}")
        
        for i, v in enumerate(order):
            if not 0 <= v < 8:
                raise ValueError(f"swizzle index {v} at position {i} outside the range 0 through 7: {order}")
            
        if not isinstance(order, tuple):
            order_changed = True
            order = tuple(order)

        if order_changed:
            object.__setattr__(self, 'order', order)

    def __call__(self, n:int) -> int:
        return self.base(self.order[n])
    
    def __repr__(self) -> str:
        order = ''.join(f"{d:01d}" for d in self.order)
        if order[0] == '0':
            order = repr(order)
        if self.base != self.__class__.base:
            return f"{self.__class__.__name__}({order}, base={self.base!r})"
        else:
            return f"{self.__class__.__name__}({order})"
