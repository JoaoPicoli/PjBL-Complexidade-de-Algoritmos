"""Compare scalar and NumPy bitmap batches; time and memory use separate trials."""
import csv
import gc
import json
from pathlib import Path
import sys
import time
import tracemalloc

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'.tools/python'))
sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from datacenter_python.bitmap import deduplicate_bitmap,deduplicate_bitmap_scalar


def measure_memory(function,a):
    gc.collect()
    tracemalloc.start()
    tracemalloc.reset_peak()
    out = function(a)
    current,peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return out,current,peak


def main():
    rng = np.random.default_rng(20261111)
    a = rng.integers(0,65536,size=10_000_000,dtype=np.uint16)
    expected = np.unique(a)  # independent oracle, never part of timed algorithm
    variants = [('escalar',deduplicate_bitmap_scalar)] + [
        (f'numpy_lote_{chunk}',lambda x,c=chunk:deduplicate_bitmap(x,c))
        for chunk in (4096,65536,1048576,10000000)]
    rows=[]
    for label,function in variants:
        function(a[:1000])
        for repetition in range(1,4):
            start=time.perf_counter_ns()
            out=function(a)
            elapsed=(time.perf_counter_ns()-start)/1e9
            np.testing.assert_array_equal(out,expected)
            rows.append({'variante':label,'n':a.size,'entrada':'iid_uniforme',
                         'semente':20261111,'repeticao':repetition,'tempo_s':elapsed,
                         'pico_rastreado_bytes':'','retido_rastreado_bytes':'',
                         'tipo':'tempo','saida_bytes':out.nbytes})
        out,current,peak=measure_memory(function,a)
        np.testing.assert_array_equal(out,expected)
        rows.append({'variante':label,'n':a.size,'entrada':'iid_uniforme',
                     'semente':20261111,'repeticao':1,'tempo_s':'',
                     'pico_rastreado_bytes':peak,'retido_rastreado_bytes':current,
                     'tipo':'memoria','saida_bytes':out.nbytes})
        print(label,'seconds', [r['tempo_s'] for r in rows if r['variante']==label and r['tipo']=='tempo'],
              'traced peak',peak,flush=True)
    with (ROOT/'dados/avaliacao_bitmap.csv').open('w',encoding='utf-8',newline='') as fp:
        writer=csv.DictWriter(fp,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    # Check that the current NumPy build exposes its data allocations to tracemalloc.
    tracemalloc.start()
    probe=np.empty(1_000_000,dtype=np.uint8)
    current,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert peak >= probe.nbytes
    (ROOT/'dados/tracemalloc_numpy.json').write_text(json.dumps({
        'numpy':np.__version__,'payload_probe_bytes':probe.nbytes,'traced_current':current,
        'traced_peak':peak,'numpy_domain':np.lib.tracemalloc_domain,
        'scope':'Python and registered NumPy allocations; excludes preexisting input, not a full native RSS/stack profiler'
    },indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
