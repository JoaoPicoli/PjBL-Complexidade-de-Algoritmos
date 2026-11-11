# Registro de execução e fechamento

Registro acumulado. **Estado atual: etapa 2**, no final deste arquivo.
A etapa 1 abaixo é histórica; suas limitações de implementação não descrevem
o estado após a autorização posterior do usuário.

## Etapa 1: análise anterior à autorização local

Data de referência: 11/11/2026, America/Sao_Paulo. Trabalho realizado na raiz
`C:/Users/PICHAU/Desktop/PjBL-Complexidade-de-Algoritmos`.

## Inspeções anteriores a edições

- Listados os diretórios de `C:/Users/PICHAU/.agents/skills/` com
  `Get-ChildItem -Directory`.
- Lidos integralmente os `SKILL.md` de SymPy, PDF e lean4-doctor, além das
  referências SymPy `core-capabilities.md`, `advanced-topics.md` e `review.md`.
- Lidos lean4-checkpoint, lean4-formalize e lean4-prove como fluxos condicionais
  a uma ferramenta disponível. Não houve atividade de formalização/prova ou
  aprendizado Lean; nenhum fluxo amplo substituiu os fluxos específicos.
- Executados `Get-Location`, `git status --short`, `rg --files --hidden`,
  `git ls-files` e `git log -5 --oneline`. Resultado inicial: branch main sem
  commits; nenhum arquivo rastreado; apenas `learning_references/` e
  `statement/` não rastreados. `git log` falhou por inexistência de commits.
- Busca `rg -n -i 'aprov|autoriz|professor'` nos textos existentes: nenhum
  registro de aprovação. O texto dos PDFs foi examinado separadamente.
- Extraídos todos os PDFs com `PdfReader(...).pages` e `page.extract_text()`;
  saída repetida em UTF-8 após falha cp1252 e dividida em blocos. Lido
  `learning_references/notion_links.txt`.
- Tentados os dois links Notion pela ferramenta web: indisponíveis. Consultado
  arXiv:2609.00065 para os metadados da atribuição exigida pela skill SymPy.
- Executados inventário `Get-Command`, `Get-CimInstance Win32_Processor`,
  `Get-CimInstance Win32_OperatingSystem`, `python --version`, versões dos
  módulos Python e `pdftoppm -v` / `pdfinfo -v`.

## Preparação e comandos efetivamente usados

Diretórios criados com `New-Item -ItemType Directory -Force`. Os seis arquivos
originais tiveram tamanho/SHA-256 registrados antes da criação documental.
Os comandos abaixo foram executados, alguns novamente após correções:

```powershell
python -m pip install --disable-pip-version-check --target .tools/python sympy==1.14.0 mpmath==1.3.0
python src/apoio/registrar_ambiente.py
python src/apoio/analise_simbolica.py
python src/apoio/gerar_relatorio.py --compilar
python src/apoio/auditar_entrega.py
python src/apoio/renderizar_pdf.py
```

As releases oficiais foram consultadas pela API GitHub e baixadas com
`Invoke-WebRequest`, seguidas de `Expand-Archive` dentro de `.tools/`:
Tectonic 0.17.0 Windows MSVC e Pandoc 3.13 Windows x86-64. Foram executados
os dois binários com `--version` e a ajuda do Tectonic. Os hashes dos ZIPs e
executáveis estão em `ambiente.json`. A instalação Python usou `--target`,
sem modificar pacotes globais; o primeiro pip usou sua configuração padrão
de cache de download. O script de reprodução inclui `--no-cache-dir`.

O gerador executa Pandoc com `--standalone --number-sections --toc`, filtro Lua
de quebras em caminhos, preâmbulo e fontes Windows. Depois executa Tectonic
com `--keep-logs --keep-intermediates`. Os argumentos completos estão no
próprio script. Cache TeX, configuração e cache de fontes ficam em `.tools/`.

Também executados:

```powershell
pdftoppm -f 2 -l 2 -scale-to 1500 -png -singlefile statement/PjBL_Complexidade_Algoritmos-1.pdf tmp/pdfs/enunciado-p2
pdftoppm -f 42 -l 42 -scale-to 1400 -png -singlefile 'learning_references/A03 - Notação Assintotica.pptx (1).pdf' tmp/pdfs/a03-p42
pdfinfo relatorios_latex/relatorio.pdf
pdftoppm -r 85 -png relatorios_latex/relatorio.pdf tmp/pdfs/relatorio
```

A revisão final usou `pdftoppm -r 100 -png`, chamado pelo script, e
`pdftotext -bbox-layout`, chamado pela auditoria. As imagens foram efetivamente
abertas para inspeção; não se inferiu qualidade visual só por extrair texto.

