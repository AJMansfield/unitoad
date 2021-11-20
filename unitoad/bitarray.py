from functools import partialmethod, singledispatchmethod
import itertools
from typing import Any, Callable, Generator, Iterable, Sequence, SupportsBytes, SupportsIndex

import operator
import copy

from unitoad.endian import BitOrdering, msb

__all__ = ['BitArray']

def ceildiv(a, b):
    return -(a // -b)

class _BitArray(Sequence[bool]): ...

class BitArray(_BitArray):
    def __init__(self, data, order:BitOrdering = msb, _len:int = None):
        self.data = bytearray(data)
        if _len is None:
            _len = 8*len(self.data)
        self._len = _len
        self.order = order
    
    def __len__(self):
        return self._len
    
    def _set_slack_bits(self, value: bool):
        """Set the 'slack bits' in the array to a particular value.
        This does not change the formal value of the array, but allows some byte-wise computations to not need to special-case the last element."""
        idx, num_slack = divmod(len(self), 8)
        if num_slack == 0:
            return
        for bit in range(8)[-num_slack:]:
            mask = self.order(bit)
            if value:
                self.data[idx] |= mask
            else:
                self.data[idx] &= ~mask
    
    def _num_slack(self) -> int:
        return len(self) % 8
    
    @singledispatchmethod
    def __getitem__(self, index: SupportsIndex) -> bool:
        index = operator.index(index)
        if abs(index) > len(self):
            raise IndexError(f"index {index} outside bit array of length {len(self)}")
        idx, bit = divmod(index, 8)
        mask = self.order(bit)
        return bool(self.data[idx] & mask)

    @__getitem__.register
    def _(self, index: slice) -> _BitArray:
        indices = range(len(self))[index]
        space = ceildiv(len(indices),8)
        result = BitArray(bytearray(b'\0'*space), order=self.order, _len=len(indices))
        for i, j in enumerate(indices):
            result[i] = self[j]
        return result

    @singledispatchmethod
    def __setitem__(self, index: SupportsIndex, value: bool) -> None:
        index = operator.index(index)
        if abs(index) > len(self):
            raise IndexError(f"index {index} outside bit array of length {len(self)}")
        idx, bit = divmod(index, 8)
        mask = self.order(bit)
        if value:
            self.data[idx] |= mask
        else:
            self.data[idx] &= ~mask

    @__setitem__.register
    def _(self, index: slice, values: Sequence[bool]) -> None:
        indices = range(len(self))[index]
        for i, v in zip(indices, values):
            self[i] = v
    
    def __iter__(self) -> Generator[bool, None, None]:
        for i in range(len(self)):
            yield self[i]
    
    def __contains__(self, item:bool) -> bool:
        if item: # doing it a byte at a time instead of a bit at a time
            data = itertools.accumulate(self.data, operator.or_)
            return data != 0x00
        else:
            data = itertools.accumulate(self.data, operator.and_)
            return data != 0xff
    
    def __bytes__(self) -> bytes:
        return bytes(self.data)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({bytes(self)!r})"
    
    def __lshift__(self, shift: int) -> _BitArray:
        return self[shift:]
    
    def __rshift__(self, shift: int) -> _BitArray:
        byte, bits = divmod(shift, 8)
        if bits == 0:
            return BitArray(bytearray(b'0' * byte) + self.data, order=self.order, _len=len(self)+shift)
        else:
            return self >> 8*(byte+1) << 8 - bits

    @singledispatchmethod
    def _iop(self, other: Iterable[SupportsIndex] | SupportsBytes, op: Callable[[Any,Any],Any], slack: bool) -> _BitArray:
        for i, v in enumerate(bytes(other)):
            self.data[i] = op(self.data[i], v)
        return self
    @_iop.register
    def _(self, other: _BitArray, op: Callable[[Any,Any],Any], slack: bool) -> _BitArray:
        other._set_slack_bits(slack)
        for i, v in enumerate(other.data):
            self.data[i] = op(self.data[i], v)
        return self

    def _op(self, other: _BitArray, op: Callable[[Any,Any],Any], slack: bool) -> _BitArray:
        return copy.copy(self)._iop(other, op, slack)

    __iand__ = partialmethod(_iop, op=operator.and_, slack=True)
    __ixor__ = partialmethod(_iop, op=operator.xor, slack=False)
    __ior__ = partialmethod(_iop, op=operator.or_, slack=False)
    __and__ = partialmethod(_op, op=operator.and_, slack=True)
    __xor__ = partialmethod(_op, op=operator.xor, slack=False)
    __or__ = partialmethod(_op, op=operator.or_, slack=False)

    @singledispatchmethod
    def __iadd__(self, other: Iterable[SupportsIndex] | SupportsBytes) -> _BitArray:
        slack = self._num_slack()
        self >>= slack
        self.data += bytes(other)
        self._len += 8*len(other)
        self <<= slack
        return self
    @__iadd__.register
    def _(self, other: _BitArray) -> _BitArray:
        slack = self._num_slack()
        self >>= slack
        self.data += other.data
        self._len += len(other)
        self <<= slack
        return self


    def __add__(self, other: _BitArray | Iterable[SupportsIndex] | SupportsBytes) -> _BitArray:
        result = copy.copy(self)
        result += other
        return result
    
    def __copy__(self) -> _BitArray:
        return BitArray(copy.copy(self.data), order=self.order, _len=len(self))
    
    def __index__(self) -> int:
        return int.from_bytes(self.data, byteorder='little', signed=False)



