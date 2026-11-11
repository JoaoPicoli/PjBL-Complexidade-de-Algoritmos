# Embarca: heapsort e compactação

`dedup_heapsort_u16(uint16_t *a, size_t n)` altera o vetor residente e retorna
o tamanho d do prefixo distinto crescente. n=0 permite a=NULL. Não há
recursão, alocação ou dados estáticos no algoritmo. size_t é de 64 bits no
alvo local e há uma asserção de capacidade para índices até 10⁷.

Build: `python src/apoio/compilar_c.py`. A DLL gerada em `.tools/` é usada
pelo driver de demonstração. `alloc_audit.c`, `alloc_hooks.h` e
`audit_fixture.c` são aparato de instrumentação; o fixture não entra na DLL
do algoritmo. Contam/refusam alocações se o algoritmo tentar usá-las.

`python src/apoio/auditar_memoria_c.py` cruza o .su, a desmontagem, símbolos
externos e seções do objeto. O limite conservador local é 104 bytes,
incluindo overhead de chamada Win64. Ver `dados/memoria_c.json`; não há
comprovação em outro sensor/ABI. A autorização local não constitui aprovação docente.
