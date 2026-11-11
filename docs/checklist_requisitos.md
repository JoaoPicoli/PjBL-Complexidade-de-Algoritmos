# Conferência dos requisitos

Estado: par 2/5 implementado por autorização local do usuário; aprovação
docente ainda sem registro. Evidências locais e pendências externas são distintas.

| Requisito | Estado e evidência |
|---|---|
| Inventário de skills antes da análise | Feito: diretórios de `.agents/skills` listados; SymPy, PDF e doctor lidos antes da análise; checkpoint/formalize/prove lidos como condicionais |
| Git inicial e preservação | Sem commits; somente entradas não rastreadas; hashes em `entradas_sha256.json` |
| Ler enunciado e todos os PDFs locais | 183 páginas lidas; registro em `leitura_materiais.md` |
| Ler notion_links.txt | Feito; consultas aos dois URLs falharam; conteúdos externos indisponíveis |
| Ferramentas e versões | `ambiente.json`, incluindo ausências e ferramentas portáteis locais |
| Estrutura de diretórios | Criada dentro da raiz; código C/Python nos diretórios correspondentes |
| Registro de aprovação existente | Não localizado entre os arquivos originais; nenhum contato externo efetuado |
| Proposta antes de programar | Preparada na etapa 1; par 2/5 adotado e implementação local autorizada na etapa 2; aprovação docente pendente |
| Análise de dez estratégias | `analise_teorica.md` e LaTeX gerado; variantes operacionais explícitas |
| Melhor/médio/pior e hipóteses | Apresentados por estratégia; hipótese de distintos limitada a n ≤ U |
| Heap/pilha/entrada/saída/disco separados | Apresentados por variante, com payload e overhead distintos |
| Corretude e determinismo | Invariantes, término e erros probabilísticos descritos; bogosort sem prazo máximo |
| Contagem força bruta | Soma triangular demonstrada e conferida por SymPy |
| Heapsort/quicksort/mergesort | Casos, recorrências e pilha/heap diferenciados |
| Hash esperado e pior | Hipóteses de carga/hash e refinamento pelo domínio explícitos |
| Bitmap 8.192 bytes versus 256 | Dedução exata, fator 32 |
| Bloom 1% e taxa empírica | Modelo aproximado separado da garantia particionada 1/128; denominador definido |
| Bogosort para os três n | Multinomial de multiplicidades válidas; logs aproximados no relatório/CSV |
| Power set e percurso de elementos | Materializado e sob demanda; n2^(n-1) elementos e binomial(n,2)2^(n-2) pares |
| Unária, espaço e I/O | Representação 1^x0, algoritmo completo, U passagens, crescimento linear em n com U fixo |
| Matriz para n=10^7 | Bits e bytes: 12,5 TB / 100 TB decimais |
| SymPy reprodutível e expressões exatas | Script em `src/apoio`, JSON e CSV teórico; aproximações identificadas |
| Formalização Lean | Não iniciada por ausência da ferramenta no PATH; diagnóstico em `formal/README.md` |
| Build e auditoria Lean | Não executados; nenhuma declaração reivindicada; não há alegação de prova formal |
| Só duas estratégias implementadas | Estratégia 2 em C e 5 em Python/NumPy; escalar/vetorizada são variantes de 5 |
| Saída crescente nas duas | Contrato e testes atualizados; 190 saídas medidas conferidas por oráculo |
| Embarca, heap/pilha/estático ≤256 bytes | Build local: limite conservador 104 bytes (56+32+16), heap/estático zero; contador positivo testado; outra ABI/sensor pendente |
| Datacenter, bitmap e prazo <2 s | 30 observações locais de n=10⁷ abaixo de 2 s; máximo 0,1026721 s; referência da disciplina não verificada |
| Bitmap efetivo e índices repetidos | 8.192 bytes de bitmap; bitwise_or.at; regressão dos bits no mesmo byte |
| Temporários NumPy | 38 ensaios de memória e avaliação de cinco variantes; tracemalloc inclui saída, não equivale a toda memória nativa |
| Testes pequenos e bordas | Nove testes passaram, incluindo oito oráculos, 364 sequências exaustivas, 40 aleatórias, fronteiras/guardas |
| Três tamanhos em ambas as estratégias | 1.000, 100.000 e 10.000.000; seis distribuições e sem duplicatas somente em n=1.000 |
| CSV de tempo/memória/ambiente/unidades | 190 tempos e 38 perfis separados, referenciados por id_memoria, com versões e hashes |
| Gráfico duas medições + oito curvas | comparacao_completa.png; pontos sólidos e oito modelos tracejados, calibração explícita |
| Relatório .tex coerente | Gerado diretamente da análise canônica, sem versão matemática divergente |
| Compilação e revisão visual PDF | Ver registro de execução e `revisao_pdf.md`; falhas não são declaradas sucesso |
| README com reprodução | Build C, testes, avaliação de lotes, benchmarks, gráficos e relatório documentados |
| Arquivos originais intactos | Auditoria SHA-256 reproduzível em `auditar_entrega.py` |
| Git final e arquivos/comandos criados | Ver `registro_execucao.md` e `manifesto_entrega.json` |

A autorização local do usuário foi atendida. Pendências externas: aprovação
do professor; prazo na máquina de referência; orçamento no compilador/ABI do
sensor real. Lean/Lake seguem indisponíveis no diagnóstico; nenhum build ou
auditoria de axiomas foi alegado.
