"""Behavioral, boundary and repeated-index regression tests for both strategies."""
import ctypes
import itertools
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'src/apoio'))
import numpy as np
from datacenter_python.bitmap import build_bitmap,deduplicate_bitmap,deduplicate_bitmap_scalar
from native import NativeHeapsort


class DedupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native = NativeHeapsort()

    def check_both(self, sequence):
        a = np.asarray(sequence,dtype=np.uint16)
        expected = np.array(sorted(set(map(int,a))),dtype=np.uint16)
        before = a.copy()
        working = a.copy()
        self.native.reset()
        size = self.native.run(working)
        np.testing.assert_array_equal(working[:size],expected)
        self.assertEqual(self.native.allocations(),(0,0))
        for chunk in (1,7,65536):
            np.testing.assert_array_equal(deduplicate_bitmap(a,chunk),expected)
        np.testing.assert_array_equal(a,before)

    def test_manual_oracles(self):
        for case in json.loads((ROOT/'tests/casos_manuais.json').read_text(encoding='utf-8')):
            with self.subTest(case=case['nome']):
                self.check_both(case['entrada'])
                np.testing.assert_array_equal(deduplicate_bitmap_scalar(
                    np.array(case['entrada'],dtype=np.uint16)),case['crescente'])

    def test_c_empty_null(self):
        self.assertEqual(self.native.function(None,0),0)

    def test_allocation_counter_positive_control(self):
        fixture = ctypes.CDLL(str(ROOT/'.tools/allocation_fixture.dll'))
        fixture.pjbl_allocation_fixture.restype = ctypes.c_void_p
        fixture.pjbl_alloc_calls.restype = ctypes.c_size_t
        fixture.pjbl_alloc_requested.restype = ctypes.c_size_t
        fixture.pjbl_alloc_reset()
        self.assertIsNone(fixture.pjbl_allocation_fixture())
        self.assertEqual(fixture.pjbl_alloc_calls(),1)
        self.assertEqual(fixture.pjbl_alloc_requested(),17)

    def test_exhaustive_short_inputs(self):
        # 1+3+9+27+81+243 cases, independent reference only outside algorithms.
        for size in range(6):
            for a in itertools.product((0,1,65535),repeat=size):
                self.check_both(a)

    def test_generated_inputs(self):
        rng = np.random.default_rng(20261111)
        for size in (2,3,4,7,8,9,31,64,101,1024):
            for _ in range(4):
                self.check_both(rng.integers(0,65536,size=size,dtype=np.uint16))

    def test_no_writes_outside_input(self):
        rng = np.random.default_rng(20261112)
        for size in (0,1,2,3,8,100,1000):
            guarded = np.empty(size+2,dtype=np.uint16)
            guarded[0],guarded[-1] = 12345,54321
            guarded[1:-1] = rng.integers(0,65536,size=size,dtype=np.uint16)
            self.native.run(guarded[1:-1])
            self.assertEqual(int(guarded[0]),12345)
            self.assertEqual(int(guarded[-1]),54321)

    def test_repeated_byte_indices_accumulate_all_bits(self):
        a = np.array([0,1,2,7,0,1,8,9,15,65528,65535],dtype=np.uint16)
        bitmap = build_bitmap(a,3)
        self.assertEqual(bitmap.dtype,np.uint8)
        self.assertEqual(bitmap.nbytes,8192)
        self.assertEqual(int(bitmap[0]),0b10000111)
        self.assertEqual(int(bitmap[1]),0b10000011)
        self.assertEqual(int(bitmap[-1]),0b10000001)

    def test_full_domain_shuffled_and_repeated(self):
        rng = np.random.default_rng(7)
        a = np.tile(np.arange(65536,dtype=np.uint16),2)
        rng.shuffle(a)
        expected = np.arange(65536,dtype=np.uint16)
        np.testing.assert_array_equal(deduplicate_bitmap(a,65535),expected)
        np.testing.assert_array_equal(build_bitmap(a),np.full(8192,255,dtype=np.uint8))
        n = self.native.run(a)
        self.assertEqual(n,65536)
        np.testing.assert_array_equal(a[:n],expected)

    def test_python_input_contract(self):
        for bad in ([1],np.array([1],dtype=np.int64),np.zeros((2,2),dtype=np.uint16)):
            with self.assertRaises(TypeError):
                deduplicate_bitmap(bad)
        with self.assertRaises(ValueError):
            deduplicate_bitmap(np.arange(10,dtype=np.uint16)[::2])
        for size in (0,-1,True):
            with self.assertRaises(ValueError):
                deduplicate_bitmap(np.array([],dtype=np.uint16),size)


if __name__ == '__main__':
    unittest.main(verbosity=2)
