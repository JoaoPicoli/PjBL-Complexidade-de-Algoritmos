"""Aggregate real observations and plot measured points plus eight theory curves."""
import csv
import json
import math
from pathlib import Path
import statistics
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'.tools/python'))
import mpmath as mp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    with (ROOT/'dados/resultados_empiricos.csv').open(encoding='utf-8',newline='') as fp:
        rows=list(csv.DictReader(fp))
    groups={}
    for row in rows:
        key=(int(row['n']),int(row['estrategia']),row['entrada'])
        groups.setdefault(key,[]).append(float(row['tempo']))
    summary=[]
    for (n,strategy,distribution),values in sorted(groups.items()):
        summary.append(dict(n=n,estrategia=strategy,entrada=distribution,repeticoes=len(values),
                            mediana_s=statistics.median(values),minimo_s=min(values),
                            maximo_s=max(values),desvio_padrao_s=statistics.stdev(values)))
    with (ROOT/'dados/resumo_empirico.csv').open('w',encoding='utf-8',newline='') as fp:
        writer=csv.DictWriter(fp,fieldnames=list(summary[0]))
        writer.writeheader();writer.writerows(summary)
    bykey={(r['n'],r['estrategia'],r['entrada']):r for r in summary}
    ns=np.array([1000,100000,10000000])
    plt.rcParams.update({'font.size':11})
    colors={2:'#16688a',5:'#b44c20'}
    names={2:'2 Heapsort C (medido)',5:'5 Bitmap NumPy (medido)'}
    # Readable measured-only view. Bars are min/max of five runs, not CIs.
    fig,ax=plt.subplots(figsize=(8.2,5.2),constrained_layout=True)
    for strategy in (2,5):
        selected=[bykey[(int(n),strategy,'iid_uniforme')] for n in ns]
        median=np.array([r['mediana_s'] for r in selected])
        low=np.array([r['minimo_s'] for r in selected])
        high=np.array([r['maximo_s'] for r in selected])
        ax.errorbar(ns,median,yerr=[median-low,high-median],marker='o',linestyle='-',
                    capsize=4,label=names[strategy],color=colors[strategy])
    ax.axhline(2,color='#666666',linestyle=':',label='Limiar de 2 s')
    ax.set(xscale='log',yscale='log',xlabel='n (leituras)',ylabel='Tempo medido (s)',
           title='Máquina local, iid uniforme - mediana e mínimo/máximo')
    ax.grid(alpha=.25);ax.legend(fontsize=10)
    fig.savefig(ROOT/'figuras/tempos_medidos.png',dpi=180);plt.close(fig)

    # One explicit visual calibration shared by all eight unimplemented models.
    n0=100000
    tref=bykey[(n0,5,'iid_uniforme')]['mediana_s']
    fref=n0+65536+8192
    c=tref/fref
    mp.mp.dps=55
    xx=np.unique(np.geomspace(1000,10000000,130).astype(int))
    U=65536
    models={1:xx*(xx-1)/2,3:xx,4:xx*np.log2(np.minimum(xx,U)+1),
            6:7*xx+114688,9:U*xx.astype(float)*(U+1)/2,10:xx.astype(float)**2}
    labels={1:'1 Força bruta',3:'3 Hash (esperado)',4:'4 AVL (limite)',
            6:'6 Bloom (k=7)',9:'9 Unária (U passagens)',10:'10 Matriz'}
    fig,axes=plt.subplots(2,1,figsize=(8.2,10.4),constrained_layout=True)
    for strategy,work in models.items():
        axes[0].plot(xx,c*work,'--',linewidth=1.3,label=labels[strategy]+' (teoria)')
    for strategy in (2,5):
        selected=[bykey[(int(n),strategy,'iid_uniforme')] for n in ns]
        median=np.array([r['mediana_s'] for r in selected])
        low=np.array([r['minimo_s'] for r in selected])
        high=np.array([r['maximo_s'] for r in selected])
        axes[0].errorbar(ns,median,yerr=[median-low,high-median],fmt='o-',
                         capsize=3,color=colors[strategy],label=names[strategy],linewidth=2)
    axes[0].set_yscale('log')
    axes[0].set_ylabel('Segundos medidos / modelos calibrados')
    axes[0].set_title('Pontos sólidos medidos; seis modelos tracejados',fontsize=12)
    bogolog=[];powerlog=[]
    for n in map(int,xx):
        d=min(n,U);a,r=divmod(n,d)
        logmult=(mp.loggamma(n+1)-r*mp.loggamma(a+2)-(d-r)*mp.loggamma(a+1))/mp.log(10)
        bogolog.append(float(mp.log10(c)+mp.log10(n)+logmult))
        powerlog.append(float(mp.log10(c)+mp.log10(math.comb(n,2))+(n-2)*mp.log10(2)))
    axes[1].plot(xx,bogolog,'--',label='7 Bogosort: esperado, balanceado')
    axes[1].plot(xx,powerlog,'--',label='8 Subconjuntos: todos os pares')
    axes[1].set_ylabel('log₁₀(segundos do modelo)')
    axes[1].set_title('Dois modelos combinatórios - escala própria',fontsize=12)
    for ax in axes:
        ax.set_xscale('log');ax.set_xlabel('n (leituras)');ax.grid(alpha=.25)
        ax.legend(fontsize=10,loc='upper center',bbox_to_anchor=(.5,-.17),
                  ncol=2 if ax is axes[0] else 1)
    fig.suptitle('Duas estratégias medidas e oito curvas teóricas',fontsize=13)
    fig.savefig(ROOT/'figuras/comparacao_completa.png',dpi=180);plt.close(fig)
    python_large=[r for r in rows if r['estrategia']=='5' and int(r['n'])==10000000]
    result={'timing_rows':len(rows),'groups':len(groups),'reference_n':n0,
            'reference_strategy':5,'reference_distribution':'iid_uniforme',
            'reference_time_s':tref,'reference_proxy':fref,'shared_visual_scale_s_per_unit':c,
            'models':[1,3,4,6,7,8,9,10],
            'calibration_warning':'Shared constant is a plotting convention, not a validated per-algorithm seconds prediction; units differ, especially disk I/O.',
            'local_python_n1e7_max_s':max(float(r['tempo']) for r in python_large),
            'local_python_n1e7_observations':len(python_large),
            'local_python_all_n1e7_under_2s':all(float(r['tempo'])<2 for r in python_large),
            'reference_machine_verified':False}
    (ROOT/'dados/resumo_resultados.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    # Inclusion produces the same tables in Markdown and the generated LaTeX.
    lines=['# Resultados locais e evidências','',
           'Ambiente: Ryzen 5 5600, Windows 11 Pro x64 (10.0.26300), Python 3.12.5, '
           'NumPy 2.1.2 e GCC 16.2.0. São 190 tempos em cinco repetições de 38 '
           'combinações de tamanho, distribuição e estratégia; há 38 ensaios de '
           'memória separados. Todas as 190 saídas foram conferidas com oráculo '
           'independente, fora da região cronometrada.','',
           '## Tempos com leituras iid uniformes','',
           '| n | Heapsort C: mediana (s) | Bitmap NumPy: mediana (s) |',
           '|--:|--:|--:|']
    for n in ns:
        number=f'{int(n):,}'.replace(',','.')
        lines.append(f"| {number} | {bykey[(int(n),2,'iid_uniforme')]['mediana_s']:.7f} | {bykey[(int(n),5,'iid_uniforme')]['mediana_s']:.7f} |")
    lines+=['','Valores decimais com ponto. Os dados brutos preservam todas as '
            'repetições, e `resumo_empirico.csv` inclui mínimos, máximos e desvio '
            'padrão amostral. Não se trata de intervalo de confiança.','',
            '## Todas as distribuições em n = 10⁷','',
            '| Entrada | C: mediana (s) | Bitmap: mediana (s) | Bitmap: máximo (s) |',
            '|:--|--:|--:|--:|']
    for distribution in ['iid_uniforme','todas_iguais','alternada_fronteiras','ciclo_dominio','ordenada','reversa']:
        cr=bykey[(10000000,2,distribution)];pr=bykey[(10000000,5,distribution)]
        lines.append(f"| {distribution.replace('_',' ')} | {cr['mediana_s']:.7f} | {pr['mediana_s']:.7f} | {pr['maximo_s']:.7f} |")
    lines+=['',f"O maior tempo das 30 observações do bitmap em n = 10⁷ foi **{result['local_python_n1e7_max_s']:.7f} s**, "
            'inferior a 2 s na máquina local. Isso satisfaz o limiar nesta amostra '
            'local; não é garantia universal de prazo nem comprovação na máquina '
            'de referência da disciplina, que não foi disponibilizada.','',
            '![Somente observações locais iid: pontos e linhas sólidas; barras indicam mínimo e máximo de cinco repetições.](../figuras/tempos_medidos.png)','',
            '## Evidência de memória da Embarca','',
            'O GCC reportou **56 bytes** de pilha estática para a única função '
            'do algoritmo. A desmontagem confirma seis pushes de registradores '
            '(48 bytes) e endereço de retorno (8 bytes), sem chamadas internas '
            'nem ajuste adicional de rsp. As versões instrumentada e normal têm '
            'código de máquina idêntico. Reservando ainda 32 bytes de home space '
            'do chamador Win64 e 16 bytes conservadores de alinhamento, o limite é','',
            '$$S_{\\mathrm{extra}} \\le 56+32+16+0_{\\mathrm{heap}}+0_{\\text{estático}}=104\\ \\text{bytes}<256.$$',
            '', 'As seções .data e .bss do objeto do algoritmo têm tamanho zero. '
            'Contadores de malloc, calloc, realloc e free registraram zero chamadas '
            'e zero bytes solicitados em todos os tamanhos e distribuições. '
            'Um controle positivo em DLL separada detectou uma tentativa de '
            '17 bytes, evitando uma instrumentação que sempre retorna zero. '
            'O objeto não tem símbolos indefinidos e a função não chama rotinas '
            'externas; assim também se confere a ausência de alocações ocultas '
            'nesse objeto.','',
            'Esse é um **limite estático conservador do build local x64**, '
            'conferido com relatórios e instruções, não uma leitura dinâmica '
            'da pilha nem RSS. Não inclui entrada/saída aliasada, código de '
            'máquina, metadados somente de leitura do objeto, Python/ctypes, '
            'CRT, SO ou interrupções. Os contadores pertencem ao aparato de '
            'auditoria, não ao objeto do algoritmo. Outra ABI, compilador ou '
            'sensor exige repetir essa auditoria.','',
            '## Temporários e seleção do bitmap','',
            'A avaliação em `avaliacao_bitmap.csv` mediu a versão escalar e '
            'lotes NumPy de 4.096, 65.536, 1.048.576 e 10.000.000 elementos: '
            'três tempos e um ensaio de memória por variante, todos iid com '
            'n = 10⁷. O lote de 65.536 foi escolhido pelo equilíbrio entre '
            'tempo e memória; a variante integral não foi escolhida só por '
            'ser marginalmente mais rápida.','',
            '| Variante | Mediana local (s) | Pico rastreado (bytes) |',
            '|:--|--:|--:|']
    with (ROOT/'dados/avaliacao_bitmap.csv').open(encoding='utf-8',newline='') as fp:
        candidates=list(csv.DictReader(fp))
    for label in dict.fromkeys(r['variante'] for r in candidates):
        times=[float(r['tempo_s']) for r in candidates if r['variante']==label and r['tipo']=='tempo']
        peak=next(int(r['pico_rastreado_bytes']) for r in candidates if r['variante']==label and r['tipo']=='memoria')
        lines.append(f"| {label.replace('_',' ')} | {statistics.median(times):.7f} | {peak} |")
    lines+=['', 'Para c = 65.536, a marcação mantém bitmap de 8.192 bytes, '
            'índices uint16 de 2c bytes e máscaras uint8 de c bytes, total de '
            'payload explícito 204.800 bytes. As fatias são views, não cópias. '
            'Os dois buffers saem de escopo antes da emissão. Esta usa U bytes '
            'de flags, até 8d bytes de índices intp e 2d bytes de saída; seu '
            'pico simultâneo de payload é','',
            '$$8\\,192+65\\,536+8d+2d\\le729\\,088\\ \\text{bytes}.$$',
            '', 'O ensaio com domínio completo registrou pico **730.080 bytes**, '
            'incluindo a saída de 131.072 bytes e cabeçalhos/temporários '
            'rastreáveis. Não se subtrai a saída do pico para inventar um '
            'pico auxiliar, pois os máximos podem ocorrer em instantes '
            'diferentes. `medicoes_memoria.csv` separa payloads analíticos, '
            'pico rastreado e tamanho da saída. Um probe de 1.000.000 bytes '
            'de NumPy produziu 1.000.096 bytes rastreados, confirmando que '
            'esta distribuição registra seus buffers de dados no tracemalloc. '
            'Esse profiler cobre Python e alocações NumPy registradas, não '
            'toda a pilha ou todo buffer nativo interno; não é RSS nem '
            'medida exaustiva do processo.','',
            '## Duas medições e oito extrapolações','',
            '![Comparação combinada: duas séries empíricas iid e oito modelos tracejados. O painel combinatório tem escala vertical própria.](../figuras/comparacao_completa.png)','',
            f'A calibração visual usa n₀ = {n0}, a mediana medida do bitmap '
            f'T₀ = {tref:.7f} s e f₅(n₀) = n₀ + U + U/8 = {fref}. Para cada '
            'uma das oito estratégias não implementadas, a linha é '
            '$\\widehat T_j(n)=T_0 f_j(n)/f_5(n_0)$. A constante comum é '
            f'aproximadamente {c:.9g} s/unidade. Trata-se de uma convenção '
            'para sobreposição gráfica, sem validação das constantes de '
            'cada algoritmo. Comparações, hashes e bits de I/O são unidades '
            'distintas. Em particular, linhas de unária e métodos '
            'combinatórios não são tempos observados ou previsões calibradas '
            'por execuções desses métodos.','',
            'Para 7 usa-se n vezes o multinomial balanceado do domínio; para '
            '8, binomial(n,2)2^(n−2). O logaritmo é avaliado sem construir '
            'esses objetos. As expressões exatas estão na análise e no '
            'CSV teórico. A faixa combinatória exige exibir log₁₀ dos segundos '
            'modelados, pois converter números com milhões de dígitos para '
            'float estouraria.','',
            '## Limitações experimentais','',
            'Uma máquina, uma semente, cinco repetições e processos de fundo '
            'não controlados não demonstram comportamento em todos os '
            'hardwares. Afinidade, frequência e caches não foram fixados. '
            'Houve um aquecimento de entrada completa por combinação. '
            'Em n pequeno, FFI e inicialização de domínio influenciam o '
            'resultado: o bitmap não precisa ser o mais rápido em n = 1.000. '
            'O heapsort varia bastante conforme as repetições dos valores, '
            'coerente com o melhor caso linear de todas iguais. Memória e '
            'tempo foram medidos em invocações separadas; o cronômetro inclui '
            'inicialização dos auxiliares e construção da saída, mas exclui '
            'geração/cópia de entrada, oráculo, impressão e profiler.','']
    content='\n'.join(lines)
    (ROOT/'docs/resultados_locais.md').write_text(content,encoding='utf-8')
    canonical=ROOT/'docs/analise_teorica.md'
    source=canonical.read_text(encoding='utf-8')
    begin='<!-- BEGIN_RESULTADOS_LOCAIS -->'
    end='<!-- END_RESULTADOS_LOCAIS -->'
    before,tail=source.split(begin,1)
    _,after=tail.split(end,1)
    canonical.write_text(before+begin+'\n\n'+content+'\n'+end+after,encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
