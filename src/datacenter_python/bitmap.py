"""Exact packed bitmap over uint16 values; output is strictly increasing.

NumPy's unbuffered ufunc.at accumulates all masks at repeated byte indices.
No set, sort, unique or histogram substitutes for the 8192-byte bitmap.
"""
from __future__ import annotations

import numpy as np

DOMAIN = 1 << 16
BITMAP_BYTES = DOMAIN // 8
DEFAULT_CHUNK = 1 << 16


def _validate(values: np.ndarray) -> None:
    if not isinstance(values, np.ndarray):
        raise TypeError('expected a numpy.ndarray; conversion belongs outside the timer')
    if values.dtype != np.dtype(np.uint16) or values.ndim != 1:
        raise TypeError('expected a one-dimensional native uint16 array')
    if not values.flags.c_contiguous:
        raise ValueError('input must be contiguous; copy explicitly outside the timer')


def build_bitmap(values: np.ndarray, chunk_size: int = DEFAULT_CHUNK) -> np.ndarray:
    """Return 8192 uint8 bytes. Bit (x % 8) of byte (x // 8) marks x."""
    _validate(values)
    if not isinstance(chunk_size, int) or isinstance(chunk_size, bool) or chunk_size <= 0:
        raise ValueError('chunk_size must be a positive integer')
    bitmap = np.zeros(BITMAP_BYTES, dtype=np.uint8)
    count = min(values.size, chunk_size)
    byte_indices = np.empty(count, dtype=np.uint16)
    masks = np.empty(count, dtype=np.uint8)
    for start in range(0, values.size, chunk_size):
        part = values[start:start + chunk_size]  # view, no payload copy
        length = part.size
        indices = byte_indices[:length]
        bits = masks[:length]
        np.right_shift(part, 3, out=indices)
        np.bitwise_and(part, 7, out=bits, casting='unsafe')
        np.left_shift(np.uint8(1), bits, out=bits)
        # Advanced indexed assignment with |= would buffer and lose bits.
        np.bitwise_or.at(bitmap, indices, bits)
    return bitmap


def deduplicate_bitmap(values: np.ndarray, chunk_size: int = DEFAULT_CHUNK) -> np.ndarray:
    """Build the packed bitmap, then enumerate its set bits in domain order."""
    bitmap = build_bitmap(values, chunk_size)
    # unpackbits uses little-endian bit order within each byte, matching marking.
    # flatnonzero enumerates domain positions, not the original input values.
    flags = np.unpackbits(bitmap, bitorder='little')
    return np.flatnonzero(flags).astype(np.uint16)


def deduplicate_bitmap_scalar(values: np.ndarray) -> np.ndarray:
    """Scalar baseline of the SAME bitmap strategy, for local comparison."""
    _validate(values)
    bitmap = bytearray(BITMAP_BYTES)
    for value in values:
        x = int(value)
        bitmap[x >> 3] |= 1 << (x & 7)
    return np.fromiter((x for x in range(DOMAIN)
                        if bitmap[x >> 3] & (1 << (x & 7))), dtype=np.uint16)
