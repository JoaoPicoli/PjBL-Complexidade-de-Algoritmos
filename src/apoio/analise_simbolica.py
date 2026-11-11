"""Conferências e modelos; não implementa estratégias de deduplicação."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.tools' / 'python'))
import sympy as sp
import mpmath as mp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    n = sp.Symbol('n', integer=True, positive=True)
    i = sp.Symbol('i', integer=True, nonnegative=True)
    h = sp.Symbol('h', integer=True, nonnegative=True)
    z = sp.Symbol('z')
    U = sp.Integer(65536)
    triangular = sp.summation(i, (i, 0, n - 1))
    assert sp.simplify(triangular - n * (n - 1) / 2) == 0
    # Derivar (1+z)^n conta incidências de índices e pares de índices.
    subsets_elements = sp.diff((1 + z)**n, z).subs(z, 1)
    subsets_pairs = sp.diff((1 + z)**n, z, 2).subs(z, 1) / 2
    assert sp.simplify(subsets_elements - n * 2**(n - 1)) == 0
    assert sp.simplify(subsets_pairs - n * (n - 1) * 2**(n - 3)) == 0
    heap_sum = sp.summation(h / sp.Integer(2)**(h + 1), (h, 0, sp.oo))
    assert heap_sum == 1
    p = sp.Rational(1, 100)
    bloom_cont = -U * sp.log(p) / sp.log(2)**2
    bloom7_expr = -7 * U / sp.log(1 - p**sp.Rational(1, 7))
    bloom7_bits = int(sp.ceiling(bloom7_expr.evalf(70)))
    bloom7_rate = (1 - sp.exp(-7 * U / bloom7_bits))**7
    u = sp.Symbol('u', positive=True)
    optimum_condition = sp.log(1-sp.exp(-u)) + u*sp.exp(-u)/(1-sp.exp(-u))
    assert sp.simplify(optimum_condition.subs(u,sp.log(2))) == 0
    # Garantia exata para o modelo particionado pelo limite da união.
    assert sp.Rational(1, 128) < p
    data = {
        'software': {'python': sys.version.split()[0], 'sympy': sp.__version__,
                     'mpmath': mp.__version__, 'numpy': np.__version__,
                     'matplotlib': matplotlib.__version__},
        'assumptions': 'n inteiro >= 1; U=65536; n=0 tratado separadamente; hashes independentes uniformes quando usados',
        'identities_exact': {
            'triangular': str(triangular),
            'subsets_elements': str(subsets_elements),
            'subsets_pairs_n_ge_2': str(sp.factor(subsets_pairs)),
            'heap_series': str(heap_sum),
            'bitmap_bytes': str(U / 8), 'bitmap_over_embarca': str(U / 8 / 256),
            'bloom_continuous_bits': str(bloom_cont),
            'bloom_k7_bits_definition': 'ceiling(-7*65536/log(1-(1/100)**(1/7)))',
            'bloom_k7_bits': bloom7_bits,
            'bloom_k7_payload_bytes': (bloom7_bits + 7) // 8,
            'partitioned_bloom_bits': int(14 * U),
            'partitioned_bloom_bytes': int(14 * U / 8),
            'partitioned_bloom_upper_probability': '1/128',
            'unary_max_bytes_n_1e7': int(10**7 * U / 8),
            'unary_expected_bits_divided_by_8_n_1e7': str(10**7 * (U + 1) / 16),
            'unary_read_bytes_n_1e7': int(10**7 * U / 8 * U),
            'matrix_bytes_uint8_n_1e7': 10**14,
            'matrix_bytes_bits_n_1e7': 10**14 // 8,
            'subsets_n50': 2**50,
            'subsets_elements_n50': 50 * 2**49,
            'subsets_8byte_index_payload_n50': 8 * 50 * 2**49,
            'subsets_pairs_n50': math.comb(50, 2) * 2**48,
            'brute_comparisons_n_1e7': 10**7 * (10**7 - 1) // 2,
            'c_stack_conservative_bound': str(sp.Integer(56)+32+16),
            'bitmap_marking_explicit_payload_at_chunk_65536': str(U/8+3*U),
            'bitmap_emission_payload_peak_at_full_domain': str(U/8+U+8*U+2*U),
        },
        'approximations': {
            'bloom_continuous_bits': str(bloom_cont.evalf(18)),
            'bloom_bits_per_key': str((bloom_cont / U).evalf(18)),
            'bloom_opt_k': str((-sp.log(p) / sp.log(2)).evalf(18)),
            'bloom_k7_probability_exponential_model': str(bloom7_rate.evalf(18)),
            'bloom_256bytes_k1_probability': str((1-sp.exp(-U/2048)).evalf(18)),
            'bloom_capacity_256bytes_k7': str((-2048*sp.log(1-p**sp.Rational(1,7))/7).evalf(18)),
            'subsets_visit_n50_days_at_1e9_per_second': str((sp.Integer(2)**50 / (10**9 * sp.Integer(86400))).evalf(18)),
            'unary_read_days_at_1e9_bytes_per_second': str((10**7 * U**2 / (8*10**9 * sp.Integer(86400))).evalf(18)),
            'factorial_1000': str(sp.factorial(1000).evalf(18)),
        },
        'checks': 'all exact symbolic identities passed; probability 1/128 < 1/100 checked exactly',
    }
    (ROOT / 'dados' / 'calculos_sympy.json').write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    mp.mp.dps = 65

    def balanced_log_factorial(nn):
        dd = min(nn, int(U))
        aa, rr = divmod(nn, dd)
        return (mp.loggamma(nn+1) - rr*mp.loggamma(aa+2)
                - (dd-rr)*mp.loggamma(aa+1)) / mp.log(10)

    def costs(nn):
        dd = min(nn,int(U))
        aa, rr = divmod(nn,dd)
        return [
            (1, 'comparacoes', f'{nn}*({nn}-1)/2', mp.log10(nn*(nn-1)//2), 'prefixo completo'),
            (2, 'proxy_n_log2n', f'{nn}*log2({nn})', mp.log10(nn*mp.log(nn, 2)), 'proxy de pior caso, nao contagem exata'),
            (3, 'proxy_consultas', str(nn), mp.log10(nn), 'esperado, hashing uniforme e carga limitada'),
            (4, 'proxy_n_log2d', f'{nn}*log2({min(nn,int(U))+1})', mp.log10(nn*mp.log(min(nn,int(U))+1, 2)), 'limite AVL'),
            (5, 'proxy_acessos', f'{nn}+65536+8192', mp.log10(nn+65536+8192), 'marcacao, inicializacao e varredura crescente do dominio; proxy'),
            (6, 'proxy_hashes_e_inicializacao', f'7*{nn}+114688', mp.log10(7*nn+114688), 'Bloom particionado k=7, D=U'),
            (7, 'proxy_trabalho_esperado', f'{nn}*factorial({nn})/(factorial({aa+1})**{rr}*factorial({aa})**{dd-rr})', mp.log10(nn)+balanced_log_factorial(nn), 'multiconjunto balanceado, embaralhamentos independentes'),
            (8, 'comparacoes_pares_subconjuntos', f'binomial({nn},2)*2**({nn}-2)', mp.log10(math.comb(nn,2))+(nn-2)*mp.log10(2), 'todos os subconjuntos, todos os pares'),
            (9, 'proxy_operacoes_bits', f'65536*{nn}*65537/2', mp.log10(mp.mpf(65536)*nn*65537/2), 'U passagens, media iid uniforme'),
            (10, 'comparacoes_construcao', f'{nn}**2', 2*mp.log10(nn), 'preenchimento da matriz; nao inclui leitura triangular'),
        ]

    with (ROOT / 'dados' / 'custos_teoricos.csv').open('w', newline='', encoding='utf-8') as fp:
        writer = csv.writer(fp)
        writer.writerow(['n','estrategia','tipo','unidade','expressao_exata_modelo','log10_custo_aproximado','hipotese'])
        for nn in (1000, 100000, 10000000):
            for strategy, unit, expression, logvalue, assumption in costs(nn):
                writer.writerow([nn, strategy, 'teorico', unit, expression, mp.nstr(logvalue, 22), assumption])

    plt.rcParams.update({'font.size': 11.5})
    fig, axes = plt.subplots(2, 1, figsize=(8.2, 10.2), constrained_layout=True)
    ns = np.unique(np.geomspace(1000, 10000000, 140).astype(int))
    all_costs = [costs(int(nn)) for nn in ns]
    labels = {
        1:'1 Força bruta: comparações', 2:'2 Heapsort: proxy n log₂ n',
        3:'3 Hash: proxy esperado n', 4:'4 AVL: proxy n log₂(d+1)',
        5:'5 Bitmap: n + U + U/8', 6:'6 Bloom: 7n + 114.688',
        7:'7 Bogosort: esperado, balanceado', 8:'8 Subconjuntos: testes de pares',
        9:'9 Unária: U passagens, iid', 10:'10 Matriz: construção n²',
    }
    for strategy in range(1, 11):
        ax = axes[1 if strategy in (7, 8) else 0]
        ys = [float(row[strategy-1][3]) for row in all_costs]
        ax.plot(ns, ys, linestyle='--', label=labels[strategy], linewidth=1.6)
    for ax in axes:
        ax.set_xscale('log')
        ax.set_xlabel('n (número de leituras)')
        ax.set_ylabel('log₁₀(custo do modelo)')
        ax.grid(alpha=0.25)
        ax.legend(fontsize=10.5, ncol=2 if ax is axes[0] else 1,
                  loc='upper center', bbox_to_anchor=(0.5,-0.16))
    axes[0].set_title('Modelos polinomiais - sem conversão para segundos', fontsize=12)
    axes[1].set_title('Modelos combinatórios - escala vertical própria', fontsize=12)
    fig.suptitle('Dez estratégias: curvas teóricas, nenhuma medição', fontsize=13)
    fig.savefig(ROOT / 'figuras' / 'modelos_teoricos.png', dpi=170)
    plt.close(fig)
    print('Identidades exatas conferidas; JSON, CSV teórico (30 linhas) e figura gerados.')
    print(json.dumps(data['approximations'], ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
