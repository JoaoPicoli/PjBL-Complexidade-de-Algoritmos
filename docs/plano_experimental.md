# Protocolo experimental do par 2/5 autorizado localmente

O usuário adotou o par 2/5 e autorizou a implementação local em 11/11/2026,
sem aprovação docente disponível. Essa pendência acadêmica continua
registrada em `proposta_par.md`. O protocolo abaixo foi executado: 19 entradas,
38 combinações entrada/estratégia, 190 tempos e 38 ensaios separados de memória.

1. Registrar a autorização local e distinguir aprovação docente. Ambiente:
   Ryzen 5 5600, Windows 11 Pro x64, Python 3.12.5, NumPy 2.1.2, GCC 16.2.0
   portátil. Não é uma referência da disciplina identificada. Fontes, DLL,
   entradas e compilador são identificados por versões/hashes.
2. Usar n = 1.000, 100.000 e 10.000.000 em ambas as estratégias, com entrada
   compacta uint16. Distribuições: iid uniforme (semente 20261111), todas
   iguais, alternância 0/65535 e ciclo do domínio. Sem duplicatas: somente
   n ≤ 65.536; usar testes pequenos e n=1.000. Acrescentar entrada ordenada e
   reversa geradas antes do cronômetro.
3. Preservar cópia original para validar fora da medição. Para heapsort,
   recriar a cópia de trabalho antes de cada repetição, pois modifica A.
   Geração, cópia, leitura do disco, oráculo e impressão ficam fora do timer.
4. Medir a função inteira: inicialização de auxiliares, deduplicação e saída
   (compactação na Embarca; saída compacta no Datacenter). Cronômetro
   monotônico de alta resolução, cinco repetições válidas após aquecimento.
   Não descartar resultados lentos sem justificativa; registrar todas as
   linhas, resumir mediana, mínimo, máximo e dispersão.
5. Validar conjunto, ausência de duplicatas e saída **estritamente crescente
   nas duas versões** depois de cada execução. O oráculo `numpy.unique`
   fica exclusivamente no driver de validação, fora do algoritmo e do timer.
6. Em C, auditar funções chamadas e instrumentar alocações atribuíveis ao
   algoritmo, contando chamadas e bytes ativos/pico. Geração/saída externa
   devem ter contadores separados. Guardar os relatórios `-fstack-usage`
   quando disponíveis e a cadeia de chamadas; somar frames simultâneos,
   alinhamento, retornos e registradores salvos. Recursão e buffers ocultos
   precisam ser excluídos por inspeção ou caracterizados. Somar heap + pilha
   + eventual armazenamento estático auxiliar para o orçamento de 256 bytes.
   Não usar RSS como evidência. Repetir nas três escalas; descrever que stack
   estático é estimativa do compilador e qual ABI/alvo ela cobre.
7. Em Python, declarar payload, overhead do ndarray do bitmap e saída. Avaliar
   temporários com instrumento apropriado em execução separada. Não igualar
   `sys.getsizeof` superficial ao pico transitivo e não cronometrar o profiler
   como se fosse a versão normal. RSS pode complementar, com unidade e escopo.
8. Comparar a marcação escalar e a vetorizada em lotes. Acumular máscaras
   com `numpy.bitwise_or.at`, nunca com indexação avançada em modo buffered.
   Escolhido lote de 65.536; payload dos dois buffers 196.608 bytes. A
   emissão varre o bitmap e gera uint16 crescente. Se outra execução de
   10⁷ exceder 2 s, otimizar a mesma estratégia e repetir sem ocultar o
   resultado anterior. Não substituir bitmap por set, unique ou histograma.
9. Guardar CSV empírico com tamanho, estratégia, distribuição/semente,
   repetição, segundos, memória em bytes por categoria, método, ambiente,
   compilador/flags e estado. Identificar contadores medidos versus estimados.
10. Produzir gráfico com pontos medidos das duas e oito curvas teóricas
    tracejadas. Anotar a calibração em segundos, as distribuições/hipóteses
    e o caráter ilustrativo de constantes compartilhadas. Sem referência de
    tempo medida, manter as curvas em unidades de trabalho. O gráfico
    `comparacao_completa.png` usa a mediana local do bitmap em n=100.000
    como referência visual comum. `tempos_medidos.png` mostra só observações
    iid, e `modelos_teoricos.png` continua sem tempos observados.

Comandos executados: `python src/apoio/compilar_c.py`,
`python src/apoio/auditar_memoria_c.py`, `python src/apoio/executar_testes.py`,
`python src/apoio/avaliar_bitmap.py`, `python src/apoio/benchmark.py` e
`python src/apoio/resumir_resultados.py`. A avaliação de candidatos tem três
repetições por variante; a série principal tem cinco. Tempo e tracemalloc
são invocações separadas. A entrada/copias/oráculos ficam fora do timer;
os auxiliares e a saída ficam dentro. Python/ctypes entra no tempo do C,
mas os objetos do driver ficam fora do orçamento de workspace do algoritmo.

Todas as 30 observações locais do bitmap em n=10⁷ ficaram abaixo de 2 s.
O limite de workspace C foi auditado em 104 bytes neste build (estimativa
estática conservadora), com heap e estático auxiliar iguais a zero. Repetir
em outro compilador/ABI e na máquina de referência da disciplina antes de
transferir essas conclusões para esses alvos. Afinidade/frequência/caches e
processos de fundo não foram controlados.
