"""ctypes boundary to the C algorithm; validation/copies are caller work."""
import ctypes
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'.tools/python'))
import numpy as np


class NativeHeapsort:
    def __init__(self):
        self.lib = ctypes.CDLL(str(ROOT/'.tools/dedup.dll'))
        self.function = self.lib.dedup_heapsort_u16
        self.function.argtypes = [ctypes.POINTER(ctypes.c_uint16),ctypes.c_size_t]
        self.function.restype = ctypes.c_size_t
        self.lib.pjbl_alloc_reset.argtypes = []
        self.lib.pjbl_alloc_reset.restype = None
        for name in ('pjbl_alloc_calls','pjbl_alloc_requested'):
            f = getattr(self.lib,name)
            f.argtypes = []
            f.restype = ctypes.c_size_t

    @staticmethod
    def pointer(values):
        if values.dtype != np.uint16 or values.ndim != 1 or not values.flags.c_contiguous:
            raise TypeError('C input must be contiguous one-dimensional uint16')
        return values.ctypes.data_as(ctypes.POINTER(ctypes.c_uint16))

    def reset(self):
        self.lib.pjbl_alloc_reset()

    def allocations(self):
        return int(self.lib.pjbl_alloc_calls()),int(self.lib.pjbl_alloc_requested())

    def run(self, values):
        return int(self.function(self.pointer(values),values.size))