O diagnóstico registrou tentativas `gcc --version`, `clang --version`, `cl`,
`lean --version`, `lake --version`, `elan --version`: arquivos executáveis não
encontrados. Não foram executados `lake build` ou `#print axioms`, pois não
há ferramenta/projeto Lean utilizável. O marcador da skill PDF foi tentado
uma vez e falhou por arquivo ausente, conforme `revisao_pdf.md`.

## Evidências e limites

Conferências simbólicas exatas passaram; produzidos 30 registros de modelos
teóricos. A auditoria confirmou dez seções de estratégias, seis entradas
originais intactas, oito oráculos manuais consistentes e zero observações
empíricas. O PDF final tem 13 páginas, sem caixas excedentes nem caracteres
ausentes no log; há um aviso de espaçamento e dependência de fontes Windows.

Não há implementações, testes executados contra algoritmos, benchmarks,
prova dos 256 bytes ou dos dois segundos. Não há provas Lean, versão Lean
detectada ou auditoria de axiomas executada; não existem fontes Lean locais.
Essa ausência não é apresentada como verificação formal bem-sucedida.

Nenhuma mensagem foi enviada ao professor. Aprovação pendente do par
proposto 2/5. Se outro par for aprovado, será esse o implementado. A
atribuição solicitada pela skill SymPy foi incluída nas referências.

Arquivos criados e seus hashes estão em `manifesto_entrega.json`; ferramentas
locais e temporários não integram essa lista de entregáveis. A checagem final
do Git preserva os arquivos originais não rastreados e mantém todos os novos
arquivos sem stage/commit. Não houve arquivo rastreado editado ou removido.

A validação final de sintaxe executou `python -m py_compile` nos cinco scripts
Python e o parser nativo PowerShell em `preparar_ferramentas.ps1`, ambos com
sucesso. Isso não executou novamente instalações nem o script de preparação
completo. Executados `git diff --check`, `git status --short`, `git diff --stat`
e `git ls-files`: sem erros de diff, sem arquivos rastreados e sem mudanças
em stage. Como a branch não tem commits, `git diff` não cobre os arquivos
novos; a lista e os hashes do manifesto complementam essa verificação.

Por fim, foram executados `python -m py_compile src/apoio/manifestar_entrega.py`
e `python src/apoio/manifestar_entrega.py`. O manifesto reúne 35 arquivos
criados (incluindo a si próprio) e seis originais preservados. Uma conferência
independente com `hashlib.sha256` validou todos os hashes listados. O hash do
próprio manifesto é omitido para evitar autorreferência.

## Etapa 2: par 2/5 adotado e execução local autorizada

O usuário informou que não pode consultar o professor e autorizou a
continuidade local. O par passou a decisão técnica da equipe: heapsort C
in-place e bitmap empacotado Python/NumPy, **ambos com saída crescente**.
A aprovação docente permanece sem registro; a autorização do usuário não foi
apresentada como aprovação do professor. Nenhuma mensagem externa foi enviada.

As skills SymPy, PDF, lean4-doctor e lean4-checkpoint foram relidas antes
da análise desta etapa, e o inventário de `.agents/skills` foi repetido.
Os materiais de entrada não mudaram; os seis hashes continuam iguais.
O manifesto da etapa 1 foi preservado em `historico/manifesto_etapa1.json`.

### Compilador e implementação

Consultada a release oficial w64devkit v2.11.0 pela API GitHub; o arquivo
`w64devkit-x64-2.11.0.7z.exe` foi baixado para `.tools/` e teve SHA-256
54c2bb9962e8a30c8270e34c5efc3d5fee579f53087fa7d435b95fbba2af7b2b.
Uma tentativa inicial de combinar download e execução do extrator foi
bloqueada pela política automática da ferramenta. A alternativa concluída
foi listar e extrair o arquivo com `tar -tf` e `tar -xf`, sem executar o
stub SFX baixado. O script de reprodução verifica hash e nomes dos membros.

Executados `gcc.exe --version` e `gcc.exe -dumpmachine` do pacote local:
GCC 16.2.0, x86_64-w64-mingw32. Não foi alterado o PATH global. Os comandos
de build completos, retornos e flags estão em `dados/auditoria_c/commands.json`.

Criados o algoritmo C (uma função folha, uint16_t/size_t), cabeçalho e aparato
de auditoria em `src/embarcada_c/`; bitmap real em `src/datacenter_python/`;
drivers, build e verificações em `src/apoio/`; testes em `tests/`. Não foram
implementadas as outras oito estratégias. Set/unique aparecem apenas nos
oráculos de validação, fora dos algoritmos e das regiões cronometradas.

### Comandos executados e resultados

```powershell
python src/apoio/compilar_c.py
python src/apoio/auditar_memoria_c.py
python -m unittest discover -s tests -p 'test_*.py' -v
python src/apoio/executar_testes.py
python src/apoio/avaliar_bitmap.py
python src/apoio/benchmark.py
python src/apoio/registrar_ambiente.py
python src/apoio/analise_simbolica.py
python src/apoio/resumir_resultados.py
python src/apoio/gerar_relatorio.py --compilar
python src/apoio/auditar_entrega.py
python src/apoio/renderizar_pdf.py
```

