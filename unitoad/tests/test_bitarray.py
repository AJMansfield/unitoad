from inspect import BoundArguments
import operator
from typing import Iterable

from unitoad.bitarray import BitArray
import pytest
from random import randbytes
from itertools import product, zip_longest


short_test_data = [
    b'Hello there!',
    b'General Kenobi!',
    b'',
    b'\0' * 19,
    b'\xff' * 20,
    randbytes(21),
]
long_test_data = [
    *short_test_data,
    *(b'\0'*n for n in range(1,16)),
    *(b'\xff'*n for n in range(1,16)),
    *(randbytes(n) for n in range(1,16)),
]

def assert_sequences_equal(A, B):
    assert len(A) == len(B)
    for i, (a, b) in enumerate(zip(A,B)):
        assert a == b, f"mismatch at index {i}"

def make_bit_list(byt: bytes, slack:int = 0) -> list[bool]:
    l = [bit == '1' for bit in ''.join(map('{:08b}'.format, byt))]
    if slack == 0:
        return l
    else:
        return l[:-slack]

class slicer:
    def __class_getitem__(cls, key):
        return key

def make_bitarray(data, slack=0):
    if slack == 0:
        return BitArray(data)
    else:
        if 8*len(data) - slack < 0:
            pytest.skip('negative length')
        return BitArray(data, _len = 8*len(data) - slack)


@pytest.mark.parametrize('data', long_test_data)
def test_init(data):
    arr = BitArray(data)
    ref = make_bit_list(data)
    assert_sequences_equal(arr, ref)

@pytest.mark.parametrize('data, slack', product(long_test_data, range(1,8)))
def test_init_slack(data, slack):
    arr = make_bitarray(data, slack=slack)
    ref = make_bit_list(data, slack=slack)
    assert_sequences_equal(arr, ref)

@pytest.mark.parametrize('data, idx', product(long_test_data, range(64)))
def test_index(data, idx):
    arr = BitArray(data)
    ref = make_bit_list(data)
    try:
        ref[idx]
    except IndexError:
        with pytest.raises(IndexError):
            arr[idx]
    else:
        assert arr[idx] == ref[idx]

@pytest.mark.parametrize('data, slack, slice_', product(short_test_data, range(8), [
    slicer[:],
    slicer[6:],
    slicer[-5:],
    slicer[1:-1],
    slicer[::2],
    slicer[100:101],
]))
def test_slice(data, slack, slice_):
    arr = make_bitarray(data, slack)
    ref = make_bit_list(data, slack)
    assert_sequences_equal(arr[slice_], ref[slice_])

@pytest.mark.parametrize('op, A, sA, B, sB', product([operator.iand, operator.ior, operator.ixor], short_test_data, range(8), short_test_data, range(8)))
def test_iop(op, A, sA, B, sB):
    A_arr = make_bitarray(A, sA)
    A_ref = make_bit_list(A, sA)
    B_arr = make_bitarray(B, sB)
    B_ref = make_bit_list(B, sB)

    A_arr = op(A_arr, B_arr)
    A_ref = [op(a, b) for a, b in zip_longest(A_ref, B_ref, fillvalue=True)]
    assert_sequences_equal(A_arr, A_ref)

@pytest.mark.parametrize('A, sA, B, sB', product(short_test_data, range(8), short_test_data, range(8)))
def test_concat(A, sA, B, sB):
    A_arr = make_bitarray(A, sA)
    A_ref = make_bit_list(A, sA)
    B_arr = make_bitarray(B, sB)
    B_ref = make_bit_list(B, sB)

    A_arr += B_arr
    A_ref += B_ref
    assert_sequences_equal(A_arr, A_ref)