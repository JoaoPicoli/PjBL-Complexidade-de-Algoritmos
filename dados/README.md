# Dados

`resultados_empiricos.csv` contém **190 tempos locais** do par 2/5:
38 combinações × cinco repetições, após autorização do usuário. O bitmap tem
saída crescente. Não confundir a autorização local com aprovação docente.

O esquema separa tempo, heap auxiliar, pilha estimada, estático, entrada,
saída, unidades, ambiente e método. `status=medido_local`. Campos não
medidos ficam vazios: a pilha Python não foi medida e o pico rastreado não
é um pico de heap auxiliar isolado. `medicoes_memoria.csv` tem 38 invocações
separadas referenciadas por `id_memoria`; os valores de memória nas cinco
linhas de tempo remetem ao mesmo ensaio e não são cinco medições de memória.
RSS não foi usado como prova de workspace.

`resumo_empirico.csv` tem mediana, mínimo, máximo e desvio padrão por grupo.
`avaliacao_bitmap.csv` tem 15 tempos e cinco perfis de memória, comparando
cinco variantes da mesma estratégia 5. `tracemalloc_numpy.json` verifica
que os buffers NumPy desta instalação são rastreados. `memoria_c.json` e
`auditoria_c/` guardam os relatórios de stack, disassembly, seções e comandos.
`testes_resultado.json` e `testes_execucao.txt` registram os testes.

`calculos_sympy.json` guarda identidades, valores exatos e aproximações.
`custos_teoricos.csv` tem 30 linhas de modelos (dez estratégias × três n),
unidades próprias e logaritmos aproximados. Não contém tempos observados.
