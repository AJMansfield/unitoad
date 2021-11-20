import itertools
from typing import Generator, Iterable, Iterator, Optional, TypeVar

T = TypeVar('T')
def chunks(it: Iterator[T], n:int, pad: Optional[T] = None) -> Generator[list[T],None,None]:
    while True:
        result = [pad]*n
        try:
            result[0] = next(it) # called outside context so we StopIteration if there are _no_ items left.
        except StopIteration:
            return
        for i in range(1,n):
            try:
                result[i] = next(it)
            except StopIteration:
                break
        else:
            yield result
            continue
        yield result
        break

def dump_char_for_byte(byte:int) -> str:
    s = bytes([byte]).decode(errors='replace')
    if s == '�':
        return '□'
    elif not s.isprintable():
        return '□'
    elif s.isspace(): # don't want tabs or newlines or anything
        return ' '
    else:
        return s

def transpose(m: tuple[Iterable[T], ...]) -> tuple[tuple[T, ...], ...]:
    return tuple(zip(*m))

def format_line(bits: tuple[str, ...], hex: tuple[str, ...], char: tuple[str, ...]) -> str:
    return ' | '.join([
            ' '.join(bits),
            ' '.join(hex),
            ''.join(char),
        ])

def bit_dump(data:bytes, cols:int=4) -> str:
    as_bits = map("{:08b}".format, data)
    as_hex = map("{:02x}".format, data)
    as_chr = map(dump_char_for_byte, data)
    all_formats = zip(as_bits, as_hex, as_chr)
    it = chunks(all_formats, n=cols, pad=('        ', '  ', ' '))
    it = map(transpose, it)
    it = (format_line(*a) for a in it)
    return '\n'.join(it)

    # bits, hex, char = itertools.tee(it, 3)
    # bits = map(lambda x: ' '.join(x[0]), bits)
    # hex =  map(lambda x: ' '.join(x[1]), hex)
    # char = map(lambda x: ''.join(x[2]),  char)
    # it = zip(bits, hex, char)
    # it = map(' | '.join, it)
    # return '\n'.join(it)
