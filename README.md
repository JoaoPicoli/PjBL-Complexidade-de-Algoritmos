# PjBL: deduplicação de leituras de sensores

**Par 2/5 implementado e medido localmente por autorização do usuário.**
Ambas as saídas são uint16 estritamente crescentes. A equipe adotou o par;
a aprovação do professor exigida pelo enunciado permanece sem registro.

Comece por [docs/proposta_par.md](docs/proposta_par.md): heapsort iterativo em C
para Embarca e bitmap exato em Python para Datacenter. O relatório completo
tem fonte [LaTeX](relatorios_latex/relatorio.tex) gerada da
[análise canônica](docs/analise_teorica.md). O [PDF](relatorios_latex/relatorio.pdf)
é compilado e inspecionado visualmente. O registro de qualidade
está em [docs/revisao_pdf.md](docs/revisao_pdf.md).

## Conteúdo

- `statement/` e `learning_references/`: entradas preexistentes, preservadas.
- `src/embarcada_c/`: heapsort iterativo e compactação; uint16_t e size_t.
- `src/datacenter_python/`: bitmap empacotado real, marcação em lotes com OR.
- `src/apoio/`: build, testes, demonstração/benchmarks, auditorias e documentos.
- `docs/`: proposta, análise, protocolo, ambiente, leitura e checklist.
- `formal/`: diagnóstico de Lean; sem fontes ou provas reivindicadas.
- `tests/`: nove testes, incluindo oito casos manuais e regressão de byte repetido.
- `dados/`: 190 tempos, 38 ensaios de memória, candidatos NumPy e evidências C.
- `figuras/`: observações locais, comparação com oito modelos e análise teórica.
- `relatorios_latex/`: fonte principal, preâmbulo e PDF se compilado.
- `.tools/` e `tmp/`: ferramentas locais e renderizações temporárias, ignoradas
  pelo Git. Não são cópias do projeto em outra raiz.

## Compilar, testar e reproduzir as medições

Comandos PowerShell, executados a partir desta raiz. Python 3.12.5 foi usado;
as versões exatas estão em [docs/ambiente.json](docs/ambiente.json). O script
de preparação baixa versões fixas e verifica SHA-256 dos binários Windows.
Precisa de rede para os downloads e para o primeiro pacote TeX do Tectonic.
Na sessão inicial NumPy, Matplotlib e pypdf já estavam instalados; apenas
SymPy/mpmath foram acrescentados ao diretório local. A preparação abaixo
também permite reproduzir essas dependências num ambiente novo.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File src/apoio/preparar_ferramentas.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File src/apoio/preparar_compilador.ps1
python src/apoio/compilar_c.py
python src/apoio/auditar_memoria_c.py
python src/apoio/executar_testes.py
python src/apoio/avaliar_bitmap.py
python src/apoio/benchmark.py
python src/apoio/registrar_ambiente.py
python src/apoio/analise_simbolica.py
python src/apoio/resumir_resultados.py
python src/apoio/gerar_relatorio.py --compilar
```

O `.tex` usa Cambria/Calibri/Consolas, disponíveis no Windows inspecionado.
Em outro sistema, adaptar essas fontes na geração. Para gerar somente LaTeX,
omitir `--compilar`. Para recompilar o `.tex` existente, sem Pandoc:

```powershell
$env:TECTONIC_CACHE_DIR = Join-Path (Get-Location) '.tools/tectonic-cache'
.\.tools\tectonic.exe --keep-logs --keep-intermediates relatorios_latex/relatorio.tex
```

O cache TeX foi direcionado para a raiz. O arquivo `.tex` é completo, pode ser
compilado por XeLaTeX com pacotes/fontes compatíveis. A skill de PDF foi lida;
seu marcador `container_tools/mark_artifact_operation_started.mjs` não está
instalado neste ambiente, e a tentativa retornou `MODULE_NOT_FOUND`.
Essa falha de integração é registrada; a compilação real usa LaTeX e Poppler.

Para renderizar e auditar o resultado, com Poppler no PATH:

```powershell
New-Item -ItemType Directory -Force tmp/pdfs | Out-Null
pdftoppm -r 100 -png relatorios_latex/relatorio.pdf tmp/pdfs/relatorio
python src/apoio/auditar_entrega.py
```

A inspeção visual deve acompanhar a auditoria automatizada; o script não
substitui a revisão de páginas, equações e tabela. Não editar o `.tex` gerado:
alterar `docs/analise_teorica.md` ou o preâmbulo e gerar novamente para manter
coerência entre Markdown e LaTeX. O bloco de resultados é gerado por
`resumir_resultados.py`, também em `docs/resultados_locais.md`; não editá-lo
manualmente. A reprodução de benchmarks substitui os CSVs da execução atual;
preserve-os com outro nome antes de comparar outra máquina.

## Implementação, testes e medições

A rotina de demonstração é `python src/apoio/benchmark.py`: chama o algoritmo
C compilado por ctypes e o bitmap NumPy, imprime medianas/máximos e memória
(heap, limite de pilha, estático, bitmap e pico rastreado conforme o método)
para cada tamanho e distribuição e salva cada observação. São cinco repetições após
aquecimento; n=1.000, 100.000 e 10.000.000 em ambas as estratégias. O plano
está em [docs/plano_experimental.md](docs/plano_experimental.md).

Para exibir os tempos e a memória já salvos sem repetir as medições:
`python src/apoio/benchmark.py --mostrar`.

Em iid com n=10⁷, medianas locais: **0,9910261 s em C** e **0,0979133 s no
bitmap NumPy**. O máximo do bitmap nas 30 observações de n=10⁷ foi
**0,1026721 s**. A máquina de referência da disciplina não foi disponibilizada;
o limite nela não foi verificado.

O objeto C tem **heap zero e estático auxiliar gravável zero**. GCC reporta
56 bytes de pilha; conferência das instruções, 32 bytes de home space Win64
e 16 bytes conservadores de alinhamento dão **limite de 104 bytes extras**
neste build. Não é RSS nem medição em um sensor real; outra ABI exige nova
auditoria. A instrumentação tem controle positivo e os relatórios ficam em
`dados/auditoria_c/` e `dados/memoria_c.json`.

O bitmap é efetivo: 8.192 bytes uint8, índices uint16 e máscaras uint8 em
lotes de 65.536; `numpy.bitwise_or.at` acumula corretamente índices repetidos.
Não usa set/unique/sort no algoritmo. A saída crescente é extraída dos bits.
O pico rastreado com domínio completo foi 730.080 bytes, incluindo saída
de 131.072 bytes. Temporários, limitações de tracemalloc e avaliação dos lotes
estão em [docs/resultados_locais.md](docs/resultados_locais.md).

GCC 16.2.0 está preparado localmente em `.tools/w64devkit/`; não é preciso
alterar o PATH global. Lean/Lake/elan não foram encontrados no PATH. Não há
Mathlib configurada, compilação Lean nem auditoria nativa de axiomas. O estado
detalhado está em [formal/README.md](formal/README.md). As provas matemáticas
em prosa permanecem no relatório, acompanhadas de conferências SymPy.

O procedimento SymPy recebeu atribuição a *Scientific Agent Skills*, conforme
exigido pela skill, com metadados verificados no arXiv. Nenhuma mensagem foi
enviada ao professor; nenhum arquivo foi adicionado ao índice ou commitado.
