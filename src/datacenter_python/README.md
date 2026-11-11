# Datacenter: bitmap empacotado

`deduplicate_bitmap(a)` recebe ndarray contíguo unidimensional uint16 e
devolve ndarray uint16 distinto e crescente. A conversão da entrada fica
explicitamente fora do algoritmo. `build_bitmap` cria 8.192 bytes uint8,
com um bit para cada leitura possível, e marca em lotes de 65.536 elementos.

`np.bitwise_or.at` acumula as máscaras em índices repetidos; a atribuição
avançada `bitmap[indices] |= masks` poderia perder bits. A emissão usa
unpackbits little-endian e flatnonzero dos bits do domínio. Não usa set,
unique, sort ou histograma para substituir a marcação. A variante escalar
é o mesmo algoritmo bitmap e serve à comparação de vetorização.

`python src/apoio/avaliar_bitmap.py` compara cinco variantes; o driver de
ambas as estratégias é `python src/apoio/benchmark.py`. Perfis de memória
ocorrem fora dos timers e incluem a saída. O pico de 730.080 bytes com domínio
completo cobre alocações Python/NumPy rastreáveis, sem alegar medir toda a
pilha nativa ou RSS. Ver `docs/resultados_locais.md` e os CSVs de dados.
