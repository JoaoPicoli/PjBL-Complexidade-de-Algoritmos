"""Reproducible local benchmarks of the two authorized strategies only."""
import argparse
import csv
import gc
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import tracemalloc

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'.tools/python'))
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'src/apoio'))
import numpy as np
from datacenter_python.bitmap import deduplicate_bitmap,DEFAULT_CHUNK
from native import NativeHeapsort

SEED=20261111
SIZES=(1000,100000,10000000)


def print_result(n,distribution,strategy,measured,memory):
    print(n,distribution,strategy,'median_s',float(np.median(measured)),
          'max_s',max(measured),
          'heap_aux_bytes',memory['heap_aux_pico'] if memory['heap_aux_pico']!='' else 'nao_isolado',
          'pilha_limite_estatico_bytes',memory['pilha_aux_estimada'] if memory['pilha_aux_estimada']!='' else 'nao_medido',
          'estatico_aux_bytes',memory['estatico_aux_bytes'],
          'bitmap_payload_bytes',memory['bitmap_payload_bytes'],
          'pico_rastreado_incl_saida_bytes',memory['pico_rastreado_bytes'] if memory['pico_rastreado_bytes']!='' else 'nao_aplicavel',
          'memory_id',memory['id_memoria'],flush=True)


def datasets(n):
    rng=np.random.default_rng(SEED)
    base=rng.integers(0,65536,size=n,dtype=np.uint16)
    yield 'iid_uniforme',base
    yield 'todas_iguais',np.full(n,42,dtype=np.uint16)
    a=np.empty(n,dtype=np.uint16)
    a[::2],a[1::2]=0,65535
    yield 'alternada_fronteiras',a
    yield 'ciclo_dominio',np.resize(np.arange(65536,dtype=np.uint16),n)
    ordered=np.sort(base)  # generate distribution, never part of timed deduplication
    yield 'ordenada',ordered
    yield 'reversa',ordered[::-1].copy()
    if n<=65536:
        yield 'sem_duplicatas',rng.choice(65536,size=n,replace=False).astype(np.uint16)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repeticoes',type=int,default=5)
    parser.add_argument('--mostrar',action='store_true',help='print saved local time/memory results without measuring again')
    args=parser.parse_args()
    if args.repeticoes<1:
        parser.error('repeticoes must be positive')
    if args.mostrar:
        with (ROOT/'dados/medicoes_memoria.csv').open(encoding='utf-8',newline='') as fp:
            memory={r['id_memoria']:r for r in csv.DictReader(fp)}
        with (ROOT/'dados/resultados_empiricos.csv').open(encoding='utf-8',newline='') as fp:
            saved=list(csv.DictReader(fp))
        print('Observacoes locais ja salvas; esta exibicao nao faz novas medicoes.')
        groups={}
        for row in saved:
            key=(int(row['n']),row['entrada'],int(row['estrategia']),row['id_memoria'])
            groups.setdefault(key,[]).append(float(row['tempo']))
        for (n,distribution,strategy,mid),times in groups.items():
            print_result(n,distribution,strategy,times,memory[mid])
        return
    native=NativeHeapsort()
    c_memory=json.loads((ROOT/'dados/memoria_c.json').read_text())
    fields=['n','estrategia','entrada','semente','repeticao','tempo','unidade_tempo',
            'heap_aux_pico','pilha_aux_estimada','estatico_aux_bytes','bitmap_payload_bytes',
            'pico_rastreado_bytes','entrada_bytes','saida_bytes','unidade_memoria',
            'metodo_memoria','id_memoria','ambiente','compilador_flags','entrada_sha256',
            'algoritmo_sha256','status']
    memfields=['id_memoria','n','estrategia','entrada','heap_aux_pico',
               'pilha_aux_estimada','estatico_aux_bytes','bitmap_payload_bytes',
               'buffers_lote_payload_bytes','emissao_temporarios_payload_bound_bytes',
               'pico_rastreado_bytes','retido_rastreado_bytes','saida_bytes',
               'alocacoes_chamadas','alocacoes_bytes_solicitados','metodo','unidade']
    environment=f'Ryzen 5 5600; {platform.platform()}; Python {platform.python_version()}; NumPy {np.__version__}; LOCAL'
    codehash={2:hashlib.sha256((ROOT/'src/embarcada_c/dedup.c').read_bytes()).hexdigest(),
              5:hashlib.sha256((ROOT/'src/datacenter_python/bitmap.py').read_bytes()).hexdigest()}
    datafile=ROOT/'dados/resultados_empiricos.csv'
    memoryfile=ROOT/'dados/medicoes_memoria.csv'
    rows_written=0
    with datafile.open('w',newline='',encoding='utf-8') as fp,memoryfile.open('w',newline='',encoding='utf-8') as mf:
        writer=csv.DictWriter(fp,fieldnames=fields);writer.writeheader()
        memwriter=csv.DictWriter(mf,fieldnames=memfields);memwriter.writeheader()
        for n in SIZES:
            for distribution,a in datasets(n):
                digest=hashlib.sha256(memoryview(a)).hexdigest()
                expected=np.unique(a)  # independent oracle, outside timing/memory scope
                for strategy in (2,5):
                    memory_id=f'{strategy}-{n}-{distribution}'
                    if strategy==2:
                        method='heap hooks measured each run; static stack/ABI bound and object sections; no RSS'
                        work=a.copy();native.reset();native.run(work)  # full-input warmup
                        native.reset();work=a.copy()
                        d=native.run(work)
                        np.testing.assert_array_equal(work[:d],expected)
                        calls,requested=native.allocations()
                        assert (calls,requested)==(0,0)
                        mem=dict(id_memoria=memory_id,n=n,estrategia=2,entrada=distribution,
                                 heap_aux_pico=0,pilha_aux_estimada=c_memory['stack_conservative_bound_bytes'],
                                 estatico_aux_bytes=0,bitmap_payload_bytes=0,buffers_lote_payload_bytes=0,
                                 emissao_temporarios_payload_bound_bytes=0,pico_rastreado_bytes='',
                                 retido_rastreado_bytes='',saida_bytes=d*2,alocacoes_chamadas=calls,
                                 alocacoes_bytes_solicitados=requested,metodo=method,unidade='byte')
                    else:
                        method='separate tracemalloc trial incl output and NumPy registered allocations; input excluded; stack/native untracked'
                        deduplicate_bitmap(a)  # full-input warmup
                        gc.collect();tracemalloc.start();tracemalloc.reset_peak()
                        output=deduplicate_bitmap(a)
                        retained,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
                        np.testing.assert_array_equal(output,expected)
                        d=output.size
                        mem=dict(id_memoria=memory_id,n=n,estrategia=5,entrada=distribution,
                                 heap_aux_pico='',pilha_aux_estimada='',estatico_aux_bytes=0,
                                 bitmap_payload_bytes=8192,buffers_lote_payload_bytes=3*min(n,DEFAULT_CHUNK),
                                 emissao_temporarios_payload_bound_bytes=65536+8*d,
                                 pico_rastreado_bytes=peak,retido_rastreado_bytes=retained,
                                 saida_bytes=output.nbytes,alocacoes_chamadas='',alocacoes_bytes_solicitados='',
                                 metodo=method,unidade='byte')
                    memwriter.writerow(mem);mf.flush()
                    measured=[]
                    for repetition in range(1,args.repeticoes+1):
                        if strategy==2:
                            work=a.copy()  # excluded from timer
                            pointer=native.pointer(work)  # boundary conversion excluded
                            native.reset()
                            start=time.perf_counter_ns()
                            d=int(native.function(pointer,n))
                            elapsed=(time.perf_counter_ns()-start)/1e9
                            output=work[:d]
                            assert native.allocations()==(0,0)
                        else:
                            start=time.perf_counter_ns()
                            output=deduplicate_bitmap(a)
                            elapsed=(time.perf_counter_ns()-start)/1e9
                        np.testing.assert_array_equal(output,expected)
                        if output.size>1:
                            assert np.all(output[1:]>output[:-1])
                        row=dict(n=n,estrategia=strategy,entrada=distribution,semente=SEED,
                                 repeticao=repetition,tempo=elapsed,unidade_tempo='s',
                                 heap_aux_pico=mem['heap_aux_pico'],pilha_aux_estimada=mem['pilha_aux_estimada'],
                                 estatico_aux_bytes=0,bitmap_payload_bytes=mem['bitmap_payload_bytes'],
                                 pico_rastreado_bytes=mem['pico_rastreado_bytes'],entrada_bytes=a.nbytes,
                                 saida_bytes=output.nbytes,unidade_memoria='byte',metodo_memoria=method,
                                 id_memoria=memory_id,ambiente=environment,
                                 compilador_flags='GCC 16.2.0 -O2 -std=c11 -fno-builtin -fno-stack-protector' if strategy==2 else f'NumPy bitwise_or.at; chunk={DEFAULT_CHUNK}',
                                 entrada_sha256=digest,algoritmo_sha256=codehash[strategy],status='medido_local')
                        writer.writerow(row);fp.flush();measured.append(elapsed);rows_written+=1
                    print_result(n,distribution,strategy,measured,mem)
    metadata={'timing_rows':rows_written,'memory_rows':38,'sizes':SIZES,
              'repetitions':args.repeticoes,'seed':SEED,'environment':environment,
              'warmups':'one full invocation per dataset/strategy',
              'timing_includes':'algorithm initialization and output; Python/ctypes call boundary',
              'timing_excludes':'input generation, copying, pointer conversion, oracle, validation, printing, memory instrumentation',
              'memory_trials':'one separate invocation per dataset/strategy; referenced by id_memoria',
              'output':'strictly increasing uint16 for both; C aliases input prefix',
              'reference_machine_verified':False,'chunk_size':DEFAULT_CHUNK,
              'source_sha256':codehash,'dll_sha256':c_memory['dll_sha256']}
    (ROOT/'dados/metodo_benchmark.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('Saved',rows_written,'timing observations',flush=True)


if __name__=='__main__':
    main()
