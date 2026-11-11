"""Audita entradas preservadas, dados locais, evidências e o PDF final."""
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.tools' / 'python'))
from pypdf import PdfReader


def main():
    results = {}
    inputs = json.loads((ROOT/'docs/entradas_sha256.json').read_text(encoding='utf-8'))
    assert len(inputs) == 6
    for item in inputs:
        path = ROOT/item['path']
        assert path.stat().st_size == item['bytes'], path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], path
    results['preserved_original_inputs'] = len(inputs)
    cases = json.loads((ROOT/'tests/casos_manuais.json').read_text(encoding='utf-8'))
    for case in cases:
        a = case['entrada']
        assert len(a) <= 10
        assert all(isinstance(x, int) and 0 <= x <= 65535 for x in a)
        expected = sorted(set(a))
        assert case['conjunto_esperado'] == expected
        assert case['crescente'] == expected
        assert case['primeira_aparicao'] == list(dict.fromkeys(a))
    results['manual_oracles_consistent'] = len(cases)
    with (ROOT/'dados/resultados_empiricos.csv').open(encoding='utf-8', newline='') as fp:
        observations=list(csv.DictReader(fp))
    assert len(observations)==190
    expected={(n,s,dist) for n in (1000,100000,10000000) for s in (2,5)
              for dist in ('iid_uniforme','todas_iguais','alternada_fronteiras',
                           'ciclo_dominio','ordenada','reversa')}
    expected|={(1000,s,'sem_duplicatas') for s in (2,5)}
    groups={}
    for row in observations:
        key=(int(row['n']),int(row['estrategia']),row['entrada'])
        groups.setdefault(key,[]).append(row)
        assert row['status']=='medido_local' and float(row['tempo'])>0
        assert row['unidade_tempo']=='s' and row['unidade_memoria']=='byte'
        assert int(row['entrada_bytes'])==2*int(row['n'])
    assert set(groups)==expected
    assert all(len(rows)==5 and {int(r['repeticao']) for r in rows}==set(range(1,6))
               for rows in groups.values())
    for n,_,dist in expected:
        cr=groups[(n,2,dist)][0];pr=groups[(n,5,dist)][0]
        assert cr['entrada_sha256']==pr['entrada_sha256']
    for strategy,path in [(2,'src/embarcada_c/dedup.c'),(5,'src/datacenter_python/bitmap.py')]:
        digest=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        assert all(r['algoritmo_sha256']==digest for r in observations if int(r['estrategia'])==strategy)
    with (ROOT/'dados/medicoes_memoria.csv').open(encoding='utf-8',newline='') as fp:
        memory=list(csv.DictReader(fp))
    assert len(memory)==38
    memory_byid={r['id_memoria']:r for r in memory}
    assert len(memory_byid)==38
    for row in observations:
        mem=memory_byid[row['id_memoria']]
        for field in ('heap_aux_pico','pilha_aux_estimada','estatico_aux_bytes',
                      'bitmap_payload_bytes','pico_rastreado_bytes','saida_bytes'):
            assert row[field]==mem[field]
    budget=json.loads((ROOT/'dados/memoria_c.json').read_text())
    assert budget['total_extra_bound_bytes']==104 and budget['passes_for_this_build']
    assert hashlib.sha256((ROOT/'.tools/dedup.dll').read_bytes()).hexdigest()==budget['dll_sha256']
    assert all(r['heap_aux_pico']=='0' and r['alocacoes_chamadas']=='0' and
               r['estatico_aux_bytes']=='0' for r in memory if r['estrategia']=='2')
    tests=json.loads((ROOT/'dados/testes_resultado.json').read_text())
    assert tests['successful'] and tests['tests_run']==9
    results['empirical_observations']=len(observations)
    results['separate_memory_trials']=len(memory)
    results['test_methods_passed']=9
    results['c_extra_bound_bytes']=104
    with (ROOT/'dados/custos_teoricos.csv').open(encoding='utf-8', newline='') as fp:
        rows = list(csv.DictReader(fp))
    assert len(rows) == 30
    assert {(int(row['n']),int(row['estrategia'])) for row in rows} == {
        (n,s) for n in [1000,100000,10000000] for s in range(1,11)}
    assert all(row['tipo'] == 'teorico' for row in rows)
    results['theoretical_rows'] = 30
    analysis = (ROOT/'docs/analise_teorica.md').read_text(encoding='utf-8')
    headings = re.findall(r'^# Estratégia (\d+):', analysis, re.M)
    assert headings == [str(i) for i in range(1,11)]
    results['strategies_with_sections'] = 10
    assert not list((ROOT/'formal').rglob('*.lean'))
    assert (ROOT/'src/embarcada_c/dedup.c').exists()
    assert (ROOT/'src/datacenter_python/bitmap.py').exists()
    implementation=(ROOT/'src/datacenter_python/bitmap.py').read_text()
    assert 'np.bitwise_or.at(bitmap, indices, bits)' in implementation
    assert not re.search(r'\b(set|unique|sort)\s*\(',implementation)
    results['implemented_strategies']=[2,5]
    results['lean_sources']='absent; no formal verification claimed'
    pdf = ROOT/'relatorios_latex/relatorio.pdf'
    reader = PdfReader(pdf)
    results['pdf_pages'] = len(reader.pages)
    text = '\n'.join(page.extract_text() for page in reader.pages)
    assert '\ufffd' not in text
    assert '628.684' in text
    assert '48.067.060,787435' in text
    assert '0.1026721' in text and '104' in text
    log = (ROOT/'relatorios_latex/relatorio.log').read_text(encoding='utf-8', errors='replace')
    assert 'Overfull' not in log
    assert 'Missing character' not in log
    results['tex_overfull_or_missing_glyphs'] = 0
    results['tex_underfull_paragraph_warnings'] = log.count('Underfull')
    tmp = ROOT/'tmp/pdfs'
    tmp.mkdir(parents=True, exist_ok=True)
    bbox = tmp/'relatorio-bbox.html'
    subprocess.run(['pdftotext','-bbox-layout',str(pdf),str(bbox)], check=True, cwd=ROOT)
    tree = ET.parse(bbox)
    ns = {'h':'http://www.w3.org/1999/xhtml'}
    words = 0
    for page in tree.findall('.//h:page',ns):
        width, height = float(page.attrib['width']),float(page.attrib['height'])
        for word in page.findall('.//h:word',ns):
            coords = {k:float(word.attrib[k]) for k in ('xMin','xMax','yMin','yMax')}
            assert coords['xMin'] >= -0.5 and coords['xMax'] <= width+0.5, (word.text,coords)
            assert coords['yMin'] >= -0.5 and coords['yMax'] <= height+0.5, (word.text,coords)
            words += 1
    assert words > 1000
    results['pdf_words_within_page_bounds'] = words
    results['limitations'] = ['Local runs only; course reference and actual sensor ABI unavailable',
                             'Visual inspection recorded separately',
                             'Professor approval not recorded; user authorized local work',
                             'No Lean compilation or kernel axiom audit']
    (ROOT/'docs/auditoria_entrega.json').write_text(
        json.dumps(results, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(results, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