Os nove testes passaram. Incluem oito casos manuais, 364 sequências
exaustivas, 40 aleatórias, guardas de memória do vetor C, ponteiro nulo/vazio,
domínio completo embaralhado/repetido, contrato de tipos, bits no mesmo byte
e controle positivo de instrumentação (solicitação de 17 bytes detectada
em DLL separada). A primeira captura de unittest pelo PowerShell formatou
stderr como NativeCommandError apesar de saída 0 e testes aprovados; o runner
Python grava agora log UTF-8 limpo e resultado JSON. Os testes foram repetidos
após ajuste da resolução de dependências locais, sem refazer os benchmarks.

O build normal e o instrumentado têm desmontagem idêntica no algoritmo:
seis pushes, sem chamadas, sem sub/add de rsp, sem símbolos externos, .data
e .bss iguais a zero. GCC reporta frame de 56 bytes; 32 bytes de home space
e 16 de reserva conservadora de alinhamento totalizam 104 bytes. Todos os
ensaios registraram zero chamadas e bytes de alocação. Isso evidencia o
orçamento neste build local, sem alegar medir dinamicamente a pilha de outro
sensor, o runtime inteiro ou interrupções.

A avaliação escalar/lotes registrou 15 tempos e cinco perfis separados.
Selecionado lote de 65.536: mediana de 0,0984213 s em iid de 10⁷ e pico
rastreado 730.080 bytes incluindo saída, contra 30.079.664 bytes do lote
integral. O probe NumPy confirma buffers rastreados; tracemalloc continua
sem medir toda a pilha e alocação nativa interna.

A série principal registrou **190 tempos** (38 combinações × cinco),
**38 perfis de memória separados**, seis distribuições nos três n e um caso
sem duplicatas adicional apenas em n=1.000. Todas as saídas medidas foram
validadas. Em iid de 10⁷, medianas C/bitmap: 0,9910261 / 0,0979133 s. O maior
tempo do bitmap em todas as 30 observações de 10⁷ foi 0,1026721 s.
São evidências locais no Ryzen 5 5600 / Windows 11; a máquina de referência
da disciplina não foi testada. Tempos brutos, unidades, distribuição/semente,
hashes, ambiente e método constam nos CSVs e no JSON de método.

O SymPy reconferiu as identidades e os payloads/limite conservador em bytes.
Os gráficos foram atualizados: observações com barras mínimo/máximo, duas
séries medidas mais oito modelos tracejados com calibração explícita, e
figura puramente teórica preservada com rótulo próprio. Proposta, plano,
READMEs, checklist, Markdown e LaTeX foram atualizados. O bloco numérico do
relatório é gerado dos CSVs para evitar divergência entre os documentos.

### Verificação documental e limites externos

O marcador da skill PDF foi tentado com `--operation-kind edit` e continuou
ausente (MODULE_NOT_FOUND). Não se simulou sucesso. A compilação real usou
Tectonic 0.17.0; foram corrigidos um acento em subscrito matemático, um trecho
longo e a impressão UTF-8 do log. Resultado: **17 páginas**, zero Overfull
ou Missing character e um Underfull de espaçamento sem corte visual. As 17
páginas foram renderizadas e inspecionadas em cinco folhas de contato. As
8.627 palavras extraídas estão dentro dos limites físicos das páginas.

A auditoria de entrega confirmou hashes, 190 linhas empíricas, 38 perfis,
as três escalas e cinco repetições por grupo, hashes iguais de entrada entre
as duas estratégias e correspondência entre fontes/DLL e os dados. Foram
executados py_compile nos scripts criados/editados, o parser nativo no script
PowerShell de preparação do compilador, `git diff --check` e `git status`.

Lean/Lake/elan continuam ausentes no PATH, sem projeto Mathlib configurado.
Não foram criadas fontes Lean, compiladas provas ou executado #print axioms;
não se reivindica auditoria formal concluída nem prova de ausência transitiva
de axiomas. O diagnóstico é mantido em `formal/README.md`.

Pendências externas: aprovação do professor, prazo na referência da disciplina
e orçamento no compilador/ABI do sensor real. A continuidade local autorizada
foi concluída sem solicitar novamente permissão. As listas de arquivos e
diferenças desde a etapa 1 estão no manifesto atualizado. Nenhum arquivo de
entrada foi alterado, nenhum arquivo foi adicionado ao índice e nenhum commit
foi criado.

A exibição do driver foi completada para imprimir também os valores de
memória e seus escopos, além do tempo. Executado
`python src/apoio/benchmark.py --mostrar`, que lê as observações já salvas
sem medi-las outra vez. O ajuste de impressão ocorre fora do timer e não
altera as implementações ou os tempos registrados. A sintaxe do driver foi
validada novamente com py_compile.
